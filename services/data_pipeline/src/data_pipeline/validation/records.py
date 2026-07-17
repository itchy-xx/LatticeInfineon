import pandas as pd
def validate_non_empty(frame:pd.DataFrame)->list[str]:
    """Minimal structural check; add confirmed contract rules tomorrow."""
    return ["dataset is empty"] if frame.empty else []
