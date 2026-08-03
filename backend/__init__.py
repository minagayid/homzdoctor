"""HomzDoctor backend package.

The application modules retain simple absolute imports so the documented
``uvicorn main:app`` command works from the backend directory. Adding the
backend directory to the module search path also makes ``backend.main`` work
from the repository root and keeps tests/launchers portable.
"""

from pathlib import Path
import sys

_BACKEND_DIR = str(Path(__file__).resolve().parent)
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)
