"""Dependency-free agent facade with explicit offline/safety states.

The production routes use the persisted services and optional model adapters.
These small agents remain as a compatibility layer for callers of the original
architecture, but they never claim that a clinical operation happened when an
optional backend is absent.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

LOG = logging.getLogger("homzdoctor.agents")
DISCLAIMER = "This is not a diagnosis or treatment recommendation; clinician review is required."


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.memory: Dict[str, Any] = {}

    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def log_action(self, action: str, details: Dict[str, Any]) -> None:
        LOG.info("agent=%s action=%s details=%s", self.name, action, json.dumps(details, default=str))


class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("Orchestrator")
        self.agents: Dict[str, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        self.agents[agent.name] = agent

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        task_type = data.get("task_type")
        if task_type in self.agents:
            self.log_action("routing", {"task": task_type})
            return await self.agents[task_type].process(data)
        return {"error": f"No agent found for task: {task_type}"}


class ImagingAgent(BaseAgent):
    def __init__(self):
        super().__init__("Imaging")

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        image_path = data.get("image_path")
        image_type = data.get("image_type", "unknown")
        self.log_action("inspect_input", {"type": image_type})
        if not image_path or not Path(image_path).is_file():
            return {
                "status": "unavailable",
                "reason": "input_not_found",
                "image_path": image_path,
                "image_type": image_type,
                "doctor_review_required": True,
                "disclaimer": DISCLAIMER,
            }
        return {
            "status": "ready_for_optional_imaging_backend",
            "image_path": image_path,
            "image_type": image_type,
            "preprocessing": {
                "volume_reconstruction": "not_run",
                "normalization": "not_run",
                "segmentation": "not_run",
            },
            "findings": {"images": [], "confidence": 0.0},
            "doctor_review_required": True,
            "disclaimer": DISCLAIMER,
        }

    async def preprocess_dicom(self, dicom_path: str) -> Dict[str, Any]:
        if not Path(dicom_path).exists():
            return {"status": "unavailable", "reason": "input_not_found", "path": dicom_path}
        return {
            "status": "requires_optional_imaging_backend",
            "path": dicom_path,
            "doctor_review_required": True,
        }

    async def segment_spine(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "requires_optional_imaging_backend",
            "vertebrae": [],
            "discs": [],
            "spinal_canal": [],
            "doctor_review_required": True,
        }


class DiagnosticAgent(BaseAgent):
    def __init__(self):
        super().__init__("Diagnostic")
        self.model = None

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.log_action("model_unavailable", {})
        return {
            "status": "unavailable",
            "suspected_conditions": [],
            "confidence": 0.0,
            "differential_diagnosis": [],
            "report": {"json": {}, "physician": "", "patient": ""},
            "doctor_review_required": True,
            "disclaimer": DISCLAIMER,
        }

    async def generate_report(self, findings: Dict[str, Any]) -> Dict[str, str]:
        return {
            "json": json.dumps(findings, default=str),
            "physician": "No report generated: an optional diagnostic model is not configured.",
            "patient": "No explanation generated: ask a clinician to review the source material.",
        }


class DrugKnowledgeAgent(BaseAgent):
    def __init__(self):
        super().__init__("DrugKnowledge")
        self.drug_db: Dict[str, Any] = {}

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        drug_name = data.get("drug_name")
        if drug_name and drug_name.lower() in self.drug_db:
            return dict(self.drug_db[drug_name.lower()])
        return {
            "status": "unavailable",
            "name": drug_name,
            "description": "No verified medication database is configured.",
            "side_effects": [],
            "interactions": [],
            "disclaimer": "Do not change medication based on this tool; consult a pharmacist or clinician.",
        }

    async def check_interactions(self, drugs: List[str]) -> List[Dict[str, Any]]:
        return []


class PharmacyAgent(BaseAgent):
    def __init__(self):
        super().__init__("Pharmacy")

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any] | List[Dict[str, Any]]:
        action = data.get("action")
        if action == "search":
            return await self.search_pharmacies(data)
        if action == "check_inventory":
            return await self.check_inventory(data)
        if action == "order":
            return await self.place_order(data)
        return {"error": f"Unknown pharmacy action: {action}"}

    async def search_pharmacies(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

    async def check_inventory(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"available": None, "status": "not_configured"}

    async def place_order(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "order_id": None,
            "order_created": False,
            "status": "not_configured",
            "requires_doctor_approval_and_patient_confirmation": True,
        }


class AppointmentAgent(BaseAgent):
    def __init__(self):
        super().__init__("Appointment")

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any] | List[Dict[str, Any]]:
        action = data.get("action")
        if action == "search_doctors":
            return []
        if action == "schedule":
            return {"appointment_id": None, "status": "not_persisted"}
        if action == "remind":
            return {"sent": False, "status": "not_configured"}
        return {"error": f"Unknown appointment action: {action}"}

    async def search_doctors(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

    async def schedule_appointment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"appointment_id": None, "status": "not_persisted"}

    async def send_reminder(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"sent": False, "status": "not_configured"}


class PatientAssistantAgent(BaseAgent):
    def __init__(self):
        super().__init__("PatientAssistant")

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        query = str(data.get("query") or "").strip()
        return {
            "response": (
                "The offline assistant cannot interpret a personal medical result. "
                "Please ask a licensed clinician to review it."
                if query
                else "Please provide a question."
            ),
            "sources": [],
            "confidence": 0.0,
            "model": "offline-fallback",
        }

    async def explain_report(self, report: Dict[str, Any]) -> str:
        return "Only a licensed clinician can explain what this report means for you."


class EscalationAgent(BaseAgent):
    RED_FLAG_SYMPTOMS = [
        "chest pain",
        "neurological deficit",
        "severe allergic reaction",
        "high fever persistence",
        "difficulty breathing",
        "shortness of breath",
        "severe headache",
    ]

    def __init__(self):
        super().__init__("Escalation")

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        symptoms = [str(symptom).lower() for symptom in (data.get("symptoms") or [])]
        red_flags = [
            symptom
            for symptom in symptoms
            if any(flag in symptom for flag in self.RED_FLAG_SYMPTOMS)
        ]
        escalated = bool(
            red_flags or data.get("missed_medication") or data.get("worsening_symptoms")
        )
        return {
            "escalated": escalated,
            "red_flags": red_flags,
            "reason": "Red flag symptoms detected" if red_flags else "Medication/symptom escalation" if escalated else None,
            "alert_doctor": escalated,
            "recommend_attention": escalated,
        }
