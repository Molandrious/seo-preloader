from datetime import datetime

from pydantic import BaseModel, Field


class SiteMapEntity(BaseModel):
    loc: str
    lastmod: datetime | None


class Sitemap(BaseModel):
    urls: list[SiteMapEntity] = Field(default_factory=list, alias='url')
