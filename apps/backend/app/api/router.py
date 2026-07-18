from fastapi import APIRouter
from app.api.routes import (
    alerts,
    export,
    health,
    hubs,
    overview,
    partners,
    production_events,
    scenarios,
    shipments,
)
api_router = APIRouter()
api_router.include_router(health.router, tags=["system"])
api_router.include_router(overview.router, prefix="/overview", tags=["overview"])
api_router.include_router(partners.router, prefix="/partners", tags=["partners"])
api_router.include_router(shipments.router, prefix="/shipments", tags=["shipments"])
api_router.include_router(production_events.router, prefix="/production-events", tags=["production"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(hubs.router, prefix="/hubs", tags=["hubs"])
