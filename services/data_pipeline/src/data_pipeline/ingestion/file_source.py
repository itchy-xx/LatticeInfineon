from pathlib import Path
import pandas as pd
from data_pipeline.ingestion.base import PartnerDataSource
class JsonFileSource(PartnerDataSource):
    """Mock/local adapter; add source-specific adapters beside it."""
    def read(self,location:Path)->pd.DataFrame: return pd.read_json(location)
