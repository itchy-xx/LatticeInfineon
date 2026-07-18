import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.optimizer.data_loader import OptimizerDataError, get_optimizer_data

logger = logging.getLogger(__name__)

app = FastAPI(title="Lattice Supply Chain API", version="0.1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
def _preload_optimizer_data() -> None:
    """Loads the Infineon workbook once at startup (not per-request, not per-scenario-run).
    If MOCK_MODE is on, skip -- the app still boots, but /scenarios/run will fail clearly
    until a real workbook is configured (no silent mock fallback, per requirement)."""
    if settings.mock_mode:
        logger.warning("MOCK_MODE is enabled: skipping Infineon workbook preload at startup.")
        return
    try:
        get_optimizer_data(settings.infineon_data_path)
    except OptimizerDataError as exc:
        logger.error("Could not preload Infineon workbook at startup: %s", exc)
