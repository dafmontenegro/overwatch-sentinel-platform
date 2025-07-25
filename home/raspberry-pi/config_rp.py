import os
import multiprocessing

class Config:

    # Modelo de detección
    MODEL_NAME = "efficientdet_lite0.tflite"

    # Threads automáticos basados en CPU
    NUM_THREADS = multiprocessing.cpu_count()
    
    # Detección de objetos
    DETECTION_MAX_RESULTS = 3
    DETECTION_SCORE_THRESHOLD = 0.5
    DETECTION_CATEGORY_ALLOWLIST = ["person", "bicycle"]    

    # Cámara
    CAMERA_NUMBER = 0

    # Video
    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720
    TARGET_FPS = 24

    # Video de respaldo y para pruebas
    FALLBACK_VIDEO = "test.mp4"

    # Configuración de procesamiento - usar variable de entorno si está disponible
    PROCESSING_SERVER_HOSTNAME = os.getenv("PROCESSING_SERVER_HOSTNAME", "http://localhost:8080")

    # Streaming
    STREAM_QUALITY = 70  # Calidad JPEG para streaming
    
    # Logging
    LOG_FILE_PATH = "pi_detector.log"