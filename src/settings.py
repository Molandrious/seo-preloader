from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, DirectoryPath, Field, FilePath
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
    host: str = Field(default='0.0.0.0')
    port: int = Field(default=3000)

class EnvSettings(_BaseSettings):
    rest: RESTSettings = RESTSettings(_env_prefix='REST_') # noqa
    generation_delay_seconds: int = Field(default=24*3600)
    sitemap_list: list[str] = Field()
    not_found_tag: str = Field(default='<meta name="ssr" content="404" data-react-helmet="true">')

class Settings(BaseModel):
    env: EnvSettings = EnvSettings()
    root_path: DirectoryPath = Path(__file__).parent.parent.resolve()
    static_path: DirectoryPath = root_path.joinpath("src", "static")
    metadata_path: FilePath = static_path.joinpath("pages_metadata.json")


@lru_cache
def get_settings() -> Settings:
    return Settings()
