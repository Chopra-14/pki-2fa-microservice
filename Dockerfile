# ============================
# Stage 1: Builder
# ============================
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies (if needed for cryptography, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# ============================
# Stage 2: Runtime
# ============================
FROM python:3.11-slim AS runtime

# Set timezone to UTC
ENV TZ=UTC

# Set working directory
WORKDIR /app

# Install system dependencies: cron + tzdata
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Configure timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . /app

# Create volume mount points for persistent storage
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Copy cron configuration file into /etc/cron.d
# (Make sure cron/2fa-cron exists in your repo and has LF line endings)
COPY cron/2fa-cron /etc/cron.d/2fa-cron

# Set correct permissions and register cron job
RUN chmod 0644 /etc/cron.d/2fa-cron \
    && crontab /etc/cron.d/2fa-cron

# Expose API port
EXPOSE 8080

# Start cron daemon and FastAPI app via uvicorn
CMD ["sh", "-c", "cron && uvicorn app.main:app --host 0.0.0.0 --port 8080"]
