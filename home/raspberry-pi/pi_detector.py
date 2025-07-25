import cv2
import time
import base64
import logging
import requests
import threading
from tflite_support.task import core
from tflite_support.task import vision
from tflite_support.task import processor
from flask import Flask, jsonify, request
from flask_cors import CORS
from config_rp import Config


class ObjectDetector:
    def __init__(self):
        base_options = core.BaseOptions(
            file_name=Config.MODEL_NAME, 
            use_coral=False, 
            num_threads=Config.NUM_THREADS
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
            ret, _ = self.video_capture.read()
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


class VideoFrameProvider:
    """Proveedor de frames optimizado para video de prueba"""
    
    def __init__(self):
        self.cap = None
        self.target_fps = Config.TARGET_FPS
        self.frame_delay = 1.0 / self.target_fps
        self.last_frame_time = time.time()
        self.is_loaded = False
        
    def load_test_video(self, video_path):
        """Carga el video de prueba sin cargar todos los frames en memoria"""
        try:
            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                logging.error(f"Cannot open test video: {video_path}")
                return False
                
            # Configurar propiedades del video
            self.video_fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Ajustar el delay si el FPS del video es diferente al target
            if self.video_fps > 0 and self.video_fps != self.target_fps:
                self.frame_delay = 1.0 / self.video_fps
                logging.warning(f"Video FPS ({self.video_fps}) differs from target FPS ({self.target_fps}). Using video FPS.")
            
            logging.info(f"Video loaded: {self.total_frames} frames at {self.video_fps} FPS")
            self.is_loaded = True
            return True
            
        except Exception as e:
            logging.error(f"Error loading test video: {e}")
            return False
    
    def get_next_frame(self):
        """Obtiene el siguiente frame del video con control preciso de FPS"""
        if not self.is_loaded or not self.cap:
            return None
            
        # Calcular tiempo hasta el próximo frame
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        sleep_time = max(0, self.frame_delay - elapsed)
        
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        # Leer frame
        ret, frame = self.cap.read()
        
        # Si llegamos al final, reiniciar
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret:
                return None
        
        self.last_frame_time = time.time()
        return frame
    
    def get_total_frames(self):
        """Retorna el número total de frames en el video"""
        return self.total_frames if self.is_loaded else 0


class RaspberryPiDetector:
    def __init__(self):
        self.camera = Camera()
        self.object_detector = ObjectDetector()
        self.processing_server_hostname = Config.PROCESSING_SERVER_HOSTNAME
        self.current_frame = None
        self.running = True
        
        # Estadísticas de rendimiento
        self.frame_times = []
        self.fps = Config.TARGET_FPS
        self.frames_processed = 0
        self.start_time = time.time()
        
        logging.info(f"Raspberry Pi Detector initialized")
        logging.info(f"Using {Config.NUM_THREADS} threads for detection")
        logging.info(f"Processing server: {self.processing_server_hostname}")
        logging.info(f"Camera fallback mode: {self.camera.use_fallback}")
        logging.info(f"Target FPS: {Config.TARGET_FPS}")

    def capture_and_detect(self):
        """Captura frames y detecta objetos, enviando datos al servidor de procesamiento"""
        try:
            while self.running and self.camera.isOpened():
                frame_start_time = time.time()
                frame = self.camera.frame()

                if frame is None:
                    logging.warning("Frame is None, skipping detection cycle.")
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
                
                if len(self.frame_times) >= Config.TARGET_FPS:
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
                        f"{self.processing_server_hostname}/process_frame",
                        timeout=15,
                        json=data
                    )
                    
                    if response.status_code == 200:
                        self.frames_processed += 1
                    else:
                        logging.warning(f"Processing server responded with status {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    logging.error(f"Error sending data to processing server: {e}")
                    time.sleep(3)
                
        except Exception as e:
            logging.error(f"Error in capture_and_detect: {e}", exc_info=True)
        finally:
            self.camera.release()

    def get_stats(self):
        """Retorna estadísticas del detector"""
        uptime = time.time() - self.start_time
        return {
            "fps": self.fps,
            "frames_processed": self.frames_processed,
            "uptime_seconds": round(uptime, 2),
            "camera_fallback": self.camera.use_fallback,
            "detection_threads": Config.NUM_THREADS
        }

    def restart(self):
        if not self.running:
            self.camera = Camera()
            self.running = True
            thread = threading.Thread(target=self.capture_and_detect)
            thread.daemon = True
            thread.start()
            logging.info("Detector restarted.")

    def stop(self):
        """Detiene el detector"""
        self.running = False
        self.camera.release()


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%B%d/%Y %H:%M:%S",
        handlers=[
            logging.FileHandler(Config.LOG_FILE_PATH),
            logging.StreamHandler()
        ]
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

        @app.route("/")
        def index():
            return jsonify({
                "status": "running",
                "service": "raspberry-pi-detector",
                "processing_server": Config.PROCESSING_SERVER_HOSTNAME,
                "camera_fallback": detector.camera.use_fallback,
                "config": {
                    "target_fps": Config.TARGET_FPS,
                    "detection_threads": Config.NUM_THREADS,
                    "frame_resolution": f"{Config.FRAME_WIDTH}x{Config.FRAME_HEIGHT}"
                }
            })

        @app.route("/status")
        def status():
            stats = detector.get_stats()
            return jsonify({
                "camera_opened": detector.camera.isOpened(),
                "processing_server": Config.PROCESSING_SERVER_HOSTNAME,
                **stats
            })
        
        @app.route("/logs")
        def get_logs():
            try:
                with open(Config.LOG_FILE_PATH, "r") as f:
                    return jsonify({"log": f.read()})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route("/shutdown", methods=["POST"])
        def shutdown():
            detector.stop()
            return jsonify({"status": "detector stopped"})
        
        @app.route("/restart", methods=["POST"])
        def restart():
            if not detector.running:
                detector.restart()
                return jsonify({"status": "detector restarted"})
            else:
                return jsonify({"status": "detector already running"}), 400

        logging.info("Starting Raspberry Pi detector service on port 8080")
        app.run(host="0.0.0.0", port=8080, threaded=True)

    except Exception as e:
        logging.error(f"Error starting service: {e}", exc_info=True)
        if 'detector' in locals():
            detector.stop()
    finally:
        if 'detector' in locals():
            detector.stop()