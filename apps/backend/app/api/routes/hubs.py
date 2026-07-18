from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.models.scenario_schemas import HubSummary
from app.optimizer.data_loader import OptimizerDataError, get_optimizer_data

router = APIRouter()


@router.get("", response_model=list[HubSummary])
def list_hubs(cold_chain_only: bool = False) -> list[dict]:
    """Real hub list from Hub_Constraints -- backs the Run Scenario page's hub-selection
    controls (hubId / affectedHubIds) so parameter options come from the workbook, not a
    hardcoded frontend list. `cold_chain_only` filters to ColdChainAvailable == 'Yes',
    matching the cold_chain_restriction scenario's declared parameter source."""
    try:
        data = get_optimizer_data(settings.infineon_data_path)
    except OptimizerDataError as exc:
        raise HTTPException(status_code=424, detail=str(exc)) from exc

    hc = data.hc
    if cold_chain_only:
        hc = hc[hc.ColdChainAvailable == "Yes"]
    return [
        {
            "hubId": row.HubID, "stage": row.Stage, "city": row.City, "country": row.Country,
            "coldChainAvailable": row.ColdChainAvailable == "Yes",
        }
        for row in hc.itertuples()
    ]
