import os
import httpx
import xml.etree.ElementTree as ET
from typing import List
from urllib.parse import urlparse

from fastapi import HTTPException
from playwright.async_api import async_playwright


class PagesService:
    async def get_page_html(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            content = await page.content()
            await browser.close()
        return content

    async def generate_pages(self, sitemap_url: str):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(sitemap_url)
                xml_data = response.text
        except httpx.ConnectTimeout:
            msg = f"Ошибка: не удалось подключиться к {sitemap_url} в отведённое время."
            print(msg)
            raise HTTPException(status_code=504, detail=msg)

        urls = self.parse_urls(xml_data)
        if not urls:
            msg = "Список URL пуст. Проверьте XML карту сайта."
            print(msg)
            raise HTTPException(status_code=404, detail=msg)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            for url in urls:
                try:
                    page = await context.new_page()
                    await page.goto(url, wait_until="networkidle")
                    content = await page.content()
                    file_path = self._generate_output_path(url)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Сохранено: {file_path}")
                except Exception as e:
                    msg = f"Ошибка при обработке {url}: {e}"
                    print(msg)
                    raise HTTPException(status_code=500, detail=msg)
                finally:
                    await page.close()

            await browser.close()

    def parse_urls(self, xml_string: str) -> List[str]:
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        root = ET.fromstring(xml_string)
        urls = []
        for url_elem in root.findall('ns:url', ns):
            loc_elem = url_elem.find('ns:loc', ns)
            if loc_elem is not None and loc_elem.text:
                url_text = loc_elem.text.strip()
                if url_text:
                    urls.append(url_text)
        return urls

    def _generate_output_path(self, url: str) -> str:
        parsed = urlparse(url)
        domain = parsed.netloc.replace('.', '')
        parts = [part for part in parsed.path.split('/') if part]
        if not parts:
            filename = "index.html"
            directory = os.path.join("src", "static", domain)
        else:
            filename = parts[-1]
            if not os.path.splitext(filename)[1]:
                filename += ".html"
            directory = os.path.join("src", "static", domain, *parts[:-1])
        return os.path.join(directory, filename)
