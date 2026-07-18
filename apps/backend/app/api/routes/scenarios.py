import uuid

from app.core.config import settings
from app.models.scenario_schemas import ScenarioDefinition, ScenarioRunRequest, ScenarioRunResult
from app.optimizer.data_loader import OptimizerDataError, get_optimizer_data
from app.optimizer.registry import get_scenario_registry
from app.optimizer.scenarios import ScenarioError, build_run_result, run_scenario
from fastapi import APIRouter, HTTPException

router = APIRouter()

# In-process, per-runId result store -- isolated per simulation run, never a single shared
# "current scenario" global. Fine for this prototype's scope (no auth/session infra exists
# elsewhere in the app either); a real deployment would key this off a user session instead.
_run_cache: dict[str, dict] = {}
_scenario_param_cache: dict[tuple, str] = {}


def _hashable(value):
    """Parameters may contain lists (e.g. affectedHubIds) -- make the cache key hashable
    without changing the request's actual meaning."""
    if isinstance(value, list):
        return tuple(_hashable(v) for v in value)
    if isinstance(value, dict):
        return tuple(sorted((k, _hashable(v)) for k, v in value.items()))
    return value


@router.get("", response_model=list[ScenarioDefinition])
def list_scenarios() -> list[dict]:
    try:
        data = get_optimizer_data(settings.infineon_data_path)
    except OptimizerDataError as exc:
        raise HTTPException(status_code=424, detail=str(exc)) from exc
    return get_scenario_registry(data)


@router.post("/run", response_model=ScenarioRunResult)
def run(request: ScenarioRunRequest) -> dict:
    try:
        data = get_optimizer_data(settings.infineon_data_path)
    except OptimizerDataError as exc:
        raise HTTPException(status_code=424, detail=str(exc)) from exc

    cache_key = (
        request.scenario_id,
        tuple(sorted((k, _hashable(v)) for k, v in request.parameters.items())),
        data.mtime,
    )
    cached_run_id = _scenario_param_cache.get(cache_key)
    if cached_run_id and cached_run_id in _run_cache:
        return _run_cache[cached_run_id]

    try:
        outcome = run_scenario(data, request.scenario_id, request.parameters)
    except ScenarioError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - surfaced as a clear optimizer failure, never masked
        raise HTTPException(status_code=500, detail=f"Optimizer run failed: {exc}") from exc

    run_id = str(uuid.uuid4())
    result = build_run_result(outcome, run_id)
    _run_cache[run_id] = result
    _scenario_param_cache[cache_key] = run_id
    return result


@router.get("/runs/{run_id}", response_model=ScenarioRunResult)
def get_run(run_id: str) -> dict:
    result = _run_cache.get(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No scenario run found for runId '{run_id}'.")
    return result
