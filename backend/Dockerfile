FROM python:3.12-slim

WORKDIR /app

# Install curl for health checks and network debugging
RUN apt-get update && \
    apt-get install -y curl iputils-ping net-tools && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default environment (can be overridden at runtime)
ENV PYTHONUNBUFFERED=1
ENV MAUEKSPOR_AI_MODE=localhost
ENV MAUEKSPOR_AI_BASE_URL=http://host.docker.internal:20128/v1

# Start uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
