import uvicorn

from src.bootstrap import make_app  # noqa
from src.settings import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        app=make_app,
        host=settings.env.rest.host,
        port=settings.env.rest.port,
        factory=True,
        lifespan='on'
    )


if __name__ == '__main__':
    main()
