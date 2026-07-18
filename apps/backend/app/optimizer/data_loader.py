"""Loads the Infineon workbook once and derives the scenario-independent structures
that legacy/lattice_optimizer.py also derives at import time (Route_Options groupings,
hub-by-stage lookups, primary-lane index, CPK_MIN/CPK_MAX). Values and formulas here are
copied verbatim from legacy/lattice_optimizer.py -- see core.py's module docstring for why
this duplication exists instead of importing the legacy module directly.
"""
from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from app.optimizer.core import (
    SCENARIOS,
    hub_pass,
    routes_available_in,
    set_hub_disruption_state,
)


class OptimizerDataError(RuntimeError):
    """Raised when the Infineon workbook is missing, unreadable, or missing required
    sheets/columns -- surfaced to the API layer as a clear error, never silently
    substituted with mock data."""


REQUIRED_SHEETS = {
    "Internal_Shipments": ["ShipmentID", "MaterialNo_Anon", "MaterialFamily", "StageFrom",
                            "StageTo", "ShipFrom_Alias", "ShipTo_Alias", "Qty", "ShipDate"],
    "Route_Options": ["RouteOptionID", "MaterialFamily", "StageFrom", "StageTo", "FromHub",
                       "ToHub", "TransportMode", "BaseLeadTimeDays", "BaseCostEUR",
                       "CapacityUnitsPerWeek", "RiskScore", "CO2Kg", "AvailableFlag",
                       "DisruptionScenario", "Notes"],
    "Hub_Constraints": ["HubID", "Stage", "City", "Country", "WeeklyCapacityUnits",
                         "MaxUtilizationPct", "CurrentUtilizationPct", "CapacityReductionPct",
                         "ColdChainAvailable", "ESDHandlingAvailable", "MoistureControlAvailable",
                         "LithiumHandlingAvailable", "FixedHandlingCost_EUR",
                         "VariableHandlingCostPerUnit_EUR"],
    "Material_Families": ["MaterialNo_Anon", "PriorityClass", "HazardClass",
                           "TempRequirement", "ShelfLifeDays"],
    "External Shipments": ["DeliveryNo", "InternalShipmentID_Link", "MaterialFamily_Link",
                            "InternalStageFrom_Link", "InternalStageTo_Link",
                            "ChargeableWeight_KG", "PUP_Date"],
}


@dataclass(frozen=True)
class OptimizerData:
    path: str
    mtime: float
    ints: pd.DataFrame
    ro: pd.DataFrame
    hc: pd.DataFrame
    mat: pd.DataFrame
    ext: pd.DataFrame
    ints_by_id: pd.DataFrame
    hubs_by_stage_country: dict
    hubs_by_stage_city: dict
    primary: pd.DataFrame
    primary_ids: set
    cand_by_scen: dict
    cpk_min: float
    cpk_max: float


def _read_workbook(path: Path) -> dict[str, pd.DataFrame]:
    if not path.is_file():
        raise OptimizerDataError(
            f"Infineon workbook not found at '{path}'. Set INFINEON_DATA_PATH to a valid "
            "workbook path (see .env.example)."
        )
    sheets: dict[str, pd.DataFrame] = {}
    for sheet, required_cols in REQUIRED_SHEETS.items():
        try:
            df = pd.read_excel(path, sheet)
        except ValueError as exc:
            raise OptimizerDataError(
                f"Infineon workbook '{path}' is missing required sheet '{sheet}': {exc}"
            ) from exc
        except Exception as exc:  # noqa: BLE001 - surfaced as a clear data-quality error
            raise OptimizerDataError(f"Could not open Infineon workbook '{path}': {exc}") from exc
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise OptimizerDataError(
                f"Sheet '{sheet}' in '{path}' is missing required column(s): {missing}"
            )
        sheets[sheet] = df
    return sheets


def load_optimizer_data(path: str | None = None) -> OptimizerData:
    """Mirrors legacy/lattice_optimizer.py's module-level load/derive block (SRC read
    through CPK_MIN/CPK_MAX), but as a pure function returning an immutable bundle instead
    of executing at import time / writing files. Call once at API startup and cache."""
    raw = Path(path or os.environ.get(
        "INFINEON_DATA_PATH", "./data/IFX_LOG_Master_Data-anonymised_StudentVersion.xlsx"
    )).expanduser()
    # Matches app/services/mock_store.py's existing convention: a relative path is resolved
    # against apps/backend (not the process cwd), since uvicorn is normally started with
    # apps/backend as cwd (scripts/dev.sh) but pytest runs from the repo root.
    resolved = raw if raw.is_absolute() else (Path(__file__).parents[2] / raw).resolve()
    sheets = _read_workbook(resolved)

    ints = sheets["Internal_Shipments"]
    ro = sheets["Route_Options"]
    hc = sheets["Hub_Constraints"]
    mf = sheets["Material_Families"]
    ext = sheets["External Shipments"]

    mat = mf.set_index("MaterialNo_Anon")
    ints_by_id = ints.set_index("ShipmentID")

    # hubs_by_stage_country/_city: pure lookups over Hub_Constraints, independent of any
    # per-scenario disruption state -- identical to legacy's module-level groupbys.
    hub_static = hc.set_index("HubID")
    hubs_by_stage_country = hub_static.reset_index().groupby(["Stage", "Country"])["HubID"].apply(list).to_dict()
    hubs_by_stage_city = hub_static.reset_index().groupby(["Stage", "City"])["HubID"].apply(list).to_dict()

    primary = ro[ro.Notes == "Primary planned lane"].set_index(
        ["MaterialFamily", "StageFrom", "StageTo", "FromHub", "ToHub"]
    )
    primary_ids = set(ro[ro.Notes == "Primary planned lane"].RouteOptionID)

    cand_by_scen = {
        s: routes_available_in(ro, s).groupby(["MaterialFamily", "StageFrom", "StageTo"])
        for s in SCENARIOS
    }

    # A11/A26: CPK_MIN/CPK_MAX derived once from a fixed PrimaryHubDown-state dead_hubs
    # reading, exactly as legacy does immediately before its External pass.
    hub_for_cpk, dead_hubs_for_cpk = set_hub_disruption_state(hc, "PrimaryHubDown")
    cpk_min, cpk_max = _derive_cpk_range(ext, ints_by_id, mat, hub_for_cpk, dead_hubs_for_cpk, cand_by_scen)

    return OptimizerData(
        path=str(resolved),
        mtime=resolved.stat().st_mtime,
        ints=ints, ro=ro, hc=hc, mat=mat, ext=ext, ints_by_id=ints_by_id,
        hubs_by_stage_country=hubs_by_stage_country, hubs_by_stage_city=hubs_by_stage_city,
        primary=primary, primary_ids=primary_ids, cand_by_scen=cand_by_scen,
        cpk_min=cpk_min, cpk_max=cpk_max,
    )


def _derive_cpk_range(ext, ints_by_id, mat, hub_df, dead_hubs, cand_by_scen) -> tuple[float, float]:
    """Copied verbatim (formula-for-formula) from legacy's _cpk_samples/CPK_MIN/CPK_MAX block."""
    samples: list[float] = []
    for _, e in ext.iterrows():
        intl = ints_by_id.loc[e.InternalShipmentID_Link]
        m = mat.loc[intl.MaterialNo_Anon]
        hz = m.HazardClass if isinstance(m.HazardClass, str) else None
        cold = m.TempRequirement == "Cold Chain"
        key = (e.MaterialFamily_Link, e.InternalStageFrom_Link, e.InternalStageTo_Link)
        for scen in SCENARIOS:
            try:
                cc = cand_by_scen[scen].get_group(key)
            except KeyError:
                continue
            for _, r in cc.iterrows():
                if r.FromHub in dead_hubs or r.ToHub in dead_hubs:
                    continue
                cold_ok = (not cold) or (hub_df.loc[r.FromHub].ColdChainAvailable == "Yes"
                                          and hub_df.loc[r.ToHub].ColdChainAvailable == "Yes")
                if not cold_ok:
                    continue
                if not (hub_pass(hub_df, r.FromHub, hz) and hub_pass(hub_df, r.ToHub, hz)):
                    continue
                samples.append(r.BaseCostEUR / e.ChargeableWeight_KG)
    cpk_min, cpk_max = np.percentile(np.array(samples), [1, 99])
    return float(cpk_min), float(cpk_max)


_cache_lock = threading.Lock()
_cached: OptimizerData | None = None


def get_optimizer_data(path: str | None = None, force_reload: bool = False) -> OptimizerData:
    """Process-wide cache, loaded once at startup (see app/main.py). force_reload lets the
    export endpoint / tests pick up a changed workbook without restarting the process."""
    global _cached
    with _cache_lock:
        if _cached is None or force_reload:
            _cached = load_optimizer_data(path)
        return _cached
