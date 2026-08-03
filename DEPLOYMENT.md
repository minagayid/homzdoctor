# HomzDoctor local run guide

Deployment is intentionally out of scope for this project pass. HomzDoctor is
prepared as a local-first research/demo system and should be run on a trusted
development machine until clinical, security, privacy, regulatory, and
operational requirements are independently addressed.

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

## Local demo data

`SEED_DEMO_DATA=true` creates the local demo doctor and pharmacy records on
startup. Set it to `false` when starting with an empty database. Demo
credentials are intended only for local development and must not be reused in
any shared environment.

## Verification

```powershell
cd backend
python -m unittest discover -s tests -v
```

No deployment, cloud provisioning, migration service, or external notification
provider is part of this verified workflow.
