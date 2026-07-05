"""Seed content for the RAG knowledge base.

A small, curated set of patient-education snippets the assistant can ground its
answers in. This is intentionally general, safety-first guidance — NOT diagnosis.
Seeded into Qdrant on startup (idempotent: point ids are content hashes).

To ingest richer sources (clinical leaflets, formularies, your own SOPs), add
them here or push them through ``VectorStore.upsert`` from an admin route.
"""

from __future__ import annotations

from typing import Dict, List

# Each entry becomes one vector point. ``source="knowledge"`` distinguishes the
# curated KB from patient-specific record embeddings (``source="record"``).
KNOWLEDGE_SNIPPETS: List[Dict[str, str]] = [
    {
        "title": "Medication adherence basics",
        "text": (
            "Take medications exactly as prescribed — same dose, same times each day. "
            "If you miss a dose, take it as soon as you remember unless it is almost time "
            "for the next dose; never double up to catch up. Set reminders and use a pill "
            "organizer. Do not stop antibiotics early even if you feel better, as this can "
            "cause the infection to return and build resistance."
        ),
    },
    {
        "title": "Reading an imaging report",
        "text": (
            "Radiology reports describe what a scan shows: 'findings' list observations, and "
            "the 'impression' summarizes what they likely mean. Phrases like 'no acute "
            "abnormality' are reassuring. 'Correlate clinically' means the finding must be "
            "interpreted alongside your symptoms by your doctor. Only a licensed clinician can "
            "confirm what a report means for you."
        ),
    },
    {
        "title": "When to seek urgent care (red flags)",
        "text": (
            "Seek emergency care immediately for: chest pain or pressure, sudden trouble "
            "breathing, sudden weakness or numbness on one side, difficulty speaking, a severe "
            "allergic reaction (swelling of lips/throat, widespread hives), a very high fever "
            "that will not come down, or the worst headache of your life. Do not wait for an "
            "AI or online tool — call emergency services."
        ),
    },
    {
        "title": "Understanding blood test (CBC) results",
        "text": (
            "A complete blood count (CBC) measures red cells, white cells, and platelets. "
            "Low hemoglobin can indicate anemia; high white cells can indicate infection or "
            "inflammation. 'Within normal limits' means values fall in the expected range. "
            "Reference ranges vary by lab, age, and sex — your clinician interprets them "
            "together with your history."
        ),
    },
    {
        "title": "Antibiotics: safe use",
        "text": (
            "Antibiotics treat bacterial infections, not viral ones like the common cold. "
            "Finish the full prescribed course. Common side effects include nausea and "
            "diarrhea. Tell your doctor about any rash, swelling, or breathing difficulty — "
            "these can signal an allergy. Avoid alcohol with certain antibiotics such as "
            "metronidazole."
        ),
    },
    {
        "title": "Pain management guidance",
        "text": (
            "For mild pain, over-the-counter options like paracetamol/acetaminophen or "
            "ibuprofen can help when used as directed; do not exceed the daily maximum. New, "
            "severe, or worsening pain — especially chest, abdominal, or head pain — should be "
            "evaluated by a clinician promptly. Note what makes the pain better or worse to "
            "share at your appointment."
        ),
    },
    {
        "title": "How HomzDoctor works and its limits",
        "text": (
            "HomzDoctor is an intelligent healthcare copilot, not a decision-maker. Every "
            "AI-generated finding from an uploaded X-ray, CT, MRI, or lab report is routed to "
            "a licensed doctor for review before it guides any treatment. Prescriptions and "
            "diagnoses are approved only by a clinician. Use the assistant to understand your "
            "results and next steps — not to replace professional medical advice."
        ),
    },
    {
        "title": "Preparing for a doctor appointment",
        "text": (
            "Bring a list of current medications and doses, recent symptoms and when they "
            "started, past medical history, and any questions you have. Mention allergies and "
            "family history. If you uploaded scans or labs, they will already be available to "
            "your reviewing doctor in HomzDoctor."
        ),
    },
]


def knowledge_documents() -> List[Dict[str, object]]:
    """Shape the snippets into VectorStore.upsert documents."""
    return [
        {
            "text": f"{item['title']}. {item['text']}",
            "payload": {"source": "knowledge", "title": item["title"]},
        }
        for item in KNOWLEDGE_SNIPPETS
    ]
