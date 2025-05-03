# 1. Base image
FROM python:3.11-slim

# 2. Install system deps for PyAudio + ffmpeg
RUN apt-get update && apt-get install -y \
    gcc \
    libasound-dev \
    portaudio19-dev \
    libportaudio2 \
    libportaudiocpp0 \
    ffmpeg \
  && rm -rf /var/lib/apt/lists/*

# 3. Set working directory
WORKDIR /app

# 4. Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your code
COPY . .

# 6. Launch your server
CMD ["python", "simple_api.py"]
