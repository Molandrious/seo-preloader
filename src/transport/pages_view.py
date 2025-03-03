from fastapi import APIRouter
from starlette.responses import HTMLResponse

from src.services.pages import PagesService

router = APIRouter(
    prefix='/pages',
    tags=['Pages']
)


@router.get('/', response_class=HTMLResponse)
async def get_page_html(url: str):
    service = PagesService()
    return await service.get_page_html(url=url)


@router.get('/generate')
async def get_generate_html(url: str):
    service = PagesService()
    await service.generate_pages(sitemap_url=url)