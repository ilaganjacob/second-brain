from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Reads api/.env (and real environment variables, which win)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-haiku-5.5"
    database_path: str = "second-brain.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
