import os

class Config:
    """Configuración para el servidor de procesamiento multi-PI - UI, almacenamiento y lógica de negocio"""
    
    # ================= CONFIGURACIÓN MANUAL (Usuario) =================
    
    # Raspberry Pi hostnames/IPs - CONFIGURAR AQUÍ TUS PIs
    RASPBERRY_PI_HOSTNAMES = {
        "pi1": "localhost",  # Reemplazar con el hostname/IP real de la Raspberry Pi 1
    }
    
    # Detección de objetos (para validación)
    DETECTION_SCORE_THRESHOLD = 0.3
    DETECTION_MAX_RESULTS = 3
    DETECTION_CATEGORY_ALLOWLIST = ["person", "bicycle"]
    
    # Zona segura (x1, y1, x2, y2)
    SAFE_ZONE_START = (0, 0)
    SAFE_ZONE_END = (480, 720)
    
    # Grabación de eventos
    MIN_VIDEO_DURATION = 1  # segundos mínimos para guardar video
    MAX_VIDEO_DURATION = 3  # segundos máximos por video
    MAX_DETECTION_DELAY = 2  # segundos sin detección para finalizar grabación
    EVENT_CHECK_INTERVAL = 12  # cada cuantos eventos verificar almacenamiento
    
    # Almacenamiento temporal (se borra al reiniciar contenedor)
    STORAGE_CAPACITY_GB = 3  # capacidad máxima en GB
    EVENTS_FOLDER = "/tmp/events"  # Carpeta temporal
    LOGS_FOLDER = "/tmp/logs"  # Logs temporales
    
    # ================= CONFIGURACIÓN AUTOMÁTICA (Sistema) =================
    
    # Video
    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720
    TARGET_FPS = 24
    
    # Streaming
    STREAM_FPS = 30
    STREAM_QUALITY = 85  # Calidad JPEG para streaming
    
    # Timeouts de red automáticos basados en contenedores
    @staticmethod
    def get_network_timeout():
        """Timeout de red optimizado para contenedores"""
        return 10.0 if os.getenv("DOCKER_CONTAINER") else 15.0
    
    @staticmethod
    def get_retry_delay():
        """Delay de reintento optimizado para contenedores"""
        return 1.0 if os.getenv("DOCKER_CONTAINER") else 2.0
    
    # Métodos para obtener información de PIs específicas
    @classmethod
    def get_pi_hostname(cls, pi_id):
        """Obtiene el hostname/IP de una PI específica"""
        return cls.RASPBERRY_PI_HOSTNAMES.get(pi_id)
    
    @classmethod
    def get_pi_url(cls, pi_id, port=8080):
        """Retorna la URL completa de una PI específica"""
        hostname = cls.get_pi_hostname(pi_id)
        if hostname:
            return f"http://{hostname}:{port}"
        return None
    
    @classmethod
    def get_all_pi_ids(cls):
        """Retorna lista de todos los IDs de PIs configuradas"""
        return list(cls.RASPBERRY_PI_HOSTNAMES.keys())
    
    @classmethod
    def validate_config(cls):
        """Valida la configuración antes de iniciar el sistema"""
        # Validar que hay al menos una PI configurada
        if not cls.RASPBERRY_PI_HOSTNAMES:
            raise ValueError("Debe configurar al menos una Raspberry Pi en RASPBERRY_PI_HOSTNAMES")
        
        # Validar IDs de PI (solo caracteres alfanuméricos y guiones bajos)
        import re
        pi_id_pattern = re.compile(r'^[a-zA-Z0-9_]+$')
        for pi_id in cls.RASPBERRY_PI_HOSTNAMES.keys():
            if not pi_id_pattern.match(pi_id):
                raise ValueError(f"PI ID '{pi_id}' contiene caracteres inválidos. Use solo letras, números y guiones bajos.")
        
        # Validar zona segura
        if cls.SAFE_ZONE_START[0] >= cls.SAFE_ZONE_END[0]:
            raise ValueError("SAFE_ZONE_START x debe ser menor que SAFE_ZONE_END x")
        if cls.SAFE_ZONE_START[1] >= cls.SAFE_ZONE_END[1]:
            raise ValueError("SAFE_ZONE_START y debe ser menor que SAFE_ZONE_END y")
        
        # Validar duración de videos
        if cls.MIN_VIDEO_DURATION >= cls.MAX_VIDEO_DURATION:
            raise ValueError("MIN_VIDEO_DURATION debe ser menor que MAX_VIDEO_DURATION")
        
        # Validar threshold de detección
        if cls.DETECTION_SCORE_THRESHOLD < 0 or cls.DETECTION_SCORE_THRESHOLD > 1:
            raise ValueError("DETECTION_SCORE_THRESHOLD debe estar entre 0 y 1")
        
        # Validar capacidad de almacenamiento
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
        
        # Crear carpetas individuales para cada PI
        for pi_id in cls.RASPBERRY_PI_HOSTNAMES.keys():
            pi_folder = os.path.join(cls.EVENTS_FOLDER, pi_id)
            os.makedirs(pi_folder, exist_ok=True)
        
        return True