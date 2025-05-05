# syntax=docker/dockerfile:1

# --- Build stage ---
FROM python:3.13-slim AS build

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

# --- Runtime stage ---
FROM python:3.13-slim AS runtime

# Create non-root user
RUN useradd -m appuser && mkdir /app && chown appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY --from=build /install /usr/local
COPY src src

# Permissions and env
USER appuser
ENV PATH="/usr/local/bin:$PATH" \
    PYTHONUNBUFFERED=1

CMD ["python", "-m", "src"]
