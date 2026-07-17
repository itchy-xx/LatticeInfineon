import pandas as pd
def process_supply_chain_events(frame:pd.DataFrame)->pd.DataFrame:
    """Idempotent seam for shipment/production tracking, hand-offs and alerts."""
    return frame.drop_duplicates().copy()
