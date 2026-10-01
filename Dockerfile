# ==========================================
# Multi-Stage Build: Enterprise RAG
# ==========================================

# 1. Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# 2. Production Python Backend
FROM python:3.11-slim AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8008

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy compiled React frontend into backend dist path
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Initialize samples and sample PDF
RUN python -m backend.data.samples.generate_sample_pdf || true

EXPOSE 8008

# Start FastAPI serving both API and Frontend
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8008}"]
