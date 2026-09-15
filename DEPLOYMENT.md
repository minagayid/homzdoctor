# HomzDoctor local run guide

Deployment is intentionally out of scope for this project pass. HomzDoctor is
prepared as a local-first research/demo system and should be run on a trusted
development machine until clinical, security, privacy, regulatory, and
operational requirements are independently addressed.

This build has no clinic or doctor-to-patient assignment model: doctor review
and adherence views are system-wide. It is not suitable for multi-clinic use
or real patient records until access is scoped to an approved care relationship,
storage protection and audit requirements are met, and external processing is
governed. Do not configure hosted inference for patient images without an
approved data-processing and patient-consent path.

## Requirements

- Python 3.10–3.12
- Node.js 18+ only when using the React interface
- No PostgreSQL, Redis, Qdrant, Docker, or hosted AI account is required for
  the default offline workflow

## Backend

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
python run_homzdoctor.py
```

The API listens on `http://127.0.0.1:8000`; interactive documentation is at
`http://127.0.0.1:8000/docs`. SQLite data and generated upload files stay under
`backend/`.

## Frontend

In a second terminal:

```powershell
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

Open `http://localhost:3000`. The frontend uses the API URL configured in
`frontend/.env` or its local default.

## Optional local AI

The assistant can connect to an OpenAI-compatible local server such as Ollama,
vLLM, or llama.cpp. Configure `LOCAL_LLM_BASE_URL`, `LOCAL_LLM_MODEL`, and
`LOCAL_LLM_API_KEY` in `backend/.env`. The application remains usable with a
deterministic safety fallback when no model server is available.
When `HF_TOKEN` is configured, the hosted vision path can send uploaded medical
images and prompts to Hugging Face. Prefer a local inference server for this
demo unless that external data flow has been explicitly approved.

The API rejects request bodies above the configured upload limit plus 1 MiB
before multipart parsing. Keep an equal or lower request-body and concurrency
limit at any reverse proxy used for a local shared environment.

## Local demo data

`SEED_DEMO_DATA` defaults to `false`. Set it to `true` only for an isolated
local demo to create the sample doctor and pharmacy records on startup. The
application rejects demo seeding in production. Demo credentials are intended
only for local development and must not be reused in any shared environment.

## Verification

```powershell
cd backend
python -m unittest discover -s tests -v
```

No deployment, cloud provisioning, migration service, or external notification
provider is part of this verified workflow.
