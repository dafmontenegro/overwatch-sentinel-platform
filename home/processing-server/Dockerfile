FROM python:3.9-bookworm

# Install necessary libraries and tzdata for timezone configuration
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1-mesa-glx libstdc++6 tzdata ffmpeg\
    && rm -rf /var/lib/apt/lists/*

# Configure timezone data
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

WORKDIR /app

# Copy project files
COPY . .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Create directories for events and logs
RUN mkdir -p /app/events /app/logs

CMD ["python", "processing_server.py"]