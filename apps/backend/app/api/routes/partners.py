from fastapi import APIRouter
from app.models.schemas import SupplyChainRecord
from app.services.mock_store import by_type
router=APIRouter()
@router.get("",response_model=list[SupplyChainRecord])
def list_partners()->list[SupplyChainRecord]: return by_type("partner")
