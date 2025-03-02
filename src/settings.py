from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, DirectoryPath, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _BaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        str_strip_whitespace=True,
        validate_default=True,
        case_sensitive=False,
    )

class RESTSettings(_BaseSettings):
    host: str = Field(default='127.0.0.1')
    port: int = Field(default=8000)

class EnvSettings(_BaseSettings):
    rest: RESTSettings = RESTSettings(_env_prefix='REST_') # noqa
    cron_timer: str = Field(default='0 0 * * *')
    sitemap_list: list[str] = Field()

class Settings(BaseModel):
    env: EnvSettings = EnvSettings()
    root_path: DirectoryPath = Path(__file__).parent.parent.resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
