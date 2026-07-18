import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

LEGACY_DIR = Path(__file__).resolve().parents[3] / "app" / "optimizer" / "legacy"
LEGACY_SCRIPT = LEGACY_DIR / "lattice_optimizer.py"
OUTPUT_WORKBOOK = LEGACY_DIR / "Lattice_Optimizer_Results.xlsx"


@router.post("")
def export_workbook() -> FileResponse:
    """Explicit-only: runs the untouched legacy script (its own openpyxl workbook-writing
    code, unmodified) to produce Lattice_Optimizer_Results.xlsx. Normal scenario-run
    requests never call this -- workbook generation only happens when this endpoint is
    explicitly invoked, per the requirement to keep it out of request-time scenario runs."""
    if not LEGACY_SCRIPT.is_file():
        raise HTTPException(status_code=424, detail="Legacy optimizer script not found.")
    proc = subprocess.run(
        [sys.executable, str(LEGACY_SCRIPT)], cwd=str(LEGACY_DIR),
        capture_output=True, text=True, timeout=600,
    )
    if proc.returncode != 0 or not OUTPUT_WORKBOOK.is_file():
        err = proc.stderr[-2000:] if proc.stderr else "unknown error"
        raise HTTPException(status_code=500, detail=f"Workbook export failed: {err}")
    return FileResponse(
        str(OUTPUT_WORKBOOK),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="Lattice_Optimizer_Results.xlsx",
    )
