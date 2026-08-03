"""
Services layer for HomzDoctor.
Encapsulates business logic and interacts with agents.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from agents.core import (
    OrchestratorAgent,
    ImagingAgent,
    DiagnosticAgent,
    DrugKnowledgeAgent,
    PharmacyAgent,
    AppointmentAgent,
    PatientAssistantAgent,
    EscalationAgent,
)
from agents.lvlm_agent import LVLMDiagnosticAgent
from agents.pharmacy_agent import LLMPharmacyAgent
from agents.llm_agent import LLMPatientAssistantAgent

from services.hf_llm_service import get_hf_llm_service



class MedicalService:
    """Service for medical records and AI analysis."""
    
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.imaging_agent = ImagingAgent()
        self.diagnostic_agent = DiagnosticAgent()
        
        # Register agents with orchestrator
        self.orchestrator.register_agent(self.imaging_agent)
        self.orchestrator.register_agent(self.diagnostic_agent)
    
    async def process_medical_image(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and analyze a medical image."""
        # Step 1: request the configured imaging capability.
        imaging_result = await self.imaging_agent.process({
            "task_type": "Imaging",
            "image_path": image_data.get("path"),
            "image_type": image_data.get("type"),
        })
        
        # Step 2: pass structured findings to the diagnostic safety layer.
        diagnostic_result = await self.diagnostic_agent.process({
            "task_type": "Diagnostic",
            "findings": imaging_result.get("findings"),
        })
        
        return {
            "imaging": imaging_result,
            "diagnostic": diagnostic_result,
            "doctor_review_required": True,
        }
    
    async def get_patient_history(self, patient_id: int) -> List[Dict[str, Any]]:
        """Return history records for legacy callers.

        Database-backed history is exposed by the authenticated API route;
        this compatibility method deliberately returns no data rather than
        pretending that a lookup succeeded.
        """
        return []


class LVLMDiagnosticService:
    """Service wrapping the Large Vision-Language Model diagnostic agent.

    Reads X-ray / CT / MRI images and lab PDFs, runs the three-pass
    (diagnose -> recheck -> finalise) pipeline, and always returns a result
    flagged for mandatory doctor review.
    """

    def __init__(self):
        self.agent = LVLMDiagnosticAgent()

    @property
    def available(self) -> bool:
        return self.agent.available()

    async def analyze_file(
        self,
        file_bytes: bytes,
        filename: str,
        modality: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run the LVLM pipeline on an uploaded image/PDF."""
        return await self.agent.process(
            {
                "file_bytes": file_bytes,
                "filename": filename,
                "modality": modality,
            }
        )

    async def analyze_path(self, file_path: str, modality: Optional[str] = None) -> Dict[str, Any]:
        """Run the LVLM pipeline on a file already stored on disk."""
        return await self.agent.process({"file_path": file_path, "modality": modality})


class PharmacyService:
    """Service for pharmacy-related operations (LLM-coordinated)."""

    def __init__(self):
        # This agent reports an explicit unavailable state until an inventory
        # provider is configured.
        self.pharmacy_agent = PharmacyAgent()
        # The new LLM agent handles real distance ranking + ordering.
        self.llm_agent = LLMPharmacyAgent()

    async def find_nearby_pharmacies(
        self,
        lat: Optional[float],
        lon: Optional[float],
        radius_km: int = 5,
        pharmacies: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Find pharmacies near a location, ranked by distance.

        ``pharmacies`` is the candidate list from the DB; the agent ranks it by
        real distance (or, if GOOGLE_MAPS_API_KEY is set and no list is given,
        queries Google Places live).
        """
        return await self.llm_agent.process({
            "action": "search",
            "latitude": lat,
            "longitude": lon,
            "radius_km": radius_km,
            "pharmacies": pharmacies or [],
        })

    async def check_medication_availability(self, pharmacy_id: int, drug_name: str) -> bool:
        """Check if a medication is available at a pharmacy."""
        result = await self.pharmacy_agent.process({
            "task_type": "Pharmacy",
            "action": "check_inventory",
            "pharmacy_id": pharmacy_id,
            "drug_name": drug_name,
        })
        return result.get("available", False)

    async def place_order(
        self,
        pharmacy: Dict[str, Any],
        prescription: Dict[str, Any],
        patient_confirmed: bool = False,
        order_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Drive the ordering procedure (guardrails enforced inside the agent)."""
        return await self.llm_agent.process({
            "action": "order",
            "pharmacy": pharmacy,
            "prescription": prescription,
            "patient_confirmed": patient_confirmed,
            "order_id": order_id,
        })


class AdherenceService:
    """Compatibility service for adherence integrations.

    Persisted adherence is implemented by the authenticated API routes. These
    methods remain for older callers and never claim that an action succeeded.
    """
    
    async def log_medication_taken(self, schedule_id: int, taken_at: Optional[datetime] = None) -> Dict[str, Any]:
        """Explain that callers must use the persisted API route."""
        return {
            "status": "not_persisted",
            "logged": False,
            "schedule_id": schedule_id,
            "taken_at": taken_at.isoformat() if taken_at else None,
        }
    
    async def calculate_adherence_score(self, patient_id: int) -> float:
        """Return the neutral score used by legacy callers without records."""
        return 0.0
    
    async def schedule_reminders(self, prescription_id: int, medication_times: List[str]) -> List[Dict[str, Any]]:
        """Return no reminders until a notification provider is configured."""
        return []


class EscalationService:
    """Service for handling critical situation escalations."""
    
    def __init__(self):
        self.escalation_agent = EscalationAgent()
    
    async def check_escalation_triggers(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if patient data triggers escalation."""
        return await self.escalation_agent.process(patient_data)
    
    async def alert_doctor(self, doctor_id: int, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Report an unavailable notification channel without false success."""
        return {
            "alert_sent": False,
            "status": "not_configured",
            "doctor_id": doctor_id,
            "alert_data": alert_data,
        }


class PatientAssistantService:
    """Service for patient assistant interactions (real LLM-backed + RAG)."""

    def __init__(self):
        # The real HF LLM-backed agent (falls back to canned answers if the
        # model backend is unavailable — see LLMPatientAssistantAgent).
        self.assistant = LLMPatientAssistantAgent()
        # Vector store powers retrieval-augmented answers. Optional: if Qdrant
        # or embeddings aren't configured, retrieval returns [] and the agent
        # answers without grounded context.
        from services.vector_store import get_vector_store

        self.vector_store = get_vector_store()

    async def answer_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Answer a patient's question via the LLM assistant, grounded with RAG."""
        context = dict(context or {})
        sources: List[Dict[str, Any]] = []

        # Retrieve grounding snippets (curated KB + this patient's records).
        try:
            hits = await self.vector_store.search(
                query,
                top_k=4,
                patient_id=context.get("patient_id"),
            )
        except Exception:
            hits = []
        if hits:
            context["retrieved_knowledge"] = [
                {"title": h.get("title") or h.get("source"), "text": h.get("text", "")}
                for h in hits
            ]
            sources = [
                {"title": h.get("title") or h.get("source", "reference"), "score": h.get("score")}
                for h in hits
            ]

        data = {"query": query, "context": context}
        try:
            result = await self.assistant.process(data)
        except Exception:
            return {
                "response": "Sorry, the assistant is temporarily unavailable. Please try again.",
                "sources": [],
                "confidence": 0.0,
            }
        # Surface retrieval sources to the client even if the agent didn't set them.
        if sources and not result.get("sources"):
            result["sources"] = sources
        return result

    async def explain_report(self, report: Dict[str, Any]) -> str:
        """Provide a patient-friendly explanation of a medical report."""
        try:
            return await self.assistant.explain_report(report)
        except Exception:
            return "I can give a simplified overview, but only your clinician can explain your exact results."
