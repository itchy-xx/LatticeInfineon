from abc import ABC,abstractmethod
from pathlib import Path
import pandas as pd
class PartnerDataSource(ABC):
    """Read-only source adapter returning raw data unchanged."""
    @abstractmethod
    def read(self,location:Path)->pd.DataFrame: ...
