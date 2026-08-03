# HomzDoctor architecture

HomzDoctor is a local-first healthcare copilot prototype. It organizes private
medical uploads, produces clearly labeled decision-support output when an
optional model is configured, and routes clinical actions through authenticated
ownership and clinician-review gates. It is not a diagnostic device or an
autonomous treatment system.

## Local workflow

```text
Patient account
      |
      v
Private upload -> persisted medical record -> optional analysis run
                                              |
                                              v
                                      mandatory doctor review
                                              |
                         +--------------------+--------------------+
                         |                                         |
                   approve/review                            reject/follow-up
                         |
                         v
                  doctor-approved prescription
                         |
                patient confirmation required
                         |
                         v
                pharmacy/inventory integration
```

The offline path uses FastAPI, SQLAlchemy with SQLite, local file storage, and
deterministic safety fallbacks. An OpenAI-compatible local model can be added
without changing the API contract. Qdrant retrieval and Hugging Face inference
are optional extras, and patient retrieval is scoped to curated knowledge plus
the authenticated patient’s own records.

## Safety boundaries

- Public registration creates patient accounts only.
- Uploads are ownership-checked, extension-validated, size-limited, and stored
  with generated filenames.
- Analysis results are persisted as pending review and include a doctor-review
  requirement.
- Patients cannot write clinical findings or approve their own records.
- Prescriptions require a reviewed record, a prescribing clinician, and
  clinician approval.
- Pharmacy ordering is disabled unless an explicit provider is configured and
  patient confirmation is present.
- Missing AI, inventory, notification, or appointment providers report an
  explicit unavailable state rather than claiming success.

## Components

| Component | Local implementation |
| --- | --- |
| API | FastAPI under `backend/api/` |
| Persistence | SQLAlchemy async + SQLite by default |
| Uploads | Generated-name local file store |
| AI compatibility | Optional OpenAI-compatible local chat endpoint |
| Knowledge retrieval | Optional Qdrant + embeddings |
| Web interface | React + TypeScript under `frontend/` |
| Verification | Python unittest suite and frontend production build |

## Deliberate non-goals

Cloud deployment, autonomous diagnosis or treatment, real pharmacy purchases,
external notification delivery, and clinical validation are not included in
this local verification pass.
