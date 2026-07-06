"""Make the backend importable the same way the app runs it.

The application is launched from the ``backend/`` directory (``uvicorn
main:app``) and imports its own packages as top-level (``from api.routes
import router``). Putting this directory on sys.path lets the test suite
resolve ``main``, ``agents``, ``api`` and ``core`` identically, no matter
which directory pytest is invoked from.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
