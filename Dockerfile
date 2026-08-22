FROM python:3.11-slim

# Install system dependencies (OpenCV, etc.)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Install project dependencies
COPY pyproject.toml .
# Install the core and api dependencies
RUN pip install .[api]

# Copy application source
COPY src/ ./src/
COPY README.md .

# Re-install in editable mode so src is linked correctly
RUN pip install -e .[api]

# Create local storage directory
RUN mkdir -p /app/tmp_uploads

ENV PYTHONPATH=/app/src
ENV STORAGE_ROOT=/app/tmp_uploads

EXPOSE 8000
CMD ["uvicorn", "doctensor.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
