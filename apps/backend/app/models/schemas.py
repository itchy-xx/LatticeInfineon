from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class SourceMetadata(BaseModel):
    source_system: str
    observed_at: datetime
    freshness_score: float | None = Field(default=None, ge=0, le=1)
    confidence_score: float | None = Field(default=None, ge=0, le=1)

class SupplyChainRecord(BaseModel):
    id: str
    record_type: str
    status: str | None = None
    partner_id: str | None = None
    occurred_at: datetime | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    source: SourceMetadata

class Overview(BaseModel):
    partners: int
    shipments: int
    production_events: int
    open_alerts: int
    data_status: str = "mock"
