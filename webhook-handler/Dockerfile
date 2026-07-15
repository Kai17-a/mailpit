FROM ghcr.io/astral-sh/uv:python3.14-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-install-project

COPY app.py .

CMD ["fastapi", "run", "app.py", "--host", "0.0.0.0", "--port", "8080"]
