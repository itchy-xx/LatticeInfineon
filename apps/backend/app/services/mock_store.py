import json
from functools import lru_cache
from pathlib import Path
from typing import Any
from app.core.config import settings
from app.models.schemas import SupplyChainRecord

@lru_cache
def records() -> list[SupplyChainRecord]:
    """Local bootstrap only; replace with repositories after schema confirmation."""
    path = Path(settings.mock_data_path)
    if not path.is_absolute(): path = (Path(__file__).parents[2] / path).resolve()
    payload: list[dict[str, Any]] = json.loads(path.read_text())
    return [SupplyChainRecord.model_validate(item) for item in payload]

def by_type(record_type: str) -> list[SupplyChainRecord]:
    return [item for item in records() if item.record_type == record_type]
