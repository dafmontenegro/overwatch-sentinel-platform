import os

class Config:
    """Configuración para el servidor de procesamiento - UI, almacenamiento y lógica de negocio"""
    
    # ================= CONFIGURACIÓN MANUAL (Usuario) =================
    
    # Detección de objetos (para validación)
    DETECTION_SCORE_THRESHOLD = 0.3
    DETECTION_MAX_RESULTS = 3
    DETECTION_CATEGORY_ALLOWLIST = ["person", "dog"]
    
    # Zona segura (x1, y1, x2, y2)
    SAFE_ZONE_START = (880, 360)
    SAFE_ZONE_END = (1280, 720)
    
    # Grabación de eventos
    MIN_VIDEO_DURATION = 1  # segundos mínimos para guardar video
    MAX_VIDEO_DURATION = 3  # segundos máximos por video
    MAX_DETECTION_DELAY = 2  # segundos sin detección para finalizar grabación
    EVENT_CHECK_INTERVAL = 12  # cada cuantos eventos verificar almacenamiento
    
    # Almacenamiento temporal (se borra al reiniciar contenedor)
    STORAGE_CAPACITY_GB = 3  # capacidad máxima en GB
    EVENTS_FOLDER = "/tmp/events"  # Carpeta temporal
    LOGS_FOLDER = "/tmp/logs"  # Logs temporales
    
    # Seguridad de red - Solo acepta conexiones de IPs específicas
    ALLOWED_RASPBERRY_IPS = ["172.20.0.9"]  # Solo IP del contenedor raspberry
    ALLOWED_CLIENT_IPS = [
        "127.0.0.1", 
        "172.20.0.12",  # IP del propio contenedor
        "host.docker.internal",  # Para acceso desde host Docker
        "192.168.65.1",  # IP típica del host Docker Desktop en Mac
        "192.168.65.254",  # IP del gateway Docker Desktop
        "macbook-air-5-2.local", 
        "MacBook-Air-Montenegro.local"
    ]
    
    # ================= CONFIGURACIÓN AUTOMÁTICA (Sistema) =================
    
    # Video
    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720
    TARGET_FPS = 24
    
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
        return 1.0 if os.getenv("DOCKER_CONTAINER") else 2.0  # Aumentado para evitar spam
    
    # Configuración de red automática
    @staticmethod
    def get_raspberry_pi_host():
        """Obtiene el host de la Raspberry Pi"""
        return os.getenv("RASPBERRY_PI_HOST", "localhost")
    
    @staticmethod
    def get_raspberry_pi_port():
        """Obtiene el puerto de la Raspberry Pi"""
        return int(os.getenv("RASPBERRY_PI_PORT", "8080"))
    
    @classmethod
    def get_raspberry_pi_url(cls):
        """Retorna la URL completa de la Raspberry Pi"""
        return f"http://{cls.get_raspberry_pi_host()}:{cls.get_raspberry_pi_port()}"
    
    @classmethod
    def validate_config(cls):
        """Valida la configuración antes de iniciar el sistema"""
        if cls.SAFE_ZONE_START[0] >= cls.SAFE_ZONE_END[0]:
            raise ValueError("SAFE_ZONE_START x debe ser menor que SAFE_ZONE_END x")
        if cls.SAFE_ZONE_START[1] >= cls.SAFE_ZONE_END[1]:
            raise ValueError("SAFE_ZONE_START y debe ser menor que SAFE_ZONE_END y")
        if cls.MIN_VIDEO_DURATION >= cls.MAX_VIDEO_DURATION:
            raise ValueError("MIN_VIDEO_DURATION debe ser menor que MAX_VIDEO_DURATION")
        if cls.DETECTION_SCORE_THRESHOLD < 0 or cls.DETECTION_SCORE_THRESHOLD > 1:
            raise ValueError("DETECTION_SCORE_THRESHOLD debe estar entre 0 y 1")
        if cls.STORAGE_CAPACITY_GB <= 0:
            raise ValueError("STORAGE_CAPACITY_GB debe ser mayor que 0")
        
        # Validar zona segura dentro del frame
        if cls.SAFE_ZONE_START[0] < 0 or cls.SAFE_ZONE_START[1] < 0:
            raise ValueError("SAFE_ZONE_START debe tener coordenadas positivas")
        if cls.SAFE_ZONE_END[0] > cls.FRAME_WIDTH or cls.SAFE_ZONE_END[1] > cls.FRAME_HEIGHT:
            raise ValueError(f"SAFE_ZONE_END debe estar dentro del frame {cls.FRAME_WIDTH}x{cls.FRAME_HEIGHT}")
        
        # Crear carpetas temporales (se borran al reiniciar contenedor)
        os.makedirs(cls.EVENTS_FOLDER, exist_ok=True)
        os.makedirs(cls.LOGS_FOLDER, exist_ok=True)
        
        return True