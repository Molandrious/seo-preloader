import json
import os
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

from fastapi import HTTPException
from playwright.async_api import BrowserContext

from src.settings import get_settings


def read_metadata():
    metadata_path = get_settings().metadata_path
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata: Dict[str, Dict[str, str]] = json.load(f)
    except Exception as e:
        print(f"Не удалось загрузить метаданные, будет создан новый файл. Ошибка: {e}")
        metadata = {}

    return metadata


def generate_output_path(url: str) -> Path:
    parsed = urlparse(url)
    domain = parsed.netloc.replace('.', '')
    parts = [part for part in parsed.path.split('/') if part]
    if not parts:
        filename = "index.html"
        directory = get_settings().static_path.joinpath(domain)
    else:
        filename = parts[-1]
        if not os.path.splitext(filename)[1]:
            filename += ".html"
        directory = get_settings().static_path.joinpath(domain, *parts[:-1])
    return directory.joinpath(filename)


async def parse_page(context: BrowserContext, url: str):
    page = await context.new_page()
    try:
        await page.goto(url, timeout=120000, wait_until="networkidle")
        content = await page.content()
    except Exception as e:
        msg = f"Ошибка при обработке {url}: {e}"
        print(msg)
        raise HTTPException(status_code=500, detail=msg)
    finally:
        await page.close()

    return content
