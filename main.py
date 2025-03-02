
from src.settings import Settings  # noqa
import uvicorn

from src.bootstrap import make_app  # noqa


def main() -> None:
    settings = Settings()
    uvicorn.run(
        app=make_app,
        host=settings.env.rest.host,
        port=settings.env.rest.port,
        factory=True,
        lifespan='on'
    )


if __name__ == '__main__':
    main()
