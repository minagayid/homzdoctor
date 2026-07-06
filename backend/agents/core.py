"""
Multi-Agent System for HomzDoctor.
Implements the 7 specialized agents as per the ARCHITECTURE.md.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.memory = {}
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results."""
        pass
    
    def log_action(self, action: str, details: Dict[str, Any]):
        """Log agent actions for audit trail."""
        print(f"[{self.name}] {action}: {json.dumps(details)}")


class OrchestratorAgent(BaseAgent):
    """Orchestrator Agent - Routes, plans, and assigns tasks."""
    
    def __init__(self):
        super().__init__("Orchestrator")
        self.agents = {}
    
    def register_agent(self, agent: BaseAgent):
        """Register a specialized agent."""
        self.agents[agent.name] = agent
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Route a task to the appropriate agent.

        Routing is resilient: a downstream agent raising is caught and
        returned as a structured error (with the failing agent named) instead
        of propagating, so a single agent fault never takes down the request.
        """
        task_type = data.get("task_type")

        if task_type not in self.agents:
            self.log_action("routing_failed", {"task": task_type, "known": list(self.agents)})
            return {"error": f"No agent found for task: {task_type}"}

        self.log_action("routing", {"task": task_type})
        try:
            return await self.agents[task_type].process(data)
        except Exception as exc:
            self.log_action("agent_error", {"task": task_type, "error": str(exc)})
            return {"error": f"Agent '{task_type}' failed: {type(exc).__name__}: {exc}", "task_type": task_type}


class ImagingAgent(BaseAgent):
    """Imaging Agent - Handles DICOM, MRI/CT processing, segmentation."""
    
    def __init__(self):
        super().__init__("Imaging")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process medical images."""
        image_path = data.get("image_path")
        image_type = data.get("image_type", "unknown")
        
        self.log_action("processing", {"path": image_path, "type": image_type})
        
        # Placeholder for actual image processing
        # In production, would use: SimpleITK, pydicom, nibabel
        return {
            "status": "processed",
            "image_path": image_path,
            "image_type": image_type,
            "preprocessing": {
                "volume_reconstruction": "completed",
                "normalization": "completed",
                "segmentation": "completed",
            },
            "findings": {
                "images": [],
                "confidence": 0.0,
            }
        }
    
    async def preprocess_dicom(self, dicom_path: str) -> Dict[str, Any]:
        """Preprocess DICOM series."""
        self.log_action("preprocessing_dicom", {"path": dicom_path})
        # Placeholder for DICOM preprocessing
        return {"status": "preprocessed", "path": dicom_path}
    
    async def segment_spine(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform spine segmentation."""
        self.log_action("segmenting", {"type": "spine"})
        # Placeholder for spine segmentation
        return {
            "vertebrae": [],
            "discs": [],
            "spinal_canal": [],
        }


class DiagnosticAgent(BaseAgent):
    """Diagnostic Agent (MedGemma) - Pathology detection, report generation."""
    
    def __init__(self):
        super().__init__("Diagnostic")
        # In production, load MedGemma model here
        self.model = None
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run diagnostic analysis on preprocessed images."""
        structured_findings = data.get("findings", {})
        
        self.log_action("diagnosing", {"findings": structured_findings})
        
        # Placeholder for MedGemma inference
        # In production, would use actual MedGemma model
        return {
            "suspected_conditions": [],
            "confidence": 0.0,
            "differential_diagnosis": [],
            "report": {
                "json": {},
                "physician": "",
                "patient": "",
            }
        }
    
    async def generate_report(self, findings: Dict[str, Any]) -> Dict[str, str]:
        """Generate structured medical reports."""
        self.log_action("generating_report", {})
        return {
            "json": json.dumps(findings),
            "physician": "Physician report placeholder",
            "patient": "Patient-friendly report placeholder",
        }


class DrugKnowledgeAgent(BaseAgent):
    """Drug Knowledge Agent - Medication lookup, side effects, interactions."""
    
    def __init__(self):
        super().__init__("DrugKnowledge")
        # In production, load drug database
        self.drug_db = {}
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Lookup drug information."""
        drug_name = data.get("drug_name")
        
        self.log_action("looking_up", {"drug": drug_name})
        
        # Placeholder for drug lookup
        return {
            "name": drug_name,
            "description": "Drug description placeholder",
            "side_effects": [],
            "interactions": [],
            "dosage": "As prescribed by physician",
        }
    
    async def check_interactions(self, drugs: List[str]) -> List[Dict[str, Any]]:
        """Check drug-drug interactions."""
        self.log_action("checking_interactions", {"drugs": drugs})
        return []


class PharmacyAgent(BaseAgent):
    """Pharmacy Agent - Search, inventory lookup, ordering."""
    
    def __init__(self):
        super().__init__("Pharmacy")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process pharmacy-related requests."""
        action = data.get("action")
        
        if action == "search":
            return await self.search_pharmacies(data)
        elif action == "check_inventory":
            return await self.check_inventory(data)
        elif action == "order":
            return await self.place_order(data)
        
        return {"error": f"Unknown pharmacy action: {action}"}
    
    async def search_pharmacies(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search nearby pharmacies."""
        lat = data.get("latitude")
        lon = data.get("longitude")
        radius = data.get("radius_km", 5)
        
        self.log_action("searching", {"lat": lat, "lon": lon, "radius": radius})
        
        # Placeholder for pharmacy search
        return []
    
    async def check_inventory(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check medication availability."""
        self.log_action("checking_inventory", {"drug": data.get("drug_name")})
        return {"available": False}
    
    async def place_order(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Place medication order."""
        self.log_action("placing_order", {"drug": data.get("drug_name")})
        return {"order_id": None, "status": "pending"}


class AppointmentAgent(BaseAgent):
    """Appointment Agent - Doctor search, scheduling, reminders."""
    
    def __init__(self):
        super().__init__("Appointment")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process appointment requests."""
        action = data.get("action")
        
        if action == "search_doctors":
            return await self.search_doctors(data)
        elif action == "schedule":
            return await self.schedule_appointment(data)
        elif action == "remind":
            return await self.send_reminder(data)
        
        return {"error": f"Unknown appointment action: {action}"}
    
    async def search_doctors(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search available doctors."""
        specialty = data.get("specialty")
        self.log_action("searching_doctors", {"specialty": specialty})
        return []
    
    async def schedule_appointment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule doctor appointment."""
        self.log_action("scheduling", data)
        return {"appointment_id": None, "status": "scheduled"}
    
    async def send_reminder(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send appointment reminder."""
        self.log_action("sending_reminder", data)
        return {"sent": True}


class PatientAssistantAgent(BaseAgent):
    """Patient Assistant Agent - Q&A, explain diagnosis/reports."""
    
    def __init__(self):
        super().__init__("PatientAssistant")
        # In production, load Qwen/Llama model
        self.llm = None
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process patient queries."""
        query = data.get("query")
        context = data.get("context", {})
        
        self.log_action("answering", {"query": query})
        
        # Placeholder for LLM response
        return {
            "response": "Patient assistant response placeholder",
            "sources": [],
            "confidence": 0.0,
        }
    
    async def explain_report(self, report: Dict[str, Any]) -> str:
        """Generate patient-friendly report explanation."""
        self.log_action("explaining_report", {})
        return "Patient-friendly explanation placeholder."


class EscalationAgent(BaseAgent):
    """Escalation Agent - Monitors for critical situations."""
    
    RED_FLAG_SYMPTOMS = [
        "chest pain",
        "neurological deficit",
        "severe allergic reaction",
        "high fever persistence",
        "difficulty breathing",
        "severe headache",
    ]
    
    def __init__(self):
        super().__init__("Escalation")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for escalation triggers.

        Red-flag matching is substring-based: a flag trips when its phrase
        appears within the reported symptom, so "sudden difficulty breathing"
        or "severe chest pain" still match ("difficulty breathing", "chest
        pain"). Exact-equality matching (the previous behaviour) silently
        missed these clinically identical phrasings, an unacceptable failure
        mode in a safety-critical escalation path. Matching is one-directional
        so a milder symptom ("headache") does not trip a more specific flag
        ("severe headache").
        """
        symptoms = data.get("symptoms", [])
        missed_medication = data.get("missed_medication", False)
        worsening_symptoms = data.get("worsening_symptoms", False)

        reasoning: List[str] = []
        red_flags = []
        for symptom in symptoms:
            s = str(symptom).lower()
            matched = next((flag for flag in self.RED_FLAG_SYMPTOMS if flag in s), None)
            if matched:
                red_flags.append(symptom)
                reasoning.append(f"Symptom {symptom!r} matches red flag {matched!r}")

        if missed_medication:
            reasoning.append("Missed medication reported")
        if worsening_symptoms:
            reasoning.append("Worsening symptoms reported")

        if red_flags or missed_medication or worsening_symptoms:
            # Red flags are the most urgent; medication/symptom drift is lower.
            severity = "critical" if red_flags else "elevated"
            self.log_action("escalating", {"red_flags": red_flags, "missed": missed_medication, "severity": severity})
            return {
                "escalated": True,
                "severity": severity,
                "reason": "Red flag symptoms detected" if red_flags else "Medication/symptom escalation",
                "red_flags": red_flags,
                "reasoning": reasoning,
                "alert_doctor": True,
                "recommend_attention": True,
            }

        return {"escalated": False, "severity": "none", "reasoning": ["No red flags or escalation triggers detected"]}
