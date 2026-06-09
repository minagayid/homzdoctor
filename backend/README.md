# HomzDoctor Backend

AI Healthcare Platform - Intelligent Healthcare Copilot

## Features

- **Medical Data Ingestion**: X-Ray, MRI, CT, DICOM, lab reports, PDFs, blood tests
- **Imaging Preprocessing**: Volume reconstruction, N4 bias correction, normalization, spine segmentation
- **AI Diagnostics**: MedGemma-based pathology detection and report generation
- **Doctor Review (HITL)**: Human-in-the-loop verification before patient-facing results
- **Prescription Management**: Physician-approved prescriptions only
- **Pharmacy Integration**: Location-based pharmacy search and ordering
- **Medication Adherence**: Smart reminders and adherence tracking
- **Appointment Scheduling**: Doctor search and appointment management
- **Patient Assistant**: Q&A and report explanation

## Multi-Agent Architecture

The system uses 7 specialized agents:

1. **Orchestrator Agent**: Routing, planning, memory, task assignment
2. **Imaging Agent**: DICOM parsing, MRI/CT processing, segmentation
3. **Diagnostic Agent (MedGemma)**: Pathology detection, report generation
4. **Drug Knowledge Agent**: Medication lookup, side effects, interactions
5. **Pharmacy Agent**: Search, inventory lookup, ordering
6. **Appointment Agent**: Doctor search, scheduling, reminders
7. **Patient Assistant Agent**: Q&A, explain diagnosis/reports

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database and other configurations

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn main:app --reload
```

### Environment Variables

Create a `.env` file with:

```env
# Application
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-change-in-production

# Database
DATABASE_URL=postgresql://homzdoctor:***@localhost:5432/homzdoctor

# Redis
REDIS_URL=redis://localhost:6379/0

# AI/ML
MEDGEMMA_MODEL_PATH=./ml/models/medgemma
```

## API Documentation

Once the server is running, API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_medical.py
```

## License

MIT License - see LICENSE file for details.
