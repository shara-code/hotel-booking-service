FROM python:3.10-slim

RUN apt-get update && apt-get upgrade -y

RUN pip install uv

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

RUN uv venv .venv

COPY . /app

# Sync dependencies with UV
RUN uv sync

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8000
EXPOSE 8000

# Run migrations and start server
CMD ["/bin/sh", "-c", ".venv/bin/python /app/src/manage.py migrate && .venv/bin/python /app/src/manage.py runserver 0.0.0.0:8000"]