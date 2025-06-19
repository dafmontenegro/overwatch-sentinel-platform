FROM python:3.9-bookworm

# Install necessary libraries and tzdata for timezone configuration
RUN apt-get update && apt-get install -y \
    curl libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1-mesa-glx \
    libstdc++6 libusb-1.0-0 tzdata \
    && rm -rf /var/lib/apt/lists/*

# Configure timezone data
ENV TZ=America/Bogota
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download TFLite model
RUN curl -L https://storage.googleapis.com/download.tensorflow.org/models/tflite/task_library/object_detection/rpi/lite-model_efficientdet_lite0_detection_metadata_1.tflite \
    -o efficientdet_lite0.tflite

# Copy application files
COPY raspberry_pi_detector.py .
COPY test.mp4 .

# Create logs directory
RUN mkdir -p /app/logs

# Set default command
CMD ["python", "raspberry_pi_detector.py"]