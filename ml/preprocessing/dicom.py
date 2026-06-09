"""
DICOM Processing for HomzDoctor.
Handles loading, parsing, and standardizing DICOM files.
"""

import pydicom
import numpy as np
from typing import Dict, Any, List, Optional
from pathlib import Path


def load_dicom(file_path: str) -> pydicom.FileDataset:
    """Load a DICOM file."""
    return pydicom.dcmread(file_path)


def load_dicom_series(directory: str) -> List[pydicom.FileDataset]:
    """Load a series of DICOM files and sort by slice position."""
    path = Path(directory)
    dicom_files = list(path.glob("*.dcm"))
    
    datasets = [pydicom.dcmread(f) for f in dicom_files]
    
    # Sort by slice location or image position
    def get_slice_position(ds):
        if hasattr(ds, 'SliceLocation'):
            return float(ds.SliceLocation)
        elif hasattr(ds, 'ImagePositionPatient'):
            return float(ds.ImagePositionPatient[2])  # Z coordinate
        return 0.0
    
    datasets.sort(key=get_slice_position)
    return datasets


def extract_metadata(ds: pydicom.FileDataset) -> Dict[str, Any]:
    """Extract relevant metadata from DICOM dataset."""
    metadata = {}
    
    # Patient info
    fields = [
        'PatientName', 'PatientID', 'PatientBirthDate', 'PatientSex',
        'StudyDate', 'StudyTime', 'StudyDescription',
        'SeriesDescription', 'Modality', 'Manufacturer',
        'SliceThickness', 'SliceLocation', 'ImagePositionPatient',
        'PixelSpacing', 'Rows', 'Columns', 'BitsAllocated',
        'SamplesPerPixel', 'PhotometricInterpretation',
    ]
    
    for field in fields:
        if hasattr(ds, field):
            metadata[field] = getattr(ds, field)
    
    return metadata


def get_pixel_array(ds: pydicom.FileDataset) -> np.ndarray:
    """Get pixel array from DICOM dataset."""
    return ds.pixel_array.astype(np.float32)


def apply_windowing(arr: np.ndarray, window_center: float, window_width: float) -> np.ndarray:
    """Apply window/level to normalize DICOM pixel values."""
    min_val = window_center - window_width / 2
    max_val = window_center + window_width / 2
    return np.clip(arr, min_val, max_val)


def normalize_image(arr: np.ndarray) -> np.ndarray:
    """Normalize image to 0-1 range."""
    min_val = arr.min()
    max_val = arr.max()
    if max_val > min_val:
        return (arr - min_val) / (max_val - min_val)
    return arr


def dicom_to_volume(series: List[pydicom.FileDataset]) -> np.ndarray:
    """Convert a DICOM series to a 3D volume."""
    slices = [get_pixel_array(ds) for ds in series]
    return np.stack(slices, axis=0)


class DICOMProcessor:
    """High-level DICOM processing class."""
    
    def __init__(self):
        pass
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single DICOM file."""
        ds = load_dicom(file_path)
        metadata = extract_metadata(ds)
        pixel_array = get_pixel_array(ds)
        
        return {
            "metadata": metadata,
            "pixel_array": pixel_array,
            "shape": pixel_array.shape,
        }
    
    def process_series(self, directory: str) -> Dict[str, Any]:
        """Process a DICOM series."""
        series = load_dicom_series(directory)
        
        # Get metadata from first slice
        metadata = extract_metadata(series[0])
        
        # Build 3D volume
        volume = dicom_to_volume(series)
        
        return {
            "metadata": metadata,
            "volume": volume,
            "num_slices": len(series),
            "shape": volume.shape,
        }
    
    def extract_single_frame(self, file_path: str, window_center: Optional[float] = None, window_width: Optional[float] = None) -> np.ndarray:
        """Extract and preprocess a single frame for display."""
        ds = load_dicom(file_path)
        arr = get_pixel_array(ds)
        
        # Apply windowing if specified
        if window_center is not None and window_width is not None:
            arr = apply_windowing(arr, window_center, window_width)
        elif hasattr(ds, 'WindowCenter') and hasattr(ds, 'WindowWidth'):
            wc = ds.WindowCenter[0] if isinstance(ds.WindowCenter, pydicom.multival.MultiValue) else ds.WindowCenter
            ww = ds.WindowWidth[0] if isinstance(ds.WindowWidth, pydicom.multival.MultiValue) else ds.WindowWidth
            arr = apply_windowing(arr, float(wc), float(ww))
        
        # Normalize
        arr = normalize_image(arr)
        
        return arr


def validate_dicom(ds: pydicom.FileDataset) -> bool:
    """Validate that a DICOM file has required fields for medical imaging."""
    required_fields = ['PatientName', 'StudyDate', 'Modality']
    
    for field in required_fields:
        if not hasattr(ds, field):
            return False
    
    if ds.Modality not in ['CT', 'MR', 'XRAY', 'CR', 'DX']:
        return False
    
    return True
