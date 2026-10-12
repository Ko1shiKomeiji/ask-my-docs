from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BeforeValidator, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def _lower(v: object) -> object:
    return v.lower() if isinstance(v, str) else v


def _upper(v: object) -> object:
    return v.upper() if isinstance(v, str) else v


Env = Annotated[Literal["local", "test", "prod"], BeforeValidator(_lower)]
LogLevel = Annotated[Literal["INFO", "DEBUG", "WARNING", "ERROR"], BeforeValidator(_upper)]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__", extra="ignore")

    database_url: dfdfSecretStr
    env: Env = "local"
    max_upload_mb: int = Field(default=30, gt=0, lt=50)
    storage_dir: Path = Path("data/uploads")
    log_level: LogLevel = "INFO"
    log_json: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]
