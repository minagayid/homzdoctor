"""Safety contracts for the dependency-free legacy agent facade."""

from __future__ import annotations

import asyncio
import unittest

from agents.core import (
    AppointmentAgent,
    DiagnosticAgent,
    DrugKnowledgeAgent,
    EscalationAgent,
    ImagingAgent,
    PatientAssistantAgent,
    PharmacyAgent,
)


class AgentSafetyTests(unittest.TestCase):
    def test_imaging_does_not_claim_to_process_a_missing_file(self):
        result = asyncio.run(
            ImagingAgent().process({"image_path": "missing-scan.dcm", "image_type": "ct"})
        )
        self.assertEqual(result["status"], "unavailable")
        self.assertTrue(result["doctor_review_required"])

    def test_diagnostic_fallback_is_explicitly_non_diagnostic(self):
        result = asyncio.run(DiagnosticAgent().process({"findings": {}}))
        self.assertEqual(result["status"], "unavailable")
        self.assertTrue(result["doctor_review_required"])
        self.assertIn("not a diagnosis", result["disclaimer"].lower())

    def test_drug_lookup_does_not_invent_a_description(self):
        result = asyncio.run(DrugKnowledgeAgent().process({"drug_name": "Unknown"}))
        self.assertEqual(result["status"], "unavailable")
        self.assertNotIn("placeholder", result["description"].lower())

    def test_legacy_pharmacy_agent_never_claims_to_place_an_order(self):
        result = asyncio.run(PharmacyAgent().process({"action": "order", "drug_name": "Unknown"}))
        self.assertFalse(result["order_created"])
        self.assertNotEqual(result["status"], "submitted")

    def test_legacy_appointment_agent_never_claims_persistence(self):
        result = asyncio.run(
            AppointmentAgent().process({"action": "schedule", "doctor_id": 1})
        )
        self.assertIsNone(result["appointment_id"])
        self.assertEqual(result["status"], "not_persisted")

    def test_patient_assistant_offline_response_is_cautious(self):
        result = asyncio.run(
            PatientAssistantAgent().process({"query": "What is my diagnosis?"})
        )
        self.assertNotIn("placeholder", result["response"].lower())
        self.assertEqual(result["confidence"], 0.0)

    def test_escalation_detects_red_flags_inside_a_sentence(self):
        result = asyncio.run(
            EscalationAgent().process({"symptoms": ["new chest pain this morning"]})
        )
        self.assertTrue(result["escalated"])
        self.assertTrue(result["recommend_attention"])


if __name__ == "__main__":
    unittest.main()
