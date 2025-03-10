FROM python:3.12-slim

ENV PYTHONPATH /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src src

RUN uv sync --frozen --no-cache
RUN uv run playwright install chromium
RUN uv run playwright install-deps

CMD ["uv", "run", "src/main.py"]



