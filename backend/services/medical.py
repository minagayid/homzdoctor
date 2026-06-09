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
        # Step 1: Preprocess image
        imaging_result = await self.imaging_agent.process({
            "task_type": "Imaging",
            "image_path": image_data.get("path"),
            "image_type": image_data.get("type"),
        })
        
        # Step 2: Run diagnostic analysis
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
        """Get a patient's medical history."""
        # Implementation placeholder
        return []


class PharmacyService:
    """Service for pharmacy-related operations."""
    
    def __init__(self):
        self.pharmacy_agent = PharmacyAgent()
    
    async def find_nearby_pharmacies(self, lat: float, lon: float, radius_km: int = 5) -> List[Dict[str, Any]]:
        """Find pharmacies near a location."""
        return await self.pharmacy_agent.process({
            "task_type": "Pharmacy",
            "action": "search",
            "latitude": lat,
            "longitude": lon,
            "radius_km": radius_km,
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
    
    async def place_order(self, pharmacy_id: int, prescription: Dict[str, Any]) -> Dict[str, Any]:
        """Place a medication order (after patient confirmation)."""
        # Verify patient confirmation
        if not prescription.get("patient_confirmed"):
            return {"error": "Patient confirmation required", "order_placed": False}
        
        return await self.pharmacy_agent.process({
            "task_type": "Pharmacy",
            "action": "order",
            "pharmacy_id": pharmacy_id,
            "prescription": prescription,
        })


class AdherenceService:
    """Service for medication adherence monitoring."""
    
    def __init__(self):
        pass
    
    async def log_medication_taken(self, schedule_id: int, taken_at: Optional[datetime] = None) -> Dict[str, Any]:
        """Log that a medication was taken."""
        # Implementation placeholder
        return {"status": "logged", "schedule_id": schedule_id}
    
    async def calculate_adherence_score(self, patient_id: int) -> float:
        """Calculate a patient's medication adherence score (0-100)."""
        # Implementation placeholder
        return 0.0
    
    async def schedule_reminders(self, prescription_id: int, medication_times: List[str]) -> List[Dict[str, Any]]:
        """Schedule medication reminders."""
        # Implementation placeholder
        return []


class EscalationService:
    """Service for handling critical situation escalations."""
    
    def __init__(self):
        self.escalation_agent = EscalationAgent()
    
    async def check_escalation_triggers(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if patient data triggers escalation."""
        return await self.escalation_agent.process(patient_data)
    
    async def alert_doctor(self, doctor_id: int, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send alert to a doctor."""
        # Implementation placeholder
        return {"alert_sent": True, "doctor_id": doctor_id}


class PatientAssistantService:
    """Service for patient assistant interactions."""
    
    def __init__(self):
        self.assistant = PatientAssistantAgent()
    
    async def answer_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Answer a patient's question."""
        return await self.assistant.process({
            "task_type": "PatientAssistant",
            "query": query,
            "context": context or {},
        })
    
    async def explain_report(self, report: Dict[str, Any]) -> str:
        """Provide a patient-friendly explanation of a medical report."""
        return await self.assistant.explain_report(report)
