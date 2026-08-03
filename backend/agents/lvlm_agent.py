"""
Large Vision-Language Model (LVLM) diagnostic agent for HomzDoctor.

Reads medical imaging (X-ray, CT, MRI) and lab findings supplied as images or
PDFs, then runs a THREE-PASS pipeline:

    1. DIAGNOSE  - first-pass structured reading of the image(s)/labs.
    2. RECHECK   - a second, skeptical pass that re-examines the image and
                   challenges the first reading (self-verification / second
                   opinion) to catch hallucinated or missed findings.
    3. FINALISE  - reconcile pass 1 + pass 2 into a single final diagnosis with
                   a calibrated confidence and differentials.

⚠️ SAFETY: This is decision SUPPORT, not a diagnosis. Every result is flagged
``doctor_review_required = True`` and carries a disclaimer. A licensed clinician
remains the approval authority (see README "Human-in-the-Loop").

Requires (for real inference):
    pip install huggingface_hub pillow pymupdf
Environment:
    HF_TOKEN, HF_VLM_MODEL  (see services/hf_vision_service.py)
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from agents.core import BaseAgent
from services.document_loader import LoadedDocument, DocumentLoadError, load_path, load_document

LOG = logging.getLogger(__name__)

DISCLAIMER = (
    "AI-generated decision support only. Not a final diagnosis. "
    "Must be reviewed and approved by a licensed clinician."
)

_SYSTEM_PROMPT = (
    "You are a careful radiology and laboratory medicine assistant. "
    "You analyse medical images (X-ray, CT, MRI) and lab reports and produce "
    "STRUCTURED, conservative findings. You never invent findings that are not "
    "visible. You always express uncertainty when image quality, view, or "
    "context is insufficient. You are decision support for a clinician, not the "
    "final decision-maker."
)

_TRIAGE_INSTRUCTIONS = (
    "You are screening an uploaded file BEFORE any diagnosis. Decide whether it "
    "is genuine clinical material: a medical/radiological image (X-ray, CT, MRI, "
    "ultrasound, mammogram, etc.) OR a clinical laboratory/diagnostic report "
    "(blood panel, pathology, radiology report).\n"
    "Anything else — terms & conditions, contracts, invoices, receipts, legal or "
    "marketing text, screenshots, photos of people/objects, ID cards, forms — is "
    "NOT clinical material.{lab_note}\n"
    "Respond ONLY with JSON:\n"
    "{{\n"
    '  "is_medical": true,\n'
    '  "document_type": "short description, e.g. chest x-ray | CBC lab report | terms and conditions",\n'
    '  "reason": "one short sentence"\n'
    "}}"
)

_DIAGNOSE_INSTRUCTIONS = (
    "Examine the provided medical image(s){lab_note} for a study described as "
    "modality='{modality}'. Respond ONLY with a JSON object of the form:\n"
    "{{\n"
    '  "observations": ["concrete visual/lab observations"],\n'
    '  "suspected_conditions": [{{"condition": str, "likelihood": "low|moderate|high"}}],\n'
    '  "differential_diagnosis": ["alternative explanations"],\n'
    '  "image_quality": "adequate|limited|poor",\n'
    '  "confidence": 0.0,\n'
    '  "urgent_findings": ["anything needing immediate attention, else empty"]\n'
    "}}\n"
    "Base every observation strictly on what is visible in the image or stated "
    "in the lab text. Do not fabricate."
)

_RECHECK_INSTRUCTIONS = (
    "A first-pass reading of this study produced the following draft:\n"
    "{draft}\n\n"
    "Now act as an independent second reader. Re-examine the SAME image(s) and "
    "critically verify the draft. Identify: (a) any findings in the draft that "
    "are NOT actually supported by the image, (b) any findings that were MISSED, "
    "(c) whether the confidence is appropriately calibrated. Respond ONLY with "
    "JSON:\n"
    "{{\n"
    '  "unsupported_findings": [str],\n'
    '  "missed_findings": [str],\n'
    '  "agreement": "agree|partial|disagree",\n'
    '  "confidence_adjustment": "raise|keep|lower",\n'
    '  "notes": str\n'
    "}}"
)

_FINALISE_INSTRUCTIONS = (
    "First-pass reading:\n{draft}\n\n"
    "Second-reader verification:\n{recheck}\n\n"
    "Reconcile both into a SINGLE final assessment. Drop unsupported findings, "
    "add genuinely missed ones, and calibrate confidence accordingly. Respond "
    "ONLY with JSON:\n"
    "{{\n"
    '  "final_findings": [str],\n'
    '  "primary_impression": str,\n'
    '  "differential_diagnosis": [str],\n'
    '  "confidence": 0.0,\n'
    '  "recommended_next_steps": [str],\n'
    '  "urgent": false\n'
    "}}"
)


def _is_not_medical(triage: Dict[str, Any]) -> bool:
    """True only when triage CONFIDENTLY says the file is not clinical material.

    Fail-open: if triage is missing/unparseable we let the pipeline proceed (the
    result is doctor-reviewed anyway), but an explicit ``is_medical: false`` /
    "no" stops the diagnosis early.
    """
    value = triage.get("is_medical")
    if isinstance(value, bool):
        return value is False
    if isinstance(value, str):
        return value.strip().lower() in {"false", "no", "0", "non-medical", "not medical"}
    return False


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Best-effort: pull the first JSON object out of a model response."""
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            return None
    return None


class LVLMDiagnosticAgent(BaseAgent):
    """Vision-language diagnostic agent with a built-in recheck pass."""

    def __init__(self) -> None:
        super().__init__("LVLMDiagnostic")
        self._vision = None
        try:
            from services.hf_vision_service import get_hf_vision_service

            self._vision = get_hf_vision_service()
            LOG.info("LVLMDiagnostic initialised with model=%s", self._vision.model)
        except Exception as exc:
            LOG.warning("LVLM vision backend unavailable, will use fallback: %s", exc)
            self._vision = None

    def available(self) -> bool:
        return self._vision is not None

    # --- input handling -----------------------------------------------------

    def _collect_document(self, data: Dict[str, Any]) -> LoadedDocument:
        """Load images/text from whichever input the caller provided."""
        if data.get("file_bytes") is not None:
            return load_document(data["file_bytes"], data.get("filename", "upload"))
        if data.get("file_path"):
            return load_path(data["file_path"])
        # Pre-decoded images passed directly (list of base64 PNG strings).
        if data.get("images_b64"):
            return LoadedDocument(
                images_b64=list(data["images_b64"]),
                text=data.get("lab_text", ""),
                page_count=len(data["images_b64"]),
                source_name=data.get("filename", "inline"),
            )
        raise DocumentLoadError("No file_bytes, file_path, or images_b64 provided")

    # --- main pipeline ------------------------------------------------------

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        modality = (data.get("modality") or data.get("record_type") or "unknown").lower()

        try:
            document = self._collect_document(data)
        except DocumentLoadError as exc:
            return self._error(f"Could not read input: {exc}", modality)

        if not document.images_b64:
            return self._error("No readable image pages found in the input.", modality)

        if not self.available():
            return self._fallback(document, modality)

        image_urls = document.as_data_urls()
        lab_note = (
            f" and the following lab text:\n---\n{document.text[:4000]}\n---"
            if document.text.strip()
            else ""
        )

        try:
            # Pass 0 — triage: is this actually clinical material? Refuse early
            # (and cheaply) for non-medical uploads like terms & conditions.
            triage_raw = self._vision.analyze(
                prompt=_TRIAGE_INSTRUCTIONS.format(lab_note=lab_note),
                image_data_urls=image_urls,
                system=_SYSTEM_PROMPT,
                max_tokens=200,
            )
            triage = _extract_json(triage_raw) or {}
            if _is_not_medical(triage):
                self.log_action("rejected_non_medical", {"type": triage.get("document_type")})
                return self._rejected(document, modality, triage)

            # Pass 1 — initial diagnosis.
            draft_raw = self._vision.analyze(
                prompt=_DIAGNOSE_INSTRUCTIONS.format(modality=modality, lab_note=lab_note),
                image_data_urls=image_urls,
                system=_SYSTEM_PROMPT,
            )
            draft = _extract_json(draft_raw) or {"raw": draft_raw}

            # Pass 2 — recheck / second opinion (re-examines the same images).
            recheck_raw = self._vision.analyze(
                prompt=_RECHECK_INSTRUCTIONS.format(draft=json.dumps(draft, indent=2)),
                image_data_urls=image_urls,
                system=_SYSTEM_PROMPT,
            )
            recheck = _extract_json(recheck_raw) or {"raw": recheck_raw}

            # Pass 3 — finalise (text-only reconciliation is fine, but we keep
            # the images so the model can break ties visually).
            final_raw = self._vision.analyze(
                prompt=_FINALISE_INSTRUCTIONS.format(
                    draft=json.dumps(draft, indent=2),
                    recheck=json.dumps(recheck, indent=2),
                ),
                image_data_urls=image_urls,
                system=_SYSTEM_PROMPT,
            )
            final = _extract_json(final_raw) or {"primary_impression": final_raw}
        except Exception as exc:
            LOG.warning("LVLM inference failed, using fallback: %s", exc)
            return self._fallback(document, modality, error=str(exc))

        self.log_action(
            "diagnosed",
            {"modality": modality, "pages": document.page_count, "model": self._vision.model},
        )

        return {
            "modality": modality,
            "model": self._vision.model,
            "pages_analyzed": len(image_urls),
            "draft_diagnosis": draft,
            "recheck": recheck,
            "final_diagnosis": final,
            "confidence": float(final.get("confidence", draft.get("confidence", 0.0)) or 0.0),
            "urgent": bool(final.get("urgent")) or bool(draft.get("urgent_findings")),
            "doctor_review_required": True,
            "disclaimer": DISCLAIMER,
        }

    # --- rejection (non-medical upload) -------------------------------------

    def _rejected(
        self, document: LoadedDocument, modality: str, triage: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Short-circuit result for a file that is not a medical image/report."""
        doc_type = triage.get("document_type") or "non-clinical document"
        message = (
            f"This file does not appear to be a medical image or lab report "
            f"(detected: {doc_type}). Please upload an X-ray, CT, MRI, ultrasound, "
            f"or a clinical lab report."
        )
        return {
            "modality": modality,
            "model": self._vision.model if self._vision else "fallback",
            "pages_analyzed": len(document.images_b64),
            "rejected": True,
            "document_type": doc_type,
            "draft_diagnosis": {},
            "recheck": {},
            "final_diagnosis": {"primary_impression": message, "final_findings": [], "confidence": 0.0},
            "confidence": 0.0,
            "urgent": False,
            "doctor_review_required": False,
            "disclaimer": DISCLAIMER,
            "message": message,
        }

    # --- fallbacks ----------------------------------------------------------

    def _fallback(
        self, document: LoadedDocument, modality: str, error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deterministic safety fallback when the model backend is unavailable."""
        return {
            "modality": modality,
            "model": "fallback",
            "pages_analyzed": len(document.images_b64),
            "draft_diagnosis": {
                "observations": [],
                "image_quality": "unknown",
                "confidence": 0.0,
            },
            "recheck": {"agreement": "n/a", "notes": "Model backend unavailable."},
            "final_diagnosis": {
                "primary_impression": "Automated analysis unavailable — manual review needed.",
                "final_findings": [],
                "confidence": 0.0,
            },
            "confidence": 0.0,
            "urgent": False,
            "doctor_review_required": True,
            "disclaimer": DISCLAIMER,
            "error": error,
        }

    def _error(self, message: str, modality: str) -> Dict[str, Any]:
        return {
            "modality": modality,
            "error": message,
            "doctor_review_required": True,
            "disclaimer": DISCLAIMER,
        }
