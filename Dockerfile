FROM python:3.12-slim

# Install system dependencies (only fonts needed now)
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY .python-version ./
COPY wallofx/ ./wallofx/
COPY run.py ./

# Install dependencies using uv
RUN uv sync --frozen

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create output directory
RUN mkdir -p wallofx/static/output

# Run the application
CMD ["uv", "run", "run.py"]
