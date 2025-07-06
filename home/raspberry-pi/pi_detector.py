import os
import cv2
import time
import json
import base64
import logging
import argparse
import requests
import threading
import multiprocessing
from tflite_support.task import core
from tflite_support.task import vision
from tflite_support.task import processor
from flask import Flask, Response, jsonify
from flask_cors import CORS


class ObjectDetector:
    def __init__(self, model_name="efficientdet_lite0.tflite", num_threads=4, score_threshold=0.3, max_results=1, category_name_allowlist=["person"]):
        base_options = core.BaseOptions(file_name=model_name, use_coral=False, num_threads=num_threads)
        detection_options = processor.DetectionOptions(max_results=max_results, score_threshold=score_threshold, category_name_allowlist=category_name_allowlist)
        options = vision.ObjectDetectorOptions(base_options=base_options, detection_options=detection_options)
        self.detector = vision.ObjectDetector.create_from_options(options)

    def detections(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return self.detector.detect(vision.TensorImage.create_from_array(rgb_image)).detections


class Camera:
    def __init__(self, frame_width=1280, frame_height=720, camera_number=0, fallback_video="test.mp4"):
        self.use_fallback = False
        self.video_capture = cv2.VideoCapture(camera_number)

        if not self.video_capture.isOpened():
            logging.warning("Unable to access camera. Falling back to sample video.")
            self.video_capture = cv2.VideoCapture(fallback_video)
            self.use_fallback = True
            self.fallback_fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            if not self.fallback_fps or self.fallback_fps <= 1:
                self.fallback_fps = 24

        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
        self.last_frame_time = time.time()

    def frame(self):
        if self.use_fallback:
            current_time = time.time()
            elapsed = current_time - self.last_frame_time
            delay = 1.0 / self.fallback_fps
            if elapsed < delay:
                time.sleep(delay - elapsed)
            self.last_frame_time = time.time()

        success, frame = self.video_capture.read()

        if self.use_fallback and not success:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = self.video_capture.read()

        return frame if success else None

    def isOpened(self):
        return self.video_capture.isOpened()

    def release(self):
        self.video_capture.release()


class RaspberryPiDetector:
    def __init__(self, frame_width=1280, frame_height=720, camera_number=0, model_name="efficientdet_lite0.tflite", 
                 num_threads=4, score_threshold=0.3, max_results=1, category_name_allowlist=["person"],
                 processing_server_host="localhost", processing_server_port=8081):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.camera = Camera(frame_width, frame_height, camera_number)
        self.object_detector = ObjectDetector(model_name, num_threads, score_threshold, max_results, category_name_allowlist)
        self.processing_server_host = processing_server_host
        self.processing_server_port = processing_server_port
        self.processing_server_url = f"http://{processing_server_host}:{processing_server_port}"
        self.current_frame = None
        self.running = True
        
        # Estadísticas de FPS
        self.fps_frame_count = 30
        self.frame_times = []
        self.fps = 24

    def capture_and_detect(self):
        """Captura frames y detecta objetos, enviando datos al servidor de procesamiento"""
        try:
            while self.running and self.camera.isOpened():
                start_time = time.time()
                frame = self.camera.frame()
                
                if frame is None:
                    continue
                
                self.current_frame = frame
                time_localtime = time.localtime()
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
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Calcular FPS
                self.frame_times.append(time.time() - start_time)
                if len(self.frame_times) >= self.fps_frame_count:
                    average_frame_time = sum(self.frame_times) / len(self.frame_times)
                    self.fps = round(1/average_frame_time, 2)
                    self.frame_times = []
                
                # Enviar datos al servidor de procesamiento
                data = {
                    "frame": frame_base64,
                    "detections": detection_data,
                    "timestamp": time.strftime("%B%d/%Y %H:%M:%S", time_localtime),
                    "fps": self.fps,
                    "frame_width": self.frame_width,
                    "frame_height": self.frame_height
                }
                
                try:
                    response = requests.post(
                        f"{self.processing_server_url}/process_frame",
                        json=data,
                        timeout=1
                    )
                    if response.status_code != 200:
                        logging.warning(f"Processing server responded with status {response.status_code}")
                except requests.exceptions.RequestException as e:
                    logging.error(f"Error sending data to processing server: {e}")
                    time.sleep(0.1)  # Evitar spam de logs
                
        except Exception as e:
            logging.error(f"Error in capture_and_detect: {e}", exc_info=True)
        finally:
            self.camera.release()

    def get_current_frame(self):
        """Retorna el frame actual para el endpoint de streaming"""
        if self.current_frame is not None:
            return self.current_frame
        return None

    def stop(self):
        self.running = False
        self.camera.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-file", default="raspberry_pi.log", help="Log file name")
    parser.add_argument("--processing-server-host", default=os.getenv("PROCESSING_SERVER_HOST", "localhost"), 
                       help="Processing server host")
    parser.add_argument("--processing-server-port", type=int, default=int(os.getenv("PROCESSING_SERVER_PORT", "8081")), 
                       help="Processing server port")
    args = parser.parse_args()

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%B%d/%Y %H:%M:%S"
    )

    try:
        # Crear detector
        detector = RaspberryPiDetector(
            frame_width=1280,
            frame_height=720,
            camera_number=0,
            model_name="efficientdet_lite0.tflite",
            num_threads=multiprocessing.cpu_count(),
            score_threshold=0.5,
            max_results=3,
            category_name_allowlist=["person", "dog"],
            processing_server_host=args.processing_server_host,
            processing_server_port=args.processing_server_port
        )

        # Iniciar captura en un hilo separado
        capture_thread = threading.Thread(target=detector.capture_and_detect)
        capture_thread.daemon = True
        capture_thread.start()

        # Iniciar servidor Flask para endpoints de la Raspberry Pi
        app = Flask(__name__)
        CORS(app)

        @app.route("/")
        def index():
            return jsonify({
                "status": "running",
                "service": "raspberry-pi-detector",
                "processing_server": f"{args.processing_server_host}:{args.processing_server_port}"
            })

        @app.route("/status")
        def status():
            return jsonify({
                "camera_opened": detector.camera.isOpened(),
                "fps": detector.fps,
                "processing_server": f"{args.processing_server_host}:{args.processing_server_port}"
            })

        @app.route("/raw_stream")
        def raw_stream():
            """Stream de frames sin procesar (solo para debugging)"""
            def generate():
                while detector.running:
                    frame = detector.get_current_frame()
                    if frame is not None:
                        _, buffer = cv2.imencode('.jpg', frame)
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    time.sleep(0.033)  # ~30 FPS
            
            return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

        logging.info(f"Starting Raspberry Pi detector service on port 8080")
        logging.info(f"Processing server: {args.processing_server_host}:{args.processing_server_port}")
        
        app.run(host="0.0.0.0", port=8080, threaded=True)

    except Exception as e:
        logging.error(f"Error starting service: {e}", exc_info=True)
        if 'detector' in locals():
            detector.stop()
    finally:
        if 'detector' in locals():
            detector.stop()