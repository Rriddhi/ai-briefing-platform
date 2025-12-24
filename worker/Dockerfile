FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (if needed)
RUN python -m nltk.downloader punkt || true

# Copy application code
COPY . .

# Run the worker
CMD ["python", "run.py", "once"]

