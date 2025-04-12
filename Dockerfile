FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock /app/

RUN uv sync --frozen --no-install-project --no-dev

COPY src/. /app/

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["gunicorn", "bookingsite.wsgi:application", "--bind", "0.0.0.0:8000"]