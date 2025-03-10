import asyncio
from collections.abc import Callable

from src.services.pages import PagesService
from src.settings import get_settings


async def run_task(task: Callable, delay_seconds: int):
    while True:
        await task()
        await asyncio.sleep(delay_seconds)


async def generate_sitemap_pages():
    for sitemap in get_settings().env.sitemap_list:
        await PagesService.generate_pages(sitemap)
