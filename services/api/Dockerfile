# Builder Phase
FROM python:3.12-slim AS builder
RUN pip install --no-cache-dir poetry==1.8.2
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

# Runtime Phase
FROM python:3.12-slim AS runtime  
RUN useradd --create-home app
USER app
COPY --from=builder /app/.venv /app/.venv
COPY src /app/src
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1 
ENV PYTHONDONTWRITEBYTECODE=1
EXPOSE 8000
CMD ["uvicorn", "ask_my_docs.api.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
