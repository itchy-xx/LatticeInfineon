from fastapi import APIRouter
from app.models.schemas import Overview
from app.services.mock_store import by_type
router = APIRouter()
@router.get("", response_model=Overview)
def overview() -> Overview:
    return Overview(partners=len(by_type("partner")), shipments=len(by_type("shipment")), production_events=len(by_type("production_event")), open_alerts=len([x for x in by_type("alert") if x.status == "open"]))
