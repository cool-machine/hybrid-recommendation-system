# Minimal Dockerfile for Streamlit frontend running in Azure Container Apps (Consumption tier)
# Uses slim Python image to keep size low.
FROM python:3.10-slim AS base

# Install system dependencies
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Install only the Python packages needed by the frontend
# (streamlit, requests, pandas for CSV/parquet reading, etc.)
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y torch tensorflow keras || true  # remove heavy deps not needed by Streamlit UI

# Copy frontend source
COPY . .

# Expose the port Streamlit will listen on
EXPOSE 8501

# Streamlit entrypoint
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true", "--server.enableCORS", "false"]
