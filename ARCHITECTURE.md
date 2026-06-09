# HomzDoctor - AI Healthcare Platform Architecture

## Core Vision & Constraint

> **"The system must NOT make final medical decisions. It should act as an intelligent healthcare copilot that assists patients and healthcare providers."**

## Core Workflow: Patient Journey

**Stage 1: Medical Data Ingestion**
Accepts: X-Ray images, MRI scans, CT scans, DICOM series, laboratory/PDF reports, blood tests.

**Stage 2: Imaging Preprocessing**
- Volume Reconstruction (3D from DICOM slices)
- N4 Bias Field Correction (MRI intensity inhomogeneity)
- Intensity Normalization
- Spine Segmentation (vertebral, disc, spinal canal masks)
- Anatomical Localization (center of mass, vertebra coordinates, labels)

**Stage 3: ROI Sampling & Analysis**
- Geo Mapping (pathology locations)
- Level Iterator (vertebral level analysis)
- ROI Sweet Spot Detection
- Slice Montage Generation
- Vision Prompt Builder (optimized prompts for multimodal medical models)

**Stage 4: MedGemma Diagnostic Engine**
Primary medical reasoning model.
- **Input:** JSON
- **Output:** JSON
- **Capabilities:** Pathology detection, report generation, differential diagnosis, structured findings

**Stage 5: Structured Medical Report Generation**
- **JSON Report:** Machine-readable structured data
- **Human Report:** Physician-style clinical report
- **Patient Report:** Simplified explanation

## Critical Architecture: Human-in-the-Loop (HITL)

> "For a healthcare application, adding a Human-in-the-Loop (HITL) Doctor Verification Layer is a much stronger architecture than allowing fully autonomous diagnosis-to-treatment execution."

### Doctor Verification Workflow

Patient Uploads Data (X-ray / MRI / Lab)
           |
           v
Imaging Pipeline
           |
           v
MedGemma Analysis
           |
           v
Structured Findings (JSON + Report)
           |
           v
=======================
 Doctor Review Layer
=======================
           |
      Approve?
      /      \
    Yes      No
     |         |
     v         v
Healthcare  Request More
Agent        Information
Swarm        / Re-analysis
     |
     v
Patient Chat -> Medication -> Location -> Nearest Pharmacy -> Doctor-approved Prescription -> Medication Order -> Adherence Monitoring

### Doctor Dashboard

**Displays:**
- **Original Scan:** MRI/X-ray/CT viewer
- **AI Findings:** e.g., Detected Herniation, Confidence: 91%
- **Clinical Summary:** Generated report
- **Actions:** Approve / Edit / Reject / Request Follow-up

**Doctor Authority:**
| Action | Capability |
|--------|------------|
| **Approve** | Accept AI findings, proceed to patient-facing agents |
| **Modify** | Change diagnosis, adjust severity, add notes, add prescription |
| **Reject** | Request more imaging, request additional labs, escalate case |

## Prescription-Only Flow (Post-Doctor Approval)

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

**Location Agent (After doctor approval):**
- Requests patient GPS permission
- Retrieves: current coordinates, city, nearby pharmacies/hospitals

**Pharmacy Discovery Agent:**
- **Search radius:** Within 2 km / 5 km / 10 km
- **Returns:** Pharmacy name, distance, open/closed status, inventory, delivery availability

**Prescription Fulfillment Flow:**
Doctor Approved Prescription
            |
            v
Nearby Pharmacy Search
            |
            v
Inventory Check
            |
            v
Patient Confirmation   <-- "No automatic purchase without patient confirmation"
            |
            v
Order Creation -> Payment -> Delivery Tracking

## Medication Adherence Agent

**Smart Reminder System capabilities:**
- Push notifications, SMS, WhatsApp, email

**Schedule Generation:**
Amoxicillin 500mg
08:00 AM
04:00 PM
12:00 AM

**Tracking:**
- Taken / Skipped / Missed
- Adherence score

## Escalation Agent

**Triggers:**
- Patient misses medication
- Symptoms worsen
- Red-flag symptoms detected

**Red-Flag Examples:**
- Chest pain
- Neurological deficit
- Severe allergic reaction
- High fever persistence

**Action:** Immediate doctor alert; system recommends medical attention instead of continuing automated guidance.

## Multi-Agent Architecture

> **Key Architectural Improvement:** "Instead of [re-reading images], use [structured findings]. This makes the system much more scalable because every downstream agent works from structured findings rather than re-reading the images each time."

| Agent | Responsibilities |
|-------|------------------|
| **Orchestrator Agent** | Routing, planning, memory, task assignment |
| **Imaging Agent** | DICOM parsing, MRI/CT processing, segmentation, localization, ROI detection |
| **Diagnostic Agent (MedGemma)** | Pathology detection, report generation, differential diagnosis |
| **Drug Knowledge Agent** | Medication lookup, side effects, interactions |
| **Pharmacy Agent** | Search, inventory lookup, ordering |
| **Appointment Agent** | Doctor search, scheduling, reminders |
| **Patient Assistant Agent** | Q&A, explain diagnosis/reports |

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.11+, FastAPI |
| **Database** | PostgreSQL (relational), Redis (caching/sessions) |
| **Message Queue** | RabbitMQ / Redis Streams |
| **AI/ML** | PyTorch, Transformers, MedGemma |
| **Image Processing** | SimpleITK, pydicom, nibabel |
| **Frontend** | React 18+, TypeScript, Tailwind CSS |
| **Mobile** | React Native / Flutter (future) |
| **DevOps** | Docker, Kubernetes, GitHub Actions |
| **Monitoring** | Prometheus, Grafana, Sentry |

## Directory Structure

homzdoctor/
├── backend/              # FastAPI application
│   ├── agents/            # Multi-agent system
│   ├── api/               # API endpoints
│   ├── core/              # Config, security, db
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── tests/             # Unit/integration tests
├── frontend/              # React application
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   └── tests/             # Frontend tests
├── ml/                    # ML models & inference
│   ├── models/            # Trained models
│   ├── preprocessing/     # Image preprocessing
│   └── inference/         # Model inference
├── infra/                 # Infrastructure as Code
│   ├── docker/            # Docker configs
│   ├── k8s/               # Kubernetes manifests
│   └── terraform/         # Terraform modules
└── docs/                  # Documentation
    ├── api/               # API documentation
    └── architecture/      # Architecture diagrams
