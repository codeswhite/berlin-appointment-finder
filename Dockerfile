# syntax=docker/dockerfile:1

# --- Build stage ---
FROM python:3.13-slim AS build
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --user -r requirements.txt

# --- Runtime stage ---
FROM python:3.13-slim AS runtime
WORKDIR /app
COPY --from=build /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .

# Use .env if present
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src"]
