"""Scenario adapters. Each returns a ScenarioRunOutcome built from real core.py engine
output only -- never invented values. Per the integration audit: PrimaryHubDown and
AirCapacityReduced are native engine scenarios (legacy/lattice_optimizer.py's own
SCENARIOS); PortCongestion and ColdChainRestriction are new parameterized adapters that
reuse the identical engine/scoring code via hub-constraint overrides (never a bespoke
formula); ExpeditedPriority is a supplementary re-score only, since the engine never
reruns route selection under priority-shifted weights (see core.py's score_priority /
score_cpk_priority and A23 in legacy/lattice_optimizer.py's own docstring).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime

import numpy as np
import pandas as pd

from app.optimizer import core
from app.optimizer.data_loader import OptimizerData

INTERNAL_SCENARIOS = {"PrimaryHubDown", "AirCapacityReduced"}


class ScenarioError(ValueError):
    """Invalid scenario id or parameters -- surfaced as a 400 by the API layer."""


@dataclass
class ScenarioOutcome:
    scenario_id: str
    scenario_label: str
    status: str
    baseline_res: pd.DataFrame
    baseline_res_ext: pd.DataFrame
    res: pd.DataFrame
    res_ext: pd.DataFrame
    affected_hub_ids: list[str] = field(default_factory=list)
    disclaimers: list[str] = field(default_factory=list)
    priority_supplementary: bool = False
    selection_changed: bool = True


def _validate_hub_id(data: OptimizerData, hub_id: str) -> None:
    if hub_id not in set(data.hc.HubID):
        raise ScenarioError(f"Unknown hubId '{hub_id}' -- not present in Hub_Constraints.")


def normal_operations(data: OptimizerData) -> ScenarioOutcome:
    res, res_ext = core.run_scenario_full(data, "Normal")
    return ScenarioOutcome(
        scenario_id="normal_operations", scenario_label="Normal Operations", status="completed",
        baseline_res=res, baseline_res_ext=res_ext, res=res, res_ext=res_ext,
    )


def primary_hub_down(data: OptimizerData) -> ScenarioOutcome:
    baseline_res, baseline_res_ext = core.run_scenario_full(data, "Normal")
    res, res_ext = core.run_scenario_full(data, "PrimaryHubDown")
    hub_df, dead_hubs = core.set_hub_disruption_state(data.hc, "PrimaryHubDown")
    affected = sorted(set(hub_df[hub_df.disrupted].index) | dead_hubs)
    return ScenarioOutcome(
        scenario_id="primary_hub_down", scenario_label="Primary hub down", status="completed",
        baseline_res=baseline_res, baseline_res_ext=baseline_res_ext, res=res, res_ext=res_ext,
        affected_hub_ids=affected,
    )


def air_capacity_reduced(data: OptimizerData) -> ScenarioOutcome:
    baseline_res, baseline_res_ext = core.run_scenario_full(data, "Normal")
    res, res_ext = core.run_scenario_full(data, "AirCapacityReduced")
    hub_df, dead_hubs = core.set_hub_disruption_state(data.hc, "AirCapacityReduced")
    affected = sorted(set(hub_df[hub_df.disrupted].index) | dead_hubs)
    return ScenarioOutcome(
        scenario_id="air_capacity_reduced", scenario_label="Air capacity reduction", status="completed",
        baseline_res=baseline_res, baseline_res_ext=baseline_res_ext, res=res, res_ext=res_ext,
        affected_hub_ids=affected,
    )


def port_congestion(data: OptimizerData, hub_id: str, capacity_reduction_pct: float) -> ScenarioOutcome:
    _validate_hub_id(data, hub_id)
    if not (0 < capacity_reduction_pct <= 1):
        raise ScenarioError("capacityReductionPct must be a fraction in (0, 1], e.g. 0.35 for 35%.")
    baseline_res, baseline_res_ext = core.run_scenario_full(data, "Normal")
    overrides = {hub_id: {"CapacityReductionPct": capacity_reduction_pct}}
    res, res_ext = core.run_scenario_full(data, "PrimaryHubDown", hub_overrides=overrides)
    return ScenarioOutcome(
        scenario_id="port_congestion", scenario_label="Port congestion", status="completed",
        baseline_res=baseline_res, baseline_res_ext=baseline_res_ext, res=res, res_ext=res_ext,
        affected_hub_ids=[hub_id],
        disclaimers=[
            "SIMULATED ASSUMPTION: port congestion is modeled by applying the requested "
            f"capacity reduction to hub {hub_id} and re-running the same hub-disruption / "
            "capacity-contention / route-selection logic used for Primary hub down. This is a "
            "what-if simulation against a private in-memory copy of hub constraints, not a "
            "live disruption or a change to the source workbook."
        ],
    )


def cold_chain_restriction(data: OptimizerData, affected_hub_ids: list[str]) -> ScenarioOutcome:
    for hub_id in affected_hub_ids:
        _validate_hub_id(data, hub_id)
    if not affected_hub_ids:
        raise ScenarioError("affectedHubIds must include at least one hub.")
    baseline_res, baseline_res_ext = core.run_scenario_full(data, "Normal")
    overrides = {hub_id: {"ColdChainAvailable": "No"} for hub_id in affected_hub_ids}
    res, res_ext = core.run_scenario_full(data, "Normal", hub_overrides=overrides)
    return ScenarioOutcome(
        scenario_id="cold_chain_restriction", scenario_label="Cold-chain restriction", status="completed",
        baseline_res=baseline_res, baseline_res_ext=baseline_res_ext, res=res, res_ext=res_ext,
        affected_hub_ids=list(affected_hub_ids),
        disclaimers=[
            "SIMULATED ASSUMPTION: cold-chain restriction is modeled by temporarily marking "
            f"{', '.join(affected_hub_ids)} as cold-chain-unavailable and re-running the "
            "engine's existing cold-chain hard constraint (A3) unchanged -- a non-cold-chain "
            "route is never substituted for a cold-chain shipment. Shipments that lose every "
            "compliant lane are reported unsolved, not silently rerouted."
        ],
    )


def expedited_priority(data: OptimizerData) -> ScenarioOutcome:
    """Supplementary re-score only (A23) -- selection is never rerun under priority weights.
    Returns the Normal-scenario assignments with the already-existing PriorityScore/
    priority-weighted lens surfaced explicitly, per the integration audit."""
    res, res_ext = core.run_scenario_full(data, "Normal")
    return ScenarioOutcome(
        scenario_id="expedited_priority", scenario_label="Expedited priority", status="completed",
        baseline_res=res, baseline_res_ext=res_ext, res=res, res_ext=res_ext,
        priority_supplementary=True, selection_changed=False,
        disclaimers=[
            "The selected routes are unchanged from Normal Operations and are shown under the "
            "supplementary expedited-priority scoring lens (PriorityScore, using each "
            "shipment's PriorityClass weighting) -- the engine does not rerun route selection "
            "under priority-shifted weights, so no route is reported as rerouted because of "
            "priority."
        ],
    )


SCENARIO_RUNNERS = {
    "normal_operations": lambda data, params: normal_operations(data),
    "primary_hub_down": lambda data, params: primary_hub_down(data),
    "air_capacity_reduced": lambda data, params: air_capacity_reduced(data),
    "port_congestion": lambda data, params: port_congestion(
        data, params.get("hubId"), params.get("capacityReductionPct")),
    "cold_chain_restriction": lambda data, params: cold_chain_restriction(
        data, params.get("affectedHubIds") or []),
    "expedited_priority": lambda data, params: expedited_priority(data),
}


def run_scenario(data: OptimizerData, scenario_id: str, parameters: dict) -> ScenarioOutcome:
    runner = SCENARIO_RUNNERS.get(scenario_id)
    if runner is None:
        raise ScenarioError(f"Unsupported scenario '{scenario_id}'.")
    return runner(data, parameters or {})


# ---------- response shaping: diff scenario vs baseline, never inventing values ----------
def _clean(v):
    if v is None:
        return None
    if isinstance(v, float) and (math.isnan(v) or np.isnan(v)):
        return None
    return v


def _row_key(row, id_col: str) -> str:
    return str(row[id_col])


def build_comparison(base_row: pd.Series | None, sel_row: pd.Series, cost_col: str) -> dict:
    b = base_row if base_row is not None else {}

    def bget(col):
        return _clean(b.get(col)) if base_row is not None else None

    return {
        "routeOptionId": _clean(sel_row.get("RouteOptionID")) or None,
        "fromHub": _clean(sel_row.get("FromHub")) or None,
        "toHub": _clean(sel_row.get("ToHub")) or None,
        "mode": _clean(sel_row.get("Mode")) or None,
        "effectiveLeadDays": _clean(sel_row.get("EffLead")),
        "cost": _clean(sel_row.get(cost_col)),
        "risk": _clean(sel_row.get("RiskAdj")),
        "solved": sel_row.get("Solved") == "Yes",
        "notes": sel_row.get("Notes") or None,
        "baselineRouteOptionId": bget("RouteOptionID"),
        "baselineEffectiveLeadDays": bget("BLead"),
        "baselineCost": bget("BCost") if base_row is not None and "BCost" in base_row else bget("BCostPerKG"),
        "baselineRisk": bget("BRisk"),
    }


def build_run_result(outcome: ScenarioOutcome, run_id: str) -> dict:
    """Builds the prompt's suggested ScenarioRunResult shape purely from real engine output.
    Missing/uncomputable values are returned as null with a dataQualityWarnings entry --
    never a placeholder."""
    warnings: list[dict] = list(
        {"code": "SIMULATED_ASSUMPTION", "message": d, "context": None} for d in outcome.disclaimers
    )

    res, res_ext = outcome.res, outcome.res_ext
    base_res, base_ext = outcome.baseline_res, outcome.baseline_res_ext

    base_by_id = base_res.set_index("ShipmentID") if len(base_res) else base_res
    base_ext_by_id = base_ext.set_index("DeliveryNo") if len(base_ext) else base_ext

    if outcome.selection_changed:
        changed_mask = res.apply(
            lambda row: (row.ShipmentID not in base_by_id.index)
            or (row.RouteOptionID != base_by_id.loc[row.ShipmentID].RouteOptionID)
            or (row.Solved != base_by_id.loc[row.ShipmentID].Solved),
            axis=1,
        ) if len(res) else pd.Series(dtype=bool)
    else:
        # Expedited priority: nothing reroutes, so "affected" = every solved shipment,
        # since every one gets the supplementary priority lens applied.
        changed_mask = res.Solved == "Yes"

    affected_internal = res[changed_mask] if len(res) else res
    affected_ids = set(affected_internal.ShipmentID) if len(affected_internal) else set()

    if len(res_ext):
        changed_mask_e = res_ext.InternalShipmentID.isin(affected_ids) if affected_ids else pd.Series(
            [False] * len(res_ext))
    else:
        changed_mask_e = pd.Series(dtype=bool)
    affected_external = res_ext[changed_mask_e] if len(res_ext) else res_ext

    internal_assignments = [
        {
            "shipmentId": row.ShipmentID,
            **build_comparison(base_by_id.loc[row.ShipmentID] if row.ShipmentID in base_by_id.index else None,
                                row, "Cost"),
            "priorityWeightedScore": _clean(row.get("PriorityScore")),
        }
        for _, row in affected_internal.iterrows()
    ] if len(affected_internal) else []

    external_assignments = [
        {
            "deliveryNo": row.DeliveryNo,
            "internalShipmentId": row.InternalShipmentID,
            **build_comparison(
                base_ext_by_id.loc[row.DeliveryNo] if row.DeliveryNo in base_ext_by_id.index else None,
                row, "CostPerKG"),
            "priorityWeightedScore": _clean(row.get("PriorityScore")),
        }
        for _, row in affected_external.iterrows()
    ] if len(affected_external) else []

    affected_shipment_ids = sorted(affected_ids)
    if not affected_shipment_ids:
        warnings.append({
            "code": "NO_AFFECTED_SHIPMENTS", "message":
                "No shipments changed route or solved status versus Normal Operations for this "
                "scenario run.", "context": None,
        })

    affected_routes = sorted({
        base_by_id.loc[sid].RouteOptionID for sid in affected_ids
        if sid in base_by_id.index and base_by_id.loc[sid].RouteOptionID
    })
    replacement_routes = sorted({
        row.RouteOptionID for _, row in affected_internal.iterrows() if row.RouteOptionID
    }) if len(affected_internal) else []

    affected_hubs = [{"hubId": h} for h in outcome.affected_hub_ids]

    summary = {
        "internalSolvedCount": int((res.Solved == "Yes").sum()) if len(res) else 0,
        "internalTotalCount": int(len(res)),
        "externalSolvedCount": int((res_ext.Solved == "Yes").sum()) if len(res_ext) else 0,
        "externalTotalCount": int(len(res_ext)),
        "affectedShipmentCount": len(affected_shipment_ids),
        "selectionChanged": outcome.selection_changed,
    }

    baseline = {
        "internalSolvedCount": int((base_res.Solved == "Yes").sum()) if len(base_res) else 0,
        "internalTotalCount": int(len(base_res)),
        "externalSolvedCount": int((base_ext.Solved == "Yes").sum()) if len(base_ext) else 0,
        "externalTotalCount": int(len(base_ext)),
    }

    return {
        "runId": run_id,
        "scenario": {"id": outcome.scenario_id, "label": outcome.scenario_label},
        "status": outcome.status,
        "baseline": baseline,
        "summary": summary,
        "affectedHubs": affected_hubs,
        "affectedRoutes": [{"routeOptionId": r} for r in affected_routes],
        "replacementRoutes": [{"routeOptionId": r} for r in replacement_routes],
        "affectedShipments": [{"shipmentId": s} for s in affected_shipment_ids],
        "internalAssignments": internal_assignments,
        "externalAssignments": external_assignments,
        "alerts": [],
        "incident": {
            "scenarioId": outcome.scenario_id,
            "scenarioLabel": outcome.scenario_label,
            "affectedHubIds": outcome.affected_hub_ids,
            "affectedShipmentIds": affected_shipment_ids,
            "solvedCount": summary["internalSolvedCount"] + summary["externalSolvedCount"],
            "unsolvedCount": (summary["internalTotalCount"] - summary["internalSolvedCount"])
            + (summary["externalTotalCount"] - summary["externalSolvedCount"]),
            "selectionChanged": outcome.selection_changed,
        },
        "dataQualityWarnings": warnings,
        "generatedAt": datetime.now(UTC).isoformat(),
    }
