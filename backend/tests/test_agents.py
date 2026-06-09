"""
Unit tests for HomzDoctor multi-agent system.
"""

import pytest
import asyncio
from backend.agents.core import (
    OrchestratorAgent,
    ImagingAgent,
    DiagnosticAgent,
    DrugKnowledgeAgent,
    PharmacyAgent,
    AppointmentAgent,
    PatientAssistantAgent,
    EscalationAgent,
)


class TestOrchestratorAgent:
    """Test Orchestrator Agent."""
    
    @pytest.mark.asyncio
    async def test_routing_to_registered_agent(self):
        orchestrator = OrchestratorAgent()
        imaging_agent = ImagingAgent()
        
        orchestrator.register_agent(imaging_agent)
        
        result = await orchestrator.process({
            "task_type": "Imaging",
            "image_path": "/test/image.dcm",
            "image_type": "mri",
        })
        
        assert result["status"] == "processed"
        assert result["image_type"] == "mri"
    
    @pytest.mark.asyncio
    async def test_routing_to_unknown_agent(self):
        orchestrator = OrchestratorAgent()
        
        result = await orchestrator.process({
            "task_type": "UnknownAgent",
        })
        
        assert "error" in result
        assert "No agent found" in result["error"]


class TestImagingAgent:
    """Test Imaging Agent."""
    
    @pytest.mark.asyncio
    async def test_process_image(self):
        agent = ImagingAgent()
        
        result = await agent.process({
            "image_path": "/test/image.dcm",
            "image_type": "ct",
        })
        
        assert result["status"] == "processed"
        assert result["image_type"] == "ct"
        assert "preprocessing" in result
    
    @pytest.mark.asyncio
    async def test_preprocess_dicom(self):
        agent = ImagingAgent()
        
        result = await agent.preprocess_dicom("/test/series.dcm")
        
        assert result["status"] == "preprocessed"
    
    @pytest.mark.asyncio
    async def test_segment_spine(self):
        agent = ImagingAgent()
        
        result = await agent.segment_spine({"image": "test"})
        
        assert "vertebrae" in result
        assert "discs" in result
        assert "spinal_canal" in result


class TestDiagnosticAgent:
    """Test Diagnostic Agent (MedGemma)."""
    
    @pytest.mark.asyncio
    async def test_process_diagnosis(self):
        agent = DiagnosticAgent()
        
        result = await agent.process({
            "findings": {"test": "data"},
        })
        
        assert "suspected_conditions" in result
        assert "confidence" in result
        assert "differential_diagnosis" in result
        assert "report" in result
    
    @pytest.mark.asyncio
    async def test_generate_report(self):
        agent = DiagnosticAgent()
        
        report = await agent.generate_report({"finding": "test"})
        
        assert "json" in report
        assert "physician" in report
        assert "patient" in report


class TestDrugKnowledgeAgent:
    """Test Drug Knowledge Agent."""
    
    @pytest.mark.asyncio
    async def test_lookup_drug(self):
        agent = DrugKnowledgeAgent()
        
        result = await agent.process({
            "drug_name": "Amoxicillin",
        })
        
        assert result["name"] == "Amoxicillin"
        assert "description" in result
        assert "side_effects" in result
        assert "interactions" in result
    
    @pytest.mark.asyncio
    async def test_check_interactions(self):
        agent = DrugKnowledgeAgent()
        
        result = await agent.check_interactions(["Amoxicillin", "Ibuprofen"])
        
        assert isinstance(result, list)


class TestPharmacyAgent:
    """Test Pharmacy Agent."""
    
    @pytest.mark.asyncio
    async def test_search_pharmacies(self):
        agent = PharmacyAgent()
        
        result = await agent.process({
            "action": "search",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "radius_km": 5,
        })
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_check_inventory(self):
        agent = PharmacyAgent()
        
        result = await agent.process({
            "action": "check_inventory",
            "drug_name": "Amoxicillin",
        })
        
        assert "available" in result
    
    @pytest.mark.asyncio
    async def test_place_order(self):
        agent = PharmacyAgent()
        
        result = await agent.process({
            "action": "order",
            "drug_name": "Amoxicillin",
        })
        
        assert "order_id" in result
        assert "status" in result


class TestAppointmentAgent:
    """Test Appointment Agent."""
    
    @pytest.mark.asyncio
    async def test_search_doctors(self):
        agent = AppointmentAgent()
        
        result = await agent.process({
            "action": "search_doctors",
            "specialty": "Neurology",
        })
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_schedule_appointment(self):
        agent = AppointmentAgent()
        
        result = await agent.process({
            "action": "schedule",
            "doctor_id": 1,
            "datetime": "2024-01-15T10:00:00",
        })
        
        assert "appointment_id" in result
        assert result["status"] == "scheduled"


class TestPatientAssistantAgent:
    """Test Patient Assistant Agent."""
    
    @pytest.mark.asyncio
    async def test_answer_query(self):
        agent = PatientAssistantAgent()
        
        result = await agent.process({
            "query": "What is my diagnosis?",
            "context": {"record_id": 1},
        })
        
        assert "response" in result
        assert "sources" in result
        assert "confidence" in result
    
    @pytest.mark.asyncio
    async def test_explain_report(self):
        agent = PatientAssistantAgent()
        
        explanation = await agent.explain_report({"diagnosis": "test"})
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0


class TestEscalationAgent:
    """Test Escalation Agent."""
    
    @pytest.mark.asyncio
    async def test_no_escalation(self):
        agent = EscalationAgent()
        
        result = await agent.process({
            "symptoms": ["headache", "fatigue"],
            "missed_medication": False,
            "worsening_symptoms": False,
        })
        
        assert result["escalated"] is False
    
    @pytest.mark.asyncio
    async def test_escalation_red_flag(self):
        agent = EscalationAgent()
        
        result = await agent.process({
            "symptoms": ["chest pain", "shortness of breath"],
            "missed_medication": False,
            "worsening_symptoms": False,
        })
        
        assert result["escalated"] is True
        assert result["alert_doctor"] is True
        assert result["recommend_attention"] is True
    
    @pytest.mark.asyncio
    async def test_escalation_missed_medication(self):
        agent = EscalationAgent()
        
        result = await agent.process({
            "symptoms": [],
            "missed_medication": True,
            "worsening_symptoms": False,
        })
        
        assert result["escalated"] is True
    
    @pytest.mark.asyncio
    async def test_escalation_worsening(self):
        agent = EscalationAgent()
        
        result = await agent.process({
            "symptoms": ["mild pain"],
            "missed_medication": False,
            "worsening_symptoms": True,
        })
        
        assert result["escalated"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
