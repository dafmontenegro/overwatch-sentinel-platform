import os

class Config:
    """Configuración para el servidor de procesamiento multi-PI"""
    
    # ================= RASPBERRY PIs CONFIGURADAS =================
    RASPBERRY_PI_IDS = ["pi1", "pi2"]  # Lista de IDs de PIs a procesar
    
    # ================= ZONA SEGURA =================
    # Coordenadas de la zona segura (x1, y1, x2, y2)
    SAFE_ZONE_START = (640, 0)    # Esquina superior izquierda
    SAFE_ZONE_END = (1280, 720)   # Esquina inferior derecha
    
    # ================= GRABACIÓN DE EVENTOS =================
    MIN_VIDEO_DURATION = 2        # segundos mínimos para guardar video
    MAX_VIDEO_DURATION = 10       # segundos máximos por video
    MAX_DETECTION_DELAY = 3       # segundos sin detección para finalizar grabación
    EVENT_CHECK_INTERVAL = 5      # cada cuantos eventos verificar almacenamiento
    
    # ================= ALMACENAMIENTO =================
    STORAGE_CAPACITY_GB = 2       # capacidad máxima en GB
    EVENTS_FOLDER = "events"      # Carpeta para guardar eventos
    
    # ================= VALIDACIÓN =================
    @classmethod
    def validate_config(cls):
        """Valida la configuración antes de iniciar el sistema"""
        # Validar que hay al menos una PI configurada
        if not cls.RASPBERRY_PI_IDS:
            raise ValueError("Debe configurar al menos una Raspberry Pi en RASPBERRY_PI_IDS")
        
        # Validar IDs de PI (solo caracteres alfanuméricos y guiones bajos)
        import re
        pi_id_pattern = re.compile(r'^[a-zA-Z0-9_]+$')
        for pi_id in cls.RASPBERRY_PI_IDS:
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
        
        # Validar capacidad de almacenamiento
        if cls.STORAGE_CAPACITY_GB <= 0:
            raise ValueError("STORAGE_CAPACITY_GB debe ser mayor que 0")
        
        # Validar zona segura dentro del frame (1280x720)
        if cls.SAFE_ZONE_START[0] < 0 or cls.SAFE_ZONE_START[1] < 0:
            raise ValueError("SAFE_ZONE_START debe tener coordenadas positivas")
        if cls.SAFE_ZONE_END[0] > 1280 or cls.SAFE_ZONE_END[1] > 720:
            raise ValueError(f"SAFE_ZONE_END debe estar dentro del frame 1280x720")
        
        # Crear carpeta de eventos
        os.makedirs(cls.EVENTS_FOLDER, exist_ok=True)
        
        # Crear carpetas individuales para cada PI
        for pi_id in cls.RASPBERRY_PI_IDS:
            pi_folder = os.path.join(cls.EVENTS_FOLDER, pi_id)
            os.makedirs(pi_folder, exist_ok=True)
        
        return True