# HomzDoctor - ML Pipeline

Machine learning models and inference pipeline for the HomzDoctor AI Healthcare Platform.

## Components

### Models

- **MedGemma**: Primary diagnostic engine for pathology detection
- **Segmentation Models**: Spine segmentation, vertebral labeling
- **Image Classification**: X-ray/MRI/CT classification

### Preprocessing

- **DICOM Processing**: Parse and standardize DICOM files
- **Volume Reconstruction**: 3D volume from 2D slices
- **N4 Bias Field Correction**: MRI intensity correction
- **Normalization**: Intensity normalization

### Inference

- **Model Serving**: FastAPI-based inference server
- **Batch Processing**: Process multiple studies
- **Real-time Inference**: Single study processing

## Setup

### Prerequisites

- Python 3.11+
- CUDA 11.8+ (for GPU acceleration)
- 16GB+ RAM recommended

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download models (see scripts/download_models.py)
python scripts/download_models.py
```

### Usage

```python
from inference.engine import InferenceEngine

engine = InferenceEngine()

# Process medical image
result = engine.process_image("path/to/image.dcm")
# Returns: findings, confidence scores, segmentations

# Generate report
report = engine.generate_report(result)
# Returns: structured report in JSON/physician/patient formats
```

## Architecture

```
ml/
├── models/
│   ├── medgemma/           # MedGemma model weights
│   └── segmentation/       # Segmentation models
├── preprocessing/
│   ├── dicom.py           # DICOM processing
│   ├── volumes.py         # Volume reconstruction
│   ├── normalization.py   # Intensity correction
│   └── segmentation.py    # Image segmentation
├── inference/
│   ├── engine.py          # Inference engine
│   ├── models.py          # Model wrappers
│   └── server.py          # FastAPI inference server
└── scripts/
    ├── download_models.py  # Model download script
    └── benchmark.py      # Performance benchmarking
```

## Docker

```bash
# Run from the repository root. The context excludes local models/datasets and uses CPU PyTorch wheels.
docker build -f ml/Dockerfile -t homzdoctor-ml:local ml

# Start the container on loopback for synthetic-data checks
docker run --rm --init -p 127.0.0.1:8080:8080 -e PORT=8080 homzdoctor-ml:local
curl http://127.0.0.1:8080/health
```

The current `/analyze`, `/segment`, and `/preprocess` endpoints return placeholder outputs; this image is a deployment scaffold, not a validated model-serving or diagnostic system. Do not send real patient data.
