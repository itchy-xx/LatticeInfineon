import pandas as pd
from data_pipeline.mappings.base import FieldMapping
def to_canonical(frame:pd.DataFrame,mapping:FieldMapping)->pd.DataFrame:
    return frame.rename(columns=mapping.apply(list(frame.columns))).copy()
