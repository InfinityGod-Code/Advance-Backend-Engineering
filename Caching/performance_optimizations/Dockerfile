FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Install debugpy for debugging
RUN pip install debugpy

# Copy the rest of the project
COPY . .

EXPOSE 8000

CMD ["uv", "run", "sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]