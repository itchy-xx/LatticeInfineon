"""Typed request/response models for the scenario API. camelCase JSON in/out; raw
pandas/Excel column names never leak past app/optimizer/scenarios.py's response builder.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


def to_camel(name: str) -> str:
    head, *tail = name.split("_")
    return head + "".join(w.capitalize() for w in tail)


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class HubSummary(CamelModel):
    hub_id: str
    stage: str
    city: str
    country: str
    cold_chain_available: bool


class ScenarioParameterSchema(CamelModel):
    name: str
    type: str
    label: str
    required: bool = False
    source: str | None = None
    min: float | None = None
    max: float | None = None
    step: float | None = None
    default: Any = None


class ScenarioDefinition(CamelModel):
    id: str
    label: str
    description: str
    supported: bool
    parameter_schema: list[ScenarioParameterSchema]
    scenario_type: str
    implementation_status: str


class ScenarioRunRequest(CamelModel):
    scenario_id: str
    parameters: dict[str, Any] = {}


class DataQualityWarning(CamelModel):
    code: str
    message: str
    context: str | None = None


class RouteComparison(CamelModel):
    shipment_id: str | None = None
    delivery_no: str | None = None
    internal_shipment_id: str | None = None
    route_option_id: str | None = None
    from_hub: str | None = None
    to_hub: str | None = None
    mode: str | None = None
    effective_lead_days: float | None = None
    cost: float | None = None
    risk: float | None = None
    solved: bool = False
    notes: str | None = None
    baseline_route_option_id: str | None = None
    baseline_effective_lead_days: float | None = None
    baseline_cost: float | None = None
    baseline_risk: float | None = None
    priority_weighted_score: float | None = None


class AffectedHub(CamelModel):
    hub_id: str


class AffectedRoute(CamelModel):
    route_option_id: str


class AffectedShipment(CamelModel):
    shipment_id: str


class IncidentDetails(CamelModel):
    scenario_id: str
    scenario_label: str
    affected_hub_ids: list[str]
    affected_shipment_ids: list[str]
    solved_count: int
    unsolved_count: int
    selection_changed: bool


class ScenarioSummary(CamelModel):
    internal_solved_count: int
    internal_total_count: int
    external_solved_count: int
    external_total_count: int
    affected_shipment_count: int
    selection_changed: bool


class ScenarioBaseline(CamelModel):
    internal_solved_count: int
    internal_total_count: int
    external_solved_count: int
    external_total_count: int


class ScenarioRef(CamelModel):
    id: str
    label: str


class ScenarioRunResult(CamelModel):
    run_id: str
    scenario: ScenarioRef
    status: str
    baseline: ScenarioBaseline
    summary: ScenarioSummary
    affected_hubs: list[AffectedHub]
    affected_routes: list[AffectedRoute]
    replacement_routes: list[AffectedRoute]
    affected_shipments: list[AffectedShipment]
    internal_assignments: list[RouteComparison]
    external_assignments: list[RouteComparison]
    alerts: list[Any] = []
    incident: IncidentDetails
    data_quality_warnings: list[DataQualityWarning]
    generated_at: str
