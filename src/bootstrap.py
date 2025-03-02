from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import lru_cache

from aiojobs import Scheduler
from fastapi import FastAPI

from src.services.tasks import generate_sitemap_pages, run_task
from src.settings import get_settings
from src.transport import rest


@asynccontextmanager
async def _lifespan(
    app: FastAPI,  # noqa
) -> AsyncGenerator[None]:

    scheduler = Scheduler(limit=1, wait_timeout=5, pending_limit=1)
    await scheduler.spawn(run_task(task=generate_sitemap_pages, delay_seconds=10))

    yield


    await scheduler.close()


@lru_cache
def make_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        lifespan=_lifespan,
        redoc_url=None,
    )

    rest.init_api_routes(app=app)

    return app
