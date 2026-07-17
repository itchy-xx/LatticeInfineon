from app.models.schemas import SupplyChainRecord
def process_event(event: SupplyChainRecord)->SupplyChainRecord:
    """Idempotent event seam for tracking, hand-offs, alerts and exceptions."""
    return event
