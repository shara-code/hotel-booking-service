FROM python:3.10-slim

RUN curl -sSL https://github.com/astral-sh/uv/releases/download/v0.1.1/uv-x86_64-unknown-linux-gnu.tar.gz | tar -xz -C /usr/local/bin/
RUN chmod +x /usr/local/bin/uv

WORKDIR /app

RUN uv venv .venv

COPY src/ .

RUN uv sync

RUN ./.venv/bin/python manage.py migrate

CMD ["./.venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]