# Use official Python image
FROM python:3.11-slim

# Prevent .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libmagic1 \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy Python dependencies
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/app ./app
COPY backend/run.py .
COPY backend/tool_classifier.h5 .

# Expose the port Render will use
EXPOSE 5000

# Start the server using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]
