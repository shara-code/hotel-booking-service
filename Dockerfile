FROM python:3.12-slim

RUN pip install uv

WORKDIR /app
COPY . /app

ENV PYTHONPATH=/app/src:$PYTHONPATH

RUN uv sync

CMD ["/app/.venv/bin/gunicorn", "--workers", "1", "--bind", "0.0.0.0:8000", "src.bookingsite.wsgi:application"]