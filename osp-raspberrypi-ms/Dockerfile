FROM python:3.9-bookworm

RUN apt-get update && apt-get install -y \
    curl libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1-mesa-glx libstdc++6 libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar archivos del proyecto
COPY requirements.txt .
COPY pi_tensorflow_lite_object_detection.py .
COPY sample.mp4 .

# Instalar dependencias de Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Descargar modelo TFLite
RUN curl -L https://storage.googleapis.com/download.tensorflow.org/models/tflite/task_library/object_detection/rpi/lite-model_efficientdet_lite0_detection_metadata_1.tflite -o efficientdet_lite0.tflite

CMD ["python", "pi_tensorflow_lite_object_detection.py"]
