"""Backend-owned scenario registry -- GET /api/v1/scenarios. The frontend requests this
list rather than hardcoding scenario labels/descriptions, per the integration requirement.
`supported`/`implementationStatus` are honest per the scenario audit: PortCongestion and
ColdChainRestriction are parameterized simulations, not native engine scenarios; Expedited
priority never reroutes (supplementary re-score only) -- see scenarios.py docstring.

Port congestion / Cold-chain restriction also carry a `default` on their parameterSchema
entries: a pre-picked, REAL example (which HubID to demo with) so "Run Scenario" works with
no typing, still fully editable by the user. The choice of WHICH hub to feature is a curated
demo decision (Manila BE_LOC_001 -- the same hub data.js's own static INCIDENT mock already
models port congestion on; Cebu OSAT_LOC_065 -- a real cold-chain-capable hub on the same
illustrative map, connected to Manila via data.js's EDGES so the disruption is visible on the
small demo map). The VALUES themselves (capacityReductionPct etc.) are read live from the
loaded workbook every request, never hardcoded, so they can never drift from the real data.
This lives entirely in the backend, not the frontend, per "the frontend must not contain a
hardcoded Manila hub, port, reduction percentage."
"""
from __future__ import annotations

# Curated demo hubs -- chosen because they're real, already on the illustrative frontend map
# (data.js HUBS), and produce a visible result. Not used for anything but pre-filling a
# default; the user can pick any other real hub instead.
PORT_CONGESTION_DEMO_HUB = "BE_LOC_001"       # Manila -- matches data.js's own INCIDENT mock
COLD_CHAIN_DEMO_HUB = "OSAT_LOC_065"          # Cebu -- cold-chain-capable, linked to Manila


def _static_registry() -> list[dict]:
    return [
        {
            "id": "normal_operations",
            "label": "Normal Operations",
            "description": "Baseline/reset state -- no disruption applied. Used for comparison "
                            "and to restore the dashboard after exiting a simulation.",
            "supported": True,
            "parameterSchema": [],
            "scenarioType": "baseline",
            "implementationStatus": "supported",
        },
        {
            "id": "primary_hub_down",
            "label": "Primary hub down",
            "description": "Runs the optimizer's native PrimaryHubDown scenario: affected hubs and "
                            "excluded routes come from Hub_Constraints/Route_Options, not a "
                            "hardcoded hub.",
            "supported": True,
            "parameterSchema": [],
            "scenarioType": "optimisation",
            "implementationStatus": "supported",
        },
        {
            "id": "air_capacity_reduced",
            "label": "Air capacity reduction",
            "description": "Runs the optimizer's native AirCapacityReduced scenario: reduced hub "
                            "capacity, queues and route changes come from the workbook's own "
                            "disruption data.",
            "supported": True,
            "parameterSchema": [],
            "scenarioType": "optimisation",
            "implementationStatus": "supported",
        },
        {
            "id": "port_congestion",
            "label": "Port congestion",
            "description": "Parameterized simulation: applies a requested capacity reduction to a "
                            "selected hub and re-runs the same hub-disruption/capacity-contention "
                            "logic used for Primary hub down. Simulated assumption, not a live "
                            "disruption.",
            "supported": True,
            "parameterSchema": [
                {"name": "hubId", "type": "hub", "label": "Congested hub", "required": True,
                 "source": "hubs"},
                {"name": "capacityReductionPct", "type": "number", "label": "Capacity reduction",
                 "required": True, "min": 0.01, "max": 1.0, "step": 0.01},
            ],
            "scenarioType": "simulation",
            "implementationStatus": "supported",
        },
        {
            "id": "cold_chain_restriction",
            "label": "Cold-chain restriction",
            "description": "Parameterized simulation: temporarily marks selected hub(s) as "
                            "cold-chain-unavailable and re-runs the optimizer's existing hard "
                            "cold-chain constraint unchanged -- never a soft penalty.",
            "supported": True,
            "parameterSchema": [
                {"name": "affectedHubIds", "type": "hub_multi", "label": "Affected hub(s)",
                 "required": True, "source": "cold_chain_capable_hubs"},
            ],
            "scenarioType": "simulation",
            "implementationStatus": "supported",
        },
        {
            "id": "expedited_priority",
            "label": "Expedited priority",
            "description": "Supplementary scoring lens only: shows the same selected routes as "
                            "Normal Operations, re-scored under each shipment's PriorityClass "
                            "weighting. The optimizer does not rerun route selection under "
                            "priority-shifted weights, so no route is shown as rerouted.",
            "supported": True,
            "parameterSchema": [],
            "scenarioType": "supplementary_analysis",
            "implementationStatus": "supplementary_only",
        },
    ]


# Backwards-compatible static export (no live defaults) -- kept for any caller that doesn't
# have loaded OptimizerData handy. GET /scenarios uses get_scenario_registry(data) instead.
SCENARIO_REGISTRY = _static_registry()


def get_scenario_registry(data) -> list[dict]:
    """Same registry, with `default` populated on port_congestion/cold_chain_restriction's
    parameterSchema entries from the REAL, currently-loaded Hub_Constraints sheet -- never a
    hardcoded number. Falls back to no default if the curated demo hub isn't present in this
    workbook (e.g. a different/updated dataset), rather than guessing."""
    registry = _static_registry()
    hc_by_id = data.hc.set_index("HubID")

    for scen in registry:
        if scen["id"] == "port_congestion" and PORT_CONGESTION_DEMO_HUB in hc_by_id.index:
            real_pct = float(hc_by_id.loc[PORT_CONGESTION_DEMO_HUB, "CapacityReductionPct"])
            for p in scen["parameterSchema"]:
                if p["name"] == "hubId":
                    p["default"] = PORT_CONGESTION_DEMO_HUB
                elif p["name"] == "capacityReductionPct" and real_pct > 0:
                    p["default"] = real_pct
        if scen["id"] == "cold_chain_restriction" and COLD_CHAIN_DEMO_HUB in hc_by_id.index:
            for p in scen["parameterSchema"]:
                if p["name"] == "affectedHubIds":
                    p["default"] = [COLD_CHAIN_DEMO_HUB]

    return registry
