# Stage 1: Build Frontend
FROM node:18 AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Backend & Serve
FROM python:3.11-slim

# Install system dependencies (ffmpeg is required for video editing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Copy the built frontend dist from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port for FastAPI
EXPOSE 8000

# Command to run the application (Uses PORT from Render if available)
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
