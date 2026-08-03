# HomzDoctor

HomzDoctor is a local-first healthcare copilot prototype for organizing medical uploads, generating clearly labeled research/decision-support results, and routing them through clinician review. It is not a diagnostic device, medical advice, prescription service, or replacement for a licensed professional.

## Local quick start

Requirements: Python 3.10–3.12. Node.js is only needed for the web interface.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
python run_homzdoctor.py
```

The API is available at `http://127.0.0.1:8000` and its documentation at `/docs`. The default database is SQLite and uploads remain under `backend/uploads/`. No external model, database, Redis server, vector database, or API key is required for the offline workflow.

To run the React interface in a second terminal:

```powershell
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

Open `http://localhost:3000`.

## Optional local open-source model

The assistant can use any OpenAI-compatible local server. Set these values in `backend/.env`:

```env
LOCAL_LLM_BASE_URL=http://127.0.0.1:11434/v1
LOCAL_LLM_MODEL=gpt-oss-20b
LOCAL_LLM_API_KEY=
```

The default remains offline and deterministic. OpenAI documents gpt-oss as a self-hosted open-weight model compatible with Ollama, vLLM, and llama.cpp: [OpenAI gpt-oss documentation](https://help.openai.com/en/articles/11870455-openai-open-weight-models-gpt-oss).

Hosted Hugging Face inference and Qdrant retrieval are optional extras:

```powershell
python -m pip install -r backend\requirements-optional-ai.txt
python -m pip install -r backend\requirements-optional-rag.txt
```

## Safety boundaries

- Public registration creates patient accounts only; doctor/admin access is not self-service.
- Medical uploads are private, size-limited, extension-validated, and stored under generated names.
- AI output is persisted as pending review and cannot directly approve treatment.
- Prescriptions require a doctor-reviewed record and clinician approval; pharmacy ordering also requires patient confirmation.
- Patient chat retrieval is scoped to curated knowledge plus the authenticated patient’s records.
- Missing optional models produce explicit offline/fallback states rather than fabricated findings.

## Tests

```powershell
cd backend
python -m unittest discover -s tests -v
```

The tests cover local storage, authentication/ownership boundaries, clinician review gating, persistent analysis results, retrieval privacy, local-model compatibility, and safe offline agent behavior.

## Project status

This is a local research/demo system. It has not been deployed and is not validated for clinical use, regulatory compliance, or autonomous diagnosis/treatment.
