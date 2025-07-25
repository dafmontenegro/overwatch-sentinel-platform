import os
import multiprocessing

class Config:
    """Configuración para el servicio Raspberry Pi - Detección y captura"""
    
    # ================= CONFIGURACIÓN MANUAL (Usuario) =================
    
    # Detección de objetos
    DETECTION_SCORE_THRESHOLD = 0.5
    DETECTION_MAX_RESULTS = 3
    DETECTION_CATEGORY_ALLOWLIST = ["person", "dog"]

    # Seguridad de red - Solo acepta conexiones del servidor de procesamiento
    ALLOWED_PROCESSING_SERVER_IPS = ["172.20.0.12"]  # Solo IP del contenedor processing
    ALLOWED_ADMIN_IPS = [
        "127.0.0.1",
        "192.168.65.1",  # IP típica del host Docker Desktop en Mac
        "192.168.65.254",  # IP del gateway Docker Desktop
        "host.docker.internal"
    ]
    
    # ================= CONFIGURACIÓN AUTOMÁTICA (Sistema) =================
    
    # Video
    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720
    TARGET_FPS = 12  # REDUCIDO para evitar saturación del processing server
    
    # Modelo de detección
    MODEL_NAME = "efficientdet_lite0.tflite"
    
    # Threads automáticos basados en CPU
    @staticmethod
    def get_num_threads():
        """Calcula el número óptimo de threads basado en la CPU"""
        cpu_count = multiprocessing.cpu_count()
        # Usar la mitad de los cores disponibles, mínimo 2, máximo 8
        return max(2, min(8, cpu_count // 2))
    
    # Cámara
    CAMERA_NUMBER = 0
    FALLBACK_VIDEO = "test.mp4"
    
    # Streaming
    STREAM_FPS = 30
    STREAM_QUALITY = 85  # Calidad JPEG para streaming
    
    # Timeouts de red automáticos basados en contenedores (AUMENTADOS)
    @staticmethod
    def get_network_timeout():
        """Timeout de red optimizado para contenedores"""
        return 10.0 if os.getenv("DOCKER_CONTAINER") else 15.0  # Aumentado significativamente
    
    @staticmethod
    def get_retry_delay():
        """Delay de reintento optimizado para contenedores"""
        return 2.0 if os.getenv("DOCKER_CONTAINER") else 3.0  # Aumentado para evitar spam
    
    # FPS calculation
    FPS_CALCULATION_FRAMES = 30
    
    # Configuración de red automática
    @staticmethod
    def get_processing_server_host():
        """Obtiene el host del servidor de procesamiento"""
        return os.getenv("PROCESSING_SERVER_HOST", "localhost")
    
    @staticmethod
    def get_processing_server_port():
        """Obtiene el puerto del servidor de procesamiento"""
        return int(os.getenv("PROCESSING_SERVER_PORT", "8081"))
    
    @classmethod
    def get_processing_server_url(cls):
        """Retorna la URL completa del servidor de procesamiento"""
        return f"http://{cls.get_processing_server_host()}:{cls.get_processing_server_port()}"
    
    @classmethod
    def validate_config(cls):
        """Valida la configuración antes de iniciar el sistema"""
        if cls.DETECTION_SCORE_THRESHOLD < 0 or cls.DETECTION_SCORE_THRESHOLD > 1:
            raise ValueError("DETECTION_SCORE_THRESHOLD debe estar entre 0 y 1")
        
        # Verificar que el modelo existe
        if not os.path.exists(cls.MODEL_NAME):
            raise FileNotFoundError(f"Modelo de detección no encontrado: {cls.MODEL_NAME}")
        
        # Verificar video de fallback
        if not os.path.exists(cls.FALLBACK_VIDEO):
            raise FileNotFoundError(f"Video de fallback no encontrado: {cls.FALLBACK_VIDEO}")
        
        return True