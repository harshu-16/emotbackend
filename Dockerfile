# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install required system packages
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose a port (adjust if needed)
EXPOSE 5000

# Run your app (change to your actual start command)
CMD ["python", "app.py"]
