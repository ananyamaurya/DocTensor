FROM python:3.11-slim

# Install system dependencies (OpenCV, etc.)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy application source
COPY pyproject.toml .
COPY src/ ./src/

# Install the core and api dependencies
RUN pip install .[api,ocr]

# Re-install in editable mode so src is linked correctly
RUN pip install -e .[api,ocr]

# Create local storage directory
RUN mkdir -p /app/tmp_uploads

ENV PYTHONPATH=/app/src
ENV STORAGE_ROOT=/app/tmp_uploads

EXPOSE 8000
CMD ["uvicorn", "doctensor.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
