import cv2
import time
import base64
import socket
import logging
import requests
import ipaddress
import threading
from tflite_support.task import core
from tflite_support.task import vision
from tflite_support.task import processor
from flask import Flask, Response, jsonify, request, abort
from flask_cors import CORS
from config_rp import Config


class SecurityMiddleware:
    """Middleware para validar IPs y hostnames autorizados"""
    
    @staticmethod
    def resolve_hostname_to_ip(hostname):
        """Resuelve un hostname a su IP correspondiente"""
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            logging.warning(f"Could not resolve hostname: {hostname}")
            return None
    
    @staticmethod
    def get_all_allowed_ips(allowed_list):
        """Convierte lista de IPs y hostnames a lista de IPs válidas"""
        allowed_ips = []
        
        for item in allowed_list:
            # Si es una IP directa
            try:
                ipaddress.ip_address(item)
                allowed_ips.append(item)
                continue
            except ValueError:
                pass
            
            # Si es un hostname, intentar resolverlo
            resolved_ip = SecurityMiddleware.resolve_hostname_to_ip(item)
            if resolved_ip:
                allowed_ips.append(resolved_ip)
                logging.info(f"Resolved {item} -> {resolved_ip}")
        
        return allowed_ips
    
    @staticmethod
    def is_raspberry_allowed(client_ip):
        """Verifica si la IP es de la Raspberry Pi autorizada"""
        try:
            client_addr = ipaddress.ip_address(client_ip)
            allowed_ips = SecurityMiddleware.get_all_allowed_ips(Config.ALLOWED_RASPBERRY_IPS)
            
            for allowed_ip in allowed_ips:
                if client_addr == ipaddress.ip_address(allowed_ip):
                    return True
            return False
        except ValueError:
            return False
    
    @staticmethod
    def is_client_allowed(client_ip):
        """Verifica si la IP es de un cliente autorizado para ver contenido"""
        try:
            client_addr = ipaddress.ip_address(client_ip)
            allowed_ips = SecurityMiddleware.get_all_allowed_ips(Config.ALLOWED_CLIENT_IPS)
            
            for allowed_ip in allowed_ips:
                if client_addr == ipaddress.ip_address(allowed_ip):
                    return True
            return False
        except ValueError:
            return False
    
    @staticmethod
    def is_processing_server_allowed(client_ip):
        """Verifica si la IP es del servidor de procesamiento autorizado"""
        try:
            client_addr = ipaddress.ip_address(client_ip)
            allowed_ips = SecurityMiddleware.get_all_allowed_ips(Config.ALLOWED_PROCESSING_SERVER_IPS)
            
            for allowed_ip in allowed_ips:
                if client_addr == ipaddress.ip_address(allowed_ip):
                    return True
            return False
        except ValueError:
            return False
        
    @staticmethod
    def is_admin_allowed(client_ip):
        """Verifica si la IP es de un administrador autorizado"""
        try:
            client_addr = ipaddress.ip_address(client_ip)
            allowed_ips = SecurityMiddleware.get_all_allowed_ips(Config.ALLOWED_ADMIN_IPS)
            
            for allowed_ip in allowed_ips:
                if client_addr == ipaddress.ip_address(allowed_ip):
                    return True
            return False
        except ValueError:
            return False


class ObjectDetector:
    def __init__(self):
        base_options = core.BaseOptions(
            file_name=Config.MODEL_NAME, 
            use_coral=False, 
            num_threads=Config.get_num_threads()
        )
        detection_options = processor.DetectionOptions(
            max_results=Config.DETECTION_MAX_RESULTS,
            score_threshold=Config.DETECTION_SCORE_THRESHOLD,
            category_name_allowlist=Config.DETECTION_CATEGORY_ALLOWLIST
        )
        options = vision.ObjectDetectorOptions(
            base_options=base_options,
            detection_options=detection_options
        )
        self.detector = vision.ObjectDetector.create_from_options(options)

    def detections(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return self.detector.detect(vision.TensorImage.create_from_array(rgb_image)).detections


class VideoFrameProvider:
    """Proveedor de frames optimizado para video de prueba"""
    
    def __init__(self):
        self.frames = []
        self.current_frame_index = 0
        self.last_frame_time = time.time()
        self.target_fps = Config.TARGET_FPS
        self.frame_delay = 1.0 / self.target_fps
        self.is_loaded = False
        
    def load_test_video(self, video_path):
        """Carga todos los frames del video de prueba en memoria de forma optimizada"""
        if self.is_loaded:
            return True
            
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logging.error(f"Cannot open test video: {video_path}")
                return False
                
            logging.info(f"Loading test video frames from {video_path}...")
            
            # Obtener información del video
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            
            logging.info(f"Video info: {total_frames} frames at {video_fps} FPS")
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Redimensionar frame si es necesario
                if frame.shape[1] != Config.FRAME_WIDTH or frame.shape[0] != Config.FRAME_HEIGHT:
                    frame = cv2.resize(frame, (Config.FRAME_WIDTH, Config.FRAME_HEIGHT))
                
                self.frames.append(frame)
                frame_count += 1
                
                # Log progreso cada 100 frames
                if frame_count % 100 == 0:
                    logging.info(f"Loaded {frame_count}/{total_frames} frames")
                
            cap.release()
            self.is_loaded = True
            
            logging.info(f"Successfully loaded {len(self.frames)} frames from test video")
            return True
            
        except Exception as e:
            logging.error(f"Error loading test video: {e}")
            return False
    
    def get_next_frame(self):
        """Obtiene el siguiente frame del video de prueba con control de FPS preciso"""
        if not self.frames:
            return None
            
        # Control de FPS más preciso
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        
        if elapsed < self.frame_delay:
            time.sleep(self.frame_delay - elapsed)
            
        # Obtener frame actual (copia para evitar modificaciones)
        frame = self.frames[self.current_frame_index].copy()
        
        # Avanzar al siguiente frame (loop infinito)
        self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
        self.last_frame_time = time.time()
        
        return frame
    
    def get_total_frames(self):
        """Retorna el número total de frames cargados"""
        return len(self.frames)


class Camera:
    def __init__(self):
        self.use_fallback = False
        self.video_capture = None
        self.video_provider = VideoFrameProvider()
        
        # Intentar abrir cámara real primero
        try:
            self.video_capture = cv2.VideoCapture(Config.CAMERA_NUMBER)
            
            if not self.video_capture.isOpened():
                raise RuntimeError("Camera not available")
                
            # Configurar cámara real
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, Config.FRAME_WIDTH)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)
            self.video_capture.set(cv2.CAP_PROP_FPS, Config.TARGET_FPS)
            
            # Probar captura de un frame
            ret, test_frame = self.video_capture.read()
            if not ret:
                raise RuntimeError("Cannot read from camera")
                
            logging.info("Successfully initialized real camera")
            
        except Exception as e:
            logging.warning(f"Camera initialization failed: {e}")
            logging.info("Falling back to test video")
            
            if self.video_capture:
                self.video_capture.release()
                self.video_capture = None
                
            self.use_fallback = True
            
            # Cargar video de prueba
            if not self.video_provider.load_test_video(Config.FALLBACK_VIDEO):
                raise RuntimeError("Cannot initialize camera or load fallback video")
                
            logging.info(f"Fallback video loaded with {self.video_provider.get_total_frames()} frames")

    def frame(self):
        """Obtiene el siguiente frame de la cámara o video de prueba"""
        if self.use_fallback:
            return self.video_provider.get_next_frame()
        else:
            success, frame = self.video_capture.read()
            if success:
                # Redimensionar si es necesario
                if frame.shape[1] != Config.FRAME_WIDTH or frame.shape[0] != Config.FRAME_HEIGHT:
                    frame = cv2.resize(frame, (Config.FRAME_WIDTH, Config.FRAME_HEIGHT))
                return frame
            return None

    def isOpened(self):
        """Verifica si la cámara o video está disponible"""
        if self.use_fallback:
            return len(self.video_provider.frames) > 0
        else:
            return self.video_capture and self.video_capture.isOpened()

    def release(self):
        """Libera recursos de la cámara"""
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None


class RaspberryPiDetector:
    def __init__(self):
        Config.validate_config()
        
        self.camera = Camera()
        self.object_detector = ObjectDetector()
        self.processing_server_url = Config.get_processing_server_url()
        self.current_frame = None
        self.running = True
        
        # Estadísticas de rendimiento
        self.frame_times = []
        self.fps = Config.TARGET_FPS
        self.frames_processed = 0
        self.start_time = time.time()
        
        logging.info(f"Raspberry Pi Detector initialized")
        logging.info(f"Using {Config.get_num_threads()} threads for detection")
        logging.info(f"Processing server: {self.processing_server_url}")
        logging.info(f"Camera fallback mode: {self.camera.use_fallback}")
        logging.info(f"Target FPS: {Config.TARGET_FPS}")

    def capture_and_detect(self):
        """Captura frames y detecta objetos, enviando datos al servidor de procesamiento"""
        try:
            while self.running and self.camera.isOpened():
                frame_start_time = time.time()
                frame = self.camera.frame()
                
                if frame is None:
                    logging.warning("Failed to capture frame")
                    time.sleep(0.1)
                    continue
                
                self.current_frame = frame
                time_localtime = time.localtime()
                
                # Detectar objetos
                detections = self.object_detector.detections(frame)
                
                # Convertir detecciones a formato JSON
                detection_data = []
                for detection in detections:
                    box = detection.bounding_box
                    detection_data.append({
                        "bbox": {
                            "x": box.origin_x,
                            "y": box.origin_y,
                            "width": box.width,
                            "height": box.height
                        },
                        "category": detection.categories[0].category_name,
                        "score": detection.categories[0].score
                    })
                
                # Codificar frame en base64
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, Config.STREAM_QUALITY])
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Calcular FPS
                frame_time = time.time() - frame_start_time
                self.frame_times.append(frame_time)
                
                if len(self.frame_times) >= Config.FPS_CALCULATION_FRAMES:
                    average_frame_time = sum(self.frame_times) / len(self.frame_times)
                    self.fps = round(1/average_frame_time, 2)
                    self.frame_times = []
                
                # Preparar datos para envío
                data = {
                    "frame": frame_base64,
                    "detections": detection_data,
                    "timestamp": time.strftime("%B%d/%Y %H:%M:%S", time_localtime),
                    "fps": self.fps,
                    "frame_width": Config.FRAME_WIDTH,
                    "frame_height": Config.FRAME_HEIGHT,
                    "detections_count": len(detection_data)
                }
                
                # Enviar datos al servidor de procesamiento
                try:
                    response = requests.post(
                        f"{self.processing_server_url}/process_frame",
                        json=data,
                        timeout=Config.get_network_timeout()
                    )
                    
                    if response.status_code == 200:
                        self.frames_processed += 1
                    else:
                        logging.warning(f"Processing server responded with status {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    logging.error(f"Error sending data to processing server: {e}")
                    time.sleep(Config.get_retry_delay())
                
                # Control de FPS para no saturar el procesador
                elapsed = time.time() - frame_start_time
                target_frame_time = 1.0 / Config.TARGET_FPS
                if elapsed < target_frame_time:
                    time.sleep(target_frame_time - elapsed)
                
        except Exception as e:
            logging.error(f"Error in capture_and_detect: {e}", exc_info=True)
        finally:
            self.camera.release()

    def get_current_frame(self):
        """Retorna el frame actual para stream directo"""
        return self.current_frame

    def get_stats(self):
        """Retorna estadísticas del detector"""
        uptime = time.time() - self.start_time
        return {
            "fps": self.fps,
            "frames_processed": self.frames_processed,
            "uptime_seconds": round(uptime, 2),
            "camera_fallback": self.camera.use_fallback,
            "detection_threads": Config.get_num_threads()
        }

    def stop(self):
        """Detiene el detector"""
        self.running = False
        self.camera.release()


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%B%d/%Y %H:%M:%S"
    )

    try:
        # Crear detector
        detector = RaspberryPiDetector()

        # Iniciar captura en un hilo separado
        capture_thread = threading.Thread(target=detector.capture_and_detect)
        capture_thread.daemon = True
        capture_thread.start()

        # Iniciar servidor Flask
        app = Flask(__name__)
        CORS(app)

        # Agregar validación antes de cada request
        @app.before_request
        def validate_ip():
            client_ip = request.remote_addr

            # Endpoints administrativos (stream, status)
            admin_endpoints = ['raw_stream', 'status', 'index']
            
            if request.endpoint in admin_endpoints:
                if not SecurityMiddleware.is_admin_allowed(client_ip):
                    logging.warning(f"Unauthorized admin access attempt from: {client_ip}")
                    abort(403)

        @app.route("/")
        def index():
            return jsonify({
                "status": "running",
                "service": "raspberry-pi-detector",
                "processing_server": Config.get_processing_server_url(),
                "camera_fallback": detector.camera.use_fallback,
                "config": {
                    "target_fps": Config.TARGET_FPS,
                    "detection_threads": Config.get_num_threads(),
                    "frame_resolution": f"{Config.FRAME_WIDTH}x{Config.FRAME_HEIGHT}"
                }
            })

        @app.route("/status")
        def status():
            stats = detector.get_stats()
            return jsonify({
                "camera_opened": detector.camera.isOpened(),
                "processing_server": Config.get_processing_server_url(),
                **stats
            })

        @app.route("/raw_stream")
        def raw_stream():
            """Stream de video directo desde la cámara (solo para debugging)"""
            def generate():
                while True:
                    frame = detector.get_current_frame()
                    if frame is not None:
                        # Añadir información de debugging
                        cv2.putText(frame, f"RAW FEED - FPS: {detector.fps}", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        cv2.putText(frame, f"Threads: {Config.get_num_threads()}", 
                                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, Config.STREAM_QUALITY])
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    
                    time.sleep(1.0 / Config.STREAM_FPS)
            
            return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

        logging.info("Starting Raspberry Pi detector service on port 8080")
        app.run(host="0.0.0.0", port=8080, threaded=True)

    except Exception as e:
        logging.error(f"Error starting service: {e}", exc_info=True)
        if 'detector' in locals():
            detector.stop()
    finally:
        if 'detector' in locals():
            detector.stop()