from fastapi import APIRouter

router = APIRouter(
    prefix='/pages',
    tags=['Pages']
)


@router.get('/')
async def get_page_html():
    return 'some_html'
