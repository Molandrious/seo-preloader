from fastapi import APIRouter
from starlette.responses import HTMLResponse

from src.services.pages import PagesService

router = APIRouter(
    prefix='/render',
    tags=['Render']
)


@router.get('/{url:path}', response_class=HTMLResponse)
async def get_page_html(url: str):
    render_data =  await PagesService.get_page_html(url=url)
    return HTMLResponse(content=render_data.content, status_code=render_data.status_code)
