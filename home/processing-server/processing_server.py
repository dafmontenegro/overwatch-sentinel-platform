import os
import cv2
import time
import base64
import shutil
import logging
import threading
import subprocess
import numpy as np
from flask import Flask, Response, jsonify, request, abort
from flask_cors import CORS
from config_ps import Config


class StorageManager:
    def __init__(self):
        self.events_folder = Config.EVENTS_FOLDER
        self.storage_capacity = Config.STORAGE_CAPACITY_GB

    @staticmethod
    def folder_size_gb(folder_path):
        """Calcula el tamaño de una carpeta en GB"""
        total_size_bytes = 0
        for dirpath, _, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size_bytes += os.path.getsize(file_path)
        return total_size_bytes / (1024 ** 3)
    
    @staticmethod
    def delete_folder(folder_path):
        """Elimina una carpeta y retorna el tamaño liberado"""
        if not os.path.exists(folder_path):
            return 0
        folder_size = StorageManager.folder_size_gb(folder_path)
        shutil.rmtree(folder_path)
        logging.warning(f"STORAGE: '{folder_path}' deleted (-{folder_size:.4f} GB)")
        return folder_size

    def supervise_folder_capacity(self):
        """Supervisa y limpia el almacenamiento cuando excede la capacidad"""
        if not os.path.exists(self.events_folder):
            return
        
        events_folder_size = StorageManager.folder_size_gb(self.events_folder)
        logging.info(f"STORAGE: '{self.events_folder}' size: {events_folder_size:.4f} GB")
        
        while events_folder_size > self.storage_capacity:
            folders = [f for f in os.listdir(self.events_folder) 
                      if os.path.isdir(os.path.join(self.events_folder, f))]
            if not folders:
                break
            folder_to_delete = os.path.join(self.events_folder, min(folders))
            events_folder_size -= StorageManager.delete_folder(folder_to_delete)


class SecurityProcessor:
    def __init__(self, pi_id="pi1"):
        self.pi_id = pi_id
        self.storage_manager = StorageManager()
        
        # Estado de grabación
        self.last_detection_timestamp = None
        self.frame_buffer = []
        self.output = {}
        self.events = 0
        self.current_processed_frame = None
        
        # Estadísticas
        self.frames_received = 0
        self.start_time = time.time()
        self.last_frame_time = 0
        
        logging.info(f"Security Processor initialized for {self.pi_id}")

    def _safe_zone_invasion(self, rect_start, rect_end):
        """Detecta si un rectángulo invade la zona segura"""
        if Config.SAFE_ZONE_START[0] > rect_end[0] or Config.SAFE_ZONE_END[0] < rect_start[0]:
            return False
        if Config.SAFE_ZONE_START[1] > rect_end[1] or Config.SAFE_ZONE_END[1] < rect_start[1]:
            return False
        return True

    def process_frame_data(self, frame_data):
        """Procesa los datos del frame recibidos de la Raspberry Pi"""
        try:
            # Actualizar estadísticas
            self.frames_received += 1
            self.last_frame_time = time.time()
            
            # Decodificar frame
            frame_bytes = base64.b64decode(frame_data['frame'])
            frame_array = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            if frame is None:
                logging.error(f"[{self.pi_id}] Failed to decode frame")
                return False
            
            # Obtener datos
            detections = frame_data['detections']
            timestamp_str = frame_data['timestamp']
            fps = frame_data.get('fps', 24)
            
            # Procesar detecciones y dibujar en el frame
            security_breach = False
            color = (0, 0, 255)  # Rojo
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_size = 1
            font_thickness = 2
            
            for detection in detections:
                bbox = detection['bbox']
                category = detection['category']
                score = detection.get('score', 0)
                
                rect_start = (int(bbox['x']), int(bbox['y']))
                rect_end = (int(bbox['x'] + bbox['width']), int(bbox['y'] + bbox['height']))
                text_position = (7 + int(bbox['x']), 21 + int(bbox['y']))
                
                # Dibujar rectángulo y texto con score
                label = f"{category} ({score:.2f})"
                cv2.putText(frame, label, text_position, font, font_size, color, font_thickness)
                cv2.rectangle(frame, rect_start, rect_end, color, font_thickness)
                
                # Verificar invasión de zona segura
                if self._safe_zone_invasion(rect_start, rect_end):
                    security_breach = True
                    # Marcar invasión con color diferente
                    cv2.rectangle(frame, rect_start, rect_end, (0, 255, 0), font_thickness)
            
            # Dibujar timestamp y PI ID
            cv2.putText(frame, f"{self.pi_id.upper()} - {timestamp_str}", (21, 42), font, font_size, color, font_thickness)
            
            # Dibujar zona segura
            zone_color = (0, 255, 255)  # Amarillo
            if security_breach:
                zone_color = (0, 0, 255)  # Rojo si hay invasión
            cv2.rectangle(frame, Config.SAFE_ZONE_START, Config.SAFE_ZONE_END, zone_color, font_thickness)
            
            # Dibujar FPS
            cv2.putText(frame, f"FPS: {fps}", (1100, 702), font, font_size, color, font_thickness)
            
            # Guardar frame procesado
            self.current_processed_frame = frame
            
            # Lógica de seguridad y grabación
            time_localtime = time.strptime(timestamp_str, "%B%d/%Y %H:%M:%S")
            self._handle_security_logic(security_breach, time_localtime, frame)
            
            return True
            
        except Exception as e:
            logging.error(f"[{self.pi_id}] Error processing frame data: {e}", exc_info=True)
            return False

    def _handle_security_logic(self, security_breach, time_localtime, frame):
        """Maneja la lógica de seguridad y grabación de eventos"""
        if security_breach:
            if not self.frame_buffer:
                self.output["file_name"] = f"{self.pi_id}_{time.strftime('%B%d_%Hhr_%Mmin%Ssec', time_localtime)}"
                self.output["day"], self.output["hours"], self.output["mins"] = self.output["file_name"].split("_")[1:]
                self.output["path"] = os.path.join(Config.EVENTS_FOLDER, self.pi_id, self.output["day"], 
                                                 self.output["hours"], f"{self.output['file_name']}.mp4")
                logging.info(f"[{self.pi_id}] Security breach detected - starting recording: {self.output['file_name']}")
                
            self.last_detection_timestamp = time.time()
            self.frame_buffer.append(frame)
        else:
            if self.last_detection_timestamp and ((time.time() - self.last_detection_timestamp) >= Config.MAX_DETECTION_DELAY):
                if len(self.frame_buffer) >= 24 * Config.MIN_VIDEO_DURATION:
                    self.save_frame_buffer(self.output["path"])
                else:
                    logging.info(f"[{self.pi_id}] Recording too short ({len(self.frame_buffer)} frames) - discarding")
                
                self.last_detection_timestamp = None
                self.frame_buffer = []
                self.output = {}
            elif len(self.frame_buffer) >= 24 * Config.MAX_VIDEO_DURATION:
                logging.info(f"[{self.pi_id}] Max recording duration reached - saving video")
                self.save_frame_buffer(self.output["path"])

    def save_frame_buffer(self, path):
        """Guarda el buffer de frames como video H.264 usando ffmpeg directamente"""
        if not self.frame_buffer:
            return
        
        output_seconds = int(len(self.frame_buffer) / 24)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Guardar frames temporales en un archivo .avi sin compresión
        temp_path = path + ".tmp.avi"
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        out = cv2.VideoWriter(temp_path, fourcc, 24, (1280, 720))

        logging.warning(f"[{self.pi_id}] EVENT: {output_seconds} seconds {path}")

        for frame in self.frame_buffer:
            out.write(frame)
        out.release()

        # Convertir a H.264 usando ffmpeg directamente
        try:
            result = subprocess.run([
                'ffmpeg', '-y', '-i', temp_path,
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                path
            ], check=True, capture_output=True)
            logging.info(f"[{self.pi_id}] Video guardado en H.264: {path}")
            os.remove(temp_path)
        except Exception as e:
            logging.error(f'[{self.pi_id}] Error al convertir a H.264: {e}')
            if hasattr(e, 'stderr'):
                logging.error(e.stderr.decode())
        
        self.events += 1
        self.frame_buffer = []
        
        if self.events % Config.EVENT_CHECK_INTERVAL == 0:
            storage_thread = threading.Thread(target=self.storage_manager.supervise_folder_capacity)
            storage_thread.daemon = True
            storage_thread.start()

    def get_current_frame(self):
        """Retorna el frame procesado actual"""
        return self.current_processed_frame

    def get_stats(self):
        """Retorna estadísticas del procesador"""
        uptime = time.time() - self.start_time
        return {
            "pi_id": self.pi_id,
            "frames_received": self.frames_received,
            "events_count": self.events,
            "uptime_seconds": round(uptime, 2),
            "last_frame_time": self.last_frame_time,
            "current_buffer_size": len(self.frame_buffer) if self.frame_buffer else 0
        }


class MultiPiManager:
    def __init__(self):
        Config.validate_config()
        
        # Diccionario de procesadores por PI
        self.processors = {}
        
        # Inicializar procesadores para cada PI configurada
        for pi_id in Config.RASPBERRY_PI_IDS:
            self.processors[pi_id] = SecurityProcessor(pi_id)
            logging.info(f"Initialized processor for {pi_id}")
        
        # Storage manager compartido
        self.storage_manager = StorageManager()
        
        # Inicializar carpeta de eventos
        os.makedirs(Config.EVENTS_FOLDER, exist_ok=True)
        self.storage_manager.supervise_folder_capacity()
        
        logging.info("MultiPi Manager initialized")
        logging.info(f"Configured PIs: {Config.RASPBERRY_PI_IDS}")

    def get_processor(self, pi_id):
        """Obtiene el procesador para una PI específica"""
        return self.processors.get(pi_id)

    def get_events_json(self):
        """Retorna la lista de eventos de todas las PIs en formato JSON"""
        if not os.path.exists(Config.EVENTS_FOLDER):
            return {"events": [], "message": "No events folder found"}
        
        events_by_pi = {}
        total_events = 0
        
        try:
            # Listar por PI
            for pi_id in self.processors.keys():
                pi_folder = os.path.join(Config.EVENTS_FOLDER, pi_id)
                if not os.path.exists(pi_folder):
                    events_by_pi[pi_id] = []
                    continue
                
                pi_events = []
                
                for day in sorted(os.listdir(pi_folder)):
                    day_path = os.path.join(pi_folder, day)
                    if not os.path.isdir(day_path):
                        continue
                        
                    day_info = {"date": day, "hours": []}
                    
                    for hour in sorted(os.listdir(day_path)):
                        hour_path = os.path.join(day_path, hour)
                        if not os.path.isdir(hour_path):
                            continue
                            
                        hour_info = {"time": hour, "videos": []}
                        
                        for video in sorted(os.listdir(hour_path)):
                            if video.endswith('.mp4'):
                                video_name = "_".join(video.split("_")[2:]).replace(".mp4", "")
                                video_path = os.path.join(pi_id, day, hour, video)
                                file_size = os.path.getsize(os.path.join(hour_path, video))
                                
                                hour_info["videos"].append({
                                    "name": video_name,
                                    "path": video_path,
                                    "filename": video,
                                    "size_mb": round(file_size / (1024 * 1024), 2),
                                    "pi_id": pi_id
                                })
                                total_events += 1
                        
                        if hour_info["videos"]:
                            day_info["hours"].append(hour_info)
                    
                    if day_info["hours"]:
                        pi_events.append(day_info)
                
                events_by_pi[pi_id] = pi_events
            
            return {
                "events_by_pi": events_by_pi,
                "total_events": total_events,
                "storage_used_gb": round(self.storage_manager.folder_size_gb(Config.EVENTS_FOLDER), 3),
                "configured_pis": Config.RASPBERRY_PI_IDS
            }
            
        except Exception as e:
            logging.error(f"Error getting events: {e}", exc_info=True)
            return {"events_by_pi": {}, "error": str(e)}

    def get_all_stats(self):
        """Retorna estadísticas de todas las PIs"""
        stats = {}
        for pi_id, processor in self.processors.items():
            stats[pi_id] = processor.get_stats()
        
        stats["storage_used_gb"] = round(self.storage_manager.folder_size_gb(Config.EVENTS_FOLDER), 3)
        stats["storage_capacity_gb"] = Config.STORAGE_CAPACITY_GB
        
        return stats


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%B%d/%Y %H:%M:%S"
    )

    # Suprimir logs de werkzeug
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    try:
        # Inicializar manager multi-PI
        pi_manager = MultiPiManager()

        # Inicializar Flask
        app = Flask(__name__)
        CORS(app)

        @app.route("/")
        def index():
            return jsonify({
                "status": "running",
                "service": "multi-pi-processing-server",
                "events_folder": Config.EVENTS_FOLDER,
                "configured_pis": Config.RASPBERRY_PI_IDS,
                "config": {
                    "safe_zone": f"{Config.SAFE_ZONE_START} to {Config.SAFE_ZONE_END}",
                    "storage_capacity_gb": Config.STORAGE_CAPACITY_GB
                }
            })

        @app.route("/process_frame", methods=["POST"])
        def process_frame():
            """Endpoint compatible con pi_detector.py (sin pi_id en URL)"""
            try:
                # Usar pi1 como default para compatibilidad
                pi_id = "pi1"
                processor = pi_manager.get_processor(pi_id)
                if not processor:
                    return jsonify({"error": f"PI {pi_id} not configured"}), 404
                
                frame_data = request.json
                if not frame_data:
                    return jsonify({"error": "No data provided"}), 400
                
                success = processor.process_frame_data(frame_data)
                
                if success:
                    return jsonify({"status": "processed", "pi_id": pi_id})
                else:
                    return jsonify({"error": "Failed to process frame"}), 500
                    
            except Exception as e:
                logging.error(f"Error in process_frame endpoint: {e}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @app.route("/stream")
        def stream():
            """Stream de video procesado (compatible con pi1)"""
            return stream_pi("pi1")

        @app.route("/stream/<pi_id>")
        def stream_pi(pi_id):
            """Stream de video procesado de una PI específica"""
            processor = pi_manager.get_processor(pi_id)
            if not processor:
                abort(404)
            
            def generate():
                while True:
                    frame = processor.get_current_frame()
                    if frame is not None:
                        # Añadir indicador de transmisión
                        current_time = int(time.time())
                        if current_time % 2:
                            cv2.circle(frame, (1238, 21), 12, (0, 255, 0), -1)  # Verde
                        
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    
                    time.sleep(1.0 / 30)  # 30 FPS para stream
            
            return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

        @app.route("/events")
        def events():
            """Endpoint para obtener la lista de eventos de todas las PIs en JSON"""
            return jsonify(pi_manager.get_events_json())

        @app.route("/video/<path:video_path>")
        def get_video(video_path):
            """Endpoint para servir videos"""
            full_path = os.path.join(Config.EVENTS_FOLDER, video_path)
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path)

                def generate():
                    with open(full_path, 'rb') as f:
                        data = f.read(1024)
                        while data:
                            yield data
                            data = f.read(1024)
                
                response = Response(generate(), mimetype='video/mp4')
                response.headers['Content-Length'] = str(file_size)
                response.headers['Accept-Ranges'] = 'bytes'
                response.headers['Cache-Control'] = 'public, max-age=3600'
        
                return response
            else:
                return jsonify({"error": "Video not found"}), 404

        @app.route("/status")
        def status():
            """Status del servidor de procesamiento multi-PI"""
            return jsonify({
                "status": "running",
                "pis": pi_manager.get_all_stats()
            })

        @app.route("/status/<pi_id>")
        def pi_status(pi_id):
            """Status de una PI específica"""
            processor = pi_manager.get_processor(pi_id)
            if not processor:
                return jsonify({"error": f"PI {pi_id} not configured"}), 404
            
            stats = processor.get_stats()
            return jsonify({
                "status": "running",
                "has_current_frame": processor.current_processed_frame is not None,
                **stats
            })

        logging.info("Starting multi-PI processing server on port 8080")
        logging.info(f"Safe zone configured: {Config.SAFE_ZONE_START} to {Config.SAFE_ZONE_END}")
        logging.info(f"Configured PIs: {Config.RASPBERRY_PI_IDS}")
        
        app.run(host="0.0.0.0", port=8080, threaded=True)

    except Exception as e:
        logging.error(f"Error starting processing server: {e}", exc_info=True)
    finally:
        logging.info("Processing server stopped")