import contextlib
import httpx
import json
import datetime

import xmltodict
from fastapi import HTTPException
from playwright.async_api import async_playwright

from src.services.models import Sitemap
from src.services.utils import parse_page, generate_output_path, read_metadata
from src.settings import get_settings


class PagesService:
    async def get_page_html(self, url: str) -> str:
        metadata = read_metadata()

        if html_metadata := metadata.get(url):
            with open(html_metadata['path'], "r", encoding="utf-8") as f:
                html: str = f.read()
            return html

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            content = await parse_page(context, url)

            if get_settings().env.not_found_tag in content:
                raise HTTPException(status_code=404)

            return content

    async def generate_pages(self, sitemap_url: str):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.get(sitemap_url)
                xml_data = response.text
        except Exception as e:
            msg = f"Ошибка при запросе {sitemap_url}: {e}"
            raise HTTPException(status_code=500, detail=msg)

        sitemap = Sitemap.model_validate(xmltodict.parse(xml_data)['urlset'])
        if not sitemap:
            msg = "Список URL пуст. Проверьте XML карту сайта."
            raise HTTPException(status_code=404, detail=msg)

        metadata = read_metadata()

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            for url_data in sitemap.urls:
                file_path = generate_output_path(url_data.loc)

                if url_data.loc in metadata and url_data.lastmod:
                    with contextlib.suppress(Exception):
                        last_fetched_dt = datetime.datetime.fromisoformat(metadata[url_data.loc]["last_fetched"])
                        if url_data.lastmod <= last_fetched_dt:
                            print(f"Пропуск {url_data.loc} по дате")
                            continue

                content = await parse_page(context, url_data.loc)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with file_path.open("w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Сохранено: {file_path}")

                metadata[url_data.loc] = {
                    "last_fetched": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "path": file_path.as_posix()
                }

        with get_settings().metadata_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
        print(f"Метаданные сохранены: {get_settings().metadata_path}")
