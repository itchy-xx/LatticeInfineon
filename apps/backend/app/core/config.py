from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./lattice-local.db"
    cors_origins: str = "http://localhost:5173"
    mock_data_path: str = "../../data/mock/supply_chain_events.mock.json"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @property
    def cors_origin_list(self) -> list[str]: return [x.strip() for x in self.cors_origins.split(",")]

@lru_cache
def get_settings() -> Settings: return Settings()
settings = get_settings()
