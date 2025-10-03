# ---------------------------
# Step 1: Base Image
# ---------------------------
FROM python:3.11-slim

# ---------------------------
# Step 2: Environment Settings
# ---------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---------------------------
# Step 3: System Dependencies
# ---------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libmagic1 \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------
# Step 4: Set Working Directory
# ---------------------------
WORKDIR /app

# ---------------------------
# Step 5: Copy & Install Python Dependencies
# ---------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------
# Step 6: Copy Project Files
# ---------------------------
COPY app ./app
COPY run.py .
COPY tool_classifier.h5 .

# ---------------------------
# Step 7: Expose Backend Port
# ---------------------------
EXPOSE 5000

# ---------------------------
# Step 8: Run Backend
# ---------------------------
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]
