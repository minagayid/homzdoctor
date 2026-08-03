# HomzDoctor API

FastAPI backend for the local-first HomzDoctor workflow.

## Run from the repository root

```powershell
python -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
python run_homzdoctor.py
```

Or run directly from this directory:

```powershell
uvicorn main:app --host 127.0.0.1 --port 8000
```

The default configuration uses SQLite, local upload storage, deterministic offline responses, and no external services. See the root README for the optional local OpenAI-compatible gpt-oss configuration.

## Tests

```powershell
python -m unittest discover -s tests -v
```

The application is a research/demo copilot. AI output requires clinician review and must not be used as a diagnosis, treatment instruction, or prescription.
