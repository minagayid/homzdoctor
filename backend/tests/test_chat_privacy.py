"""Tests that private record retrieval is scoped to the authenticated patient."""

import asyncio
import unittest

from services.medical import PatientAssistantService


class _CaptureVectorStore:
    def __init__(self):
        self.patient_id = "unset"

    async def search(self, query, top_k=4, source=None, patient_id=None):
        self.patient_id = patient_id
        return []


class _StaticAssistant:
    async def process(self, data):
        return {"response": "safe", "sources": [], "confidence": 0.0}


class ChatPrivacyTests(unittest.TestCase):
    def test_patient_id_is_passed_to_private_retrieval_scope(self):
        service = PatientAssistantService()
        capture = _CaptureVectorStore()
        service.vector_store = capture
        service.assistant = _StaticAssistant()

        asyncio.run(service.answer_query("What is in my report?", {"patient_id": 42}))

        self.assertEqual(capture.patient_id, 42)


if __name__ == "__main__":
    unittest.main()
