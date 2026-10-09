from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/.env, found from this file so it works whatever the current working directory is.
_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    """Read from the ``.env`` file in the project root; real environment variables take precedence."""

    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    database_url: str
    database_echo: bool = False
