# HomzDoctor - AI Healthcare Platform

> **"Intelligent Healthcare Copilot for Patients and Providers"**

HomzDoctor is a production-grade healthcare AI platform designed as an intelligent copilot -- **NOT a final medical decision-maker**. It guides patients from medical imaging/lab results through diagnosis support, medication adherence, pharmacy fulfillment, and appointment scheduling.

## Core Vision & Constraint

**The system must NOT make final medical decisions.** It acts as an intelligent healthcare copilot that assists patients and healthcare providers. Licensed clinicians remain the approval authority for diagnoses, prescriptions, and treatment decisions.

## 8-Stage Core Workflow

| Stage | Component | Key Function |
|-------|-----------|------------|
| 1 | **Medical Data Ingestion** | Accept X-Rays, MRI, CT, DICOM, lab reports, PDFs, blood tests |
| 2 | **Imaging Preprocessing** | Volume reconstruction, N4 bias correction, normalization, spine segmentation |
| 3 | **ROI Sampling & Analysis** | Geo-mapping, ROI detection, slice montage, vision prompt building |
| 4 | **MedGemma Diagnostic Engine** | Pathology detection, report generation, differential diagnosis |
| 5 | **Structured Medical Report** | JSON / physician / patient-formatted reports |
| 6 | **Interactive AI Chat** | Qwen/Llama/Ollama-based assistant for post-diagnosis support |
| 7 | **Medication & Adherence** | Drug lookup, reminders (SMS, WhatsApp, push, email), adherence scoring |
| 8 | **Pharmacy & Appointments** | Location-based pharmacy search, inventory, ordering, hospital BPMN scheduling |

## Key Architecture: Human-in-the-Loop (HITL)

Every AI-generated finding goes through a **Doctor Review Layer** before reaching the patient:

```
Patient Uploads Data
        |
        v
Imaging Pipeline -> MedGemma Analysis -> Structured Findings (JSON + Report)
        |
        v
========================
 Doctor Review Layer
========================
        |
   Approve? --Yes--> Healthcare Agent Swarm
  /      \         (Patient Chat -> Medication -> Pharmacy -> Adherence)
Yes      No
  |        |
  v        v
Continue  Request More Info / Re-analysis
```

### Doctor Dashboard Controls:

| Action | Capability |
|--------|-----------|
| **Approve** | Accept AI findings |
| **Modify** | Change diagnosis, adjust severity, add notes/prescription |
| **Reject** | Request more imaging, additional labs, or escalate |

## Multi-Agent Architecture

| Agent | Responsibilities |
|-------|----------------|
| **Orchestrator** | Routing, planning, memory, task assignment |
| **Imaging** | DICOM parsing, MRI/CT processing, segmentation, localization, ROI detection |
| **Diagnostic (MedGemma)** | Inference, pathology detection, report generation |
| **Drug Knowledge** | Medication lookup, side effects, interactions |
| **Pharmacy** | Search, inventory lookup, ordering |
| **Appointment** | Doctor search, scheduling, reminders |
| **Patient Assistant** | Q&A, explain diagnosis/reports |

## Prescription-Only Flow

> **"Only physician-approved medications can move forward."**

```json
{
  "doctor_id": "123",
  "approved": true,
  "prescription": [
    {
      "drug": "Amoxicillin",
      "dose": "500mg",
      "frequency": "Every 8 hours",
      "duration": "7 days"
    }
  ]
}
```

## Location & Pharmacy Fulfillment Flow

```
Doctor Approved Prescription
        |
        v
Location Agent: GPS Coordinates
        |
        v
Nearest Pharmacy Search (within 2/5/10 km)
        |
        v
Inventory Check -> Patient Confirmation -> Order Creation -> Payment -> Delivery Tracking
```

## Escalation Agent (Safety-Critical)

**Triggers for immediate doctor alert:**
- Patient misses medication
- Symptoms worsen
- Red-flag symptoms detected:
  - Chest pain
  - Neurological deficit
  - Severe allergic reaction
  - High fever persistence

> "The system immediately recommends medical attention instead of continuing automated guidance."

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.11+, FastAPI |
| **Database** | PostgreSQL, Redis |
| **Message Queue** | RabbitMQ / Redis Streams |
| **AI/ML** | PyTorch, Transformers, MedGemma |
| **Image Processing** | SimpleITK, pydicom, nibabel |
| **Frontend** | React 18+, TypeScript, Tailwind CSS |
| **DevOps** | Docker, Kubernetes, GitHub Actions |

## Directory Structure

```
homzdoctor/
├── backend/              # FastAPI application
│   ├── agents/            # Multi-agent system (7 agents)
│   ├── api/               # REST API endpoints
│   ├── core/              # Config, security, database
│   ├── models/            # SQLAlchemy database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic layer
│   └── tests/             # Unit/integration tests
├── frontend/              # React application
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   └── tests/             # Frontend tests
├── ml/                    # ML models & inference
│   ├── models/            # Trained models (MedGemma)
│   ├── preprocessing/     # Image preprocessing pipeline
│   └── inference/         # Model inference engine
├── infra/                 # Infrastructure as Code
│   ├── docker/            # Docker configurations
│   ├── k8s/               # Kubernetes manifests
│   └── terraform/         # Terraform modules
└── docs/                  # Documentation
    ├── api/               # API documentation
    └── architecture/      # Architecture diagrams
```

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Node.js 18+ (frontend)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configurations
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

See `backend/.env.example` for required environment variables.

## API Documentation

Available at `http://localhost:8000/docs` (Swagger UI) when the backend is running.

## License

MIT License - see LICENSE file for details.
