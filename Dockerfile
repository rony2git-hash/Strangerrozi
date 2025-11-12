# Use an official lightweight Python runtime
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Prevent Python from writing .pyc files and enable stdout/stderr flushing
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies needed by some libs (e.g., cryptography, ffmpeg optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app code
COPY . /app

# Create a non-root user (recommended)
RUN useradd --create-home appuser
USER appuser
WORKDIR /home/appuser

# Expose (not required for worker, but harmless)
EXPOSE 8080

# Default command — run main.py
# We're running polling so start the script directly.
CMD ["python", "/app/main.py"]
