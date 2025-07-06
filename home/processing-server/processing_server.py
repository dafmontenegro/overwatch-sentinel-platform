import os
import cv2
import time
import json
import base64
import shutil
import logging
import argparse
import threading
import numpy as np
from flask import Flask, Response, jsonify, request
from flask_cors import CORS


class StorageManager:
    def __init__(self, events_folder="events", storage_capacity=32):
        self.events_folder = events_folder
        self.storage_capacity = storage_capacity

    @staticmethod
    def folder_size_gb(folder_path):
        total_size_bytes = 0
        for dirpath, _, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size_bytes += os.path.getsize(file_path)
        return total_size_bytes / (1024 ** 3)
    
    @staticmethod
    def delete_folder(folder_path):
        if not os.path.exists(folder_path):
            return 0
        folder_size = StorageManager.folder_size_gb(folder_path)
        shutil.rmtree(folder_path)
        logging.warning(f"STORAGE: '{folder_path}' was deleted (-{folder_size:.4f} GB)")
        return folder_size

    def supervise_folder_capacity(self):
        if not os.path.exists(self.events_folder):
            return
        
        events_folder_size = StorageManager.folder_size_gb(self.events_folder)
        logging.info(f"STORAGE: '{self.events_folder}' is ({events_folder_size:.4f} GB)")
        
        while events_folder_size > self.storage_capacity:
            folders = [f for f in os.listdir(self.events_folder) if os.path.isdir(os.path.join(self.events_folder, f))]
            if not folders:
                break
            folder_to_delete = os.path.join(self.events_folder, min(folders))
            events_folder_size -= StorageManager.delete_folder(folder_to_delete)


class SecurityProcessor:
    def __init__(self, frame_width=1280, frame_height=720, folder_name="events", storage_capacity=21,
                 safe_zone=((880, 360), (1280, 720)), fps=24):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.folder_name = folder_name
        self.storage_manager = StorageManager(folder_name, storage_capacity)
        self.safe_zone_start, self.safe_zone_end = safe_zone
        self.fps = fps
        
        # Estado de grabación
        self.last_detection_timestamp = None
        self.frame_buffer = []
        self.output = {}
        self.events = 0
        self.current_processed_frame = None
        
        # Inicializar carpeta de eventos
        os.makedirs(folder_name, exist_ok=True)
        self.storage_manager.supervise_folder_capacity()

    def _safe_zone_invasion(self, rect_start, rect_end):
        """Detecta si un rectángulo invade la zona segura"""
        if self.safe_zone_start[0] > rect_end[0] or self.safe_zone_end[0] < rect_start[0]:
            return False
        if self.safe_zone_start[1] > rect_end[1] or self.safe_zone_end[1] < rect_start[1]:
            return False
        return True

    def process_frame_data(self, frame_data):
        """Procesa los datos del frame recibidos de la Raspberry Pi"""
        try:
            # Decodificar frame
            frame_bytes = base64.b64decode(frame_data['frame'])
            frame_array = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            if frame is None:
                logging.error("Failed to decode frame")
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
                
                rect_start = (bbox['x'], bbox['y'])
                rect_end = (bbox['x'] + bbox['width'], bbox['y'] + bbox['height'])
                text_position = (7 + bbox['x'], 21 + bbox['y'])
                
                # Dibujar rectángulo y texto
                cv2.putText(frame, category, text_position, font, font_size, color, font_thickness)
                cv2.rectangle(frame, rect_start, rect_end, color, font_thickness)
                
                # Verificar invasión de zona segura
                if self._safe_zone_invasion(rect_start, rect_end):
                    security_breach = True
            
            # Dibujar timestamp
            cv2.putText(frame, timestamp_str, (21, 42), font, font_size, color, font_thickness)
            
            # Dibujar zona segura
            cv2.rectangle(frame, self.safe_zone_start, self.safe_zone_end, (0, 255, 255), font_thickness)
            
            # Dibujar FPS
            cv2.putText(frame, f"FPS: {fps}", (self.frame_width - 180, self.frame_height - 18), 
                       font, font_size, color, font_thickness)
            
            # Guardar frame procesado
            self.current_processed_frame = frame
            
            # Lógica de seguridad y grabación
            time_localtime = time.strptime(timestamp_str, "%B%d/%Y %H:%M:%S")
            self._handle_security_logic(security_breach, time_localtime, frame)
            
            return True
            
        except Exception as e:
            logging.error(f"Error processing frame data: {e}", exc_info=True)
            return False

    def _handle_security_logic(self, security_breach, time_localtime, frame, 
                             min_video_duration=1, max_video_duration=9, 
                             max_detection_delay=3, event_check_interval=12):
        """Maneja la lógica de seguridad y grabación de eventos"""
        if security_breach:
            if not self.frame_buffer:
                self.output["file_name"] = time.strftime("%B%d_%Hhr_%Mmin%Ssec", time_localtime)
                self.output["day"], self.output["hours"], self.output["mins"] = self.output["file_name"].split("_")
                self.output["path"] = os.path.join(self.folder_name, self.output["day"], 
                                                 self.output["hours"], f"{self.output['file_name']}.avi")
            self.last_detection_timestamp = time.time()
            self.frame_buffer.append(frame)
        else:
            if self.last_detection_timestamp and ((time.time() - self.last_detection_timestamp) >= max_detection_delay):
                if len(self.frame_buffer) >= self.fps * min_video_duration:
                    self.save_frame_buffer(self.output["path"], event_check_interval)
                self.last_detection_timestamp = None
                self.frame_buffer = []
                self.output = {}
            elif len(self.frame_buffer) >= self.fps * max_video_duration:
                self.save_frame_buffer(self.output["path"], event_check_interval)

    def save_frame_buffer(self, path, event_check_interval=12):
        """Guarda el buffer de frames como video"""
        if not self.frame_buffer:
            return
            
        output_seconds = int(len(self.frame_buffer) / self.fps)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(path, fourcc, self.fps, (self.frame_width, self.frame_height))
        
        logging.warning(f"EVENT: {output_seconds} seconds {path}")
        
        for frame in self.frame_buffer:
            out.write(frame)
        out.release()
        
        self.events += 1
        self.frame_buffer = []
        
        if self.events % event_check_interval == 0:
            storage_thread = threading.Thread(target=self.storage_manager.supervise_folder_capacity)
            storage_thread.daemon = True
            storage_thread.start()

    def get_events_json(self):
        """Retorna la lista de eventos en formato JSON"""
        if not os.path.exists(self.folder_name):
            return {"events": [], "message": "No events folder found"}
        
        events = []
        
        try:
            for day in sorted(os.listdir(self.folder_name)):
                day_path = os.path.join(self.folder_name, day)
                if not os.path.isdir(day_path):
                    continue
                    
                day_info = {"date": day, "hours": []}
                
                for hour in sorted(os.listdir(day_path)):
                    hour_path = os.path.join(day_path, hour)
                    if not os.path.isdir(hour_path):
                        continue
                        
                    hour_info = {"time": hour, "videos": []}
                    
                    for video in sorted(os.listdir(hour_path)):
                        if video.endswith('.avi'):
                            video_name = "".join(video.split("_")[1:]).replace(".avi", "")
                            video_path = os.path.join(day, hour, video)
                            file_size = os.path.getsize(os.path.join(hour_path, video))
                            
                            hour_info["videos"].append({
                                "name": video_name,
                                "path": video_path,
                                "filename": video,
                                "size_mb": round(file_size / (1024 * 1024), 2)
                            })
                    
                    if hour_info["videos"]:
                        day_info["hours"].append(hour_info)
                
                if day_info["hours"]:
                    events.append(day_info)
            
            return {
                "events": events,
                "total_events": sum(len(hour["videos"]) for day in events for hour in day["hours"]),
                "storage_used_gb": round(self.storage_manager.folder_size_gb(self.folder_name), 3)
            }
            
        except Exception as e:
            logging.error(f"Error getting events: {e}", exc_info=True)
            return {"events": [], "error": str(e)}

    def get_current_frame(self):
        """Retorna el frame procesado actual"""
        return self.current_processed_frame


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder-name", default="events", help="Events folder name")
    parser.add_argument("--log-file", default="processing_server.log", help="Log file name")
    args = parser.parse_args()

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%B%d/%Y %H:%M:%S"
    )

    try:
        # Inicializar procesador de seguridad
        processor = SecurityProcessor(
            frame_width=1280,
            frame_height=720,
            folder_name=args.folder_name,
            storage_capacity=21,
            safe_zone=((880, 360), (1280, 720)),
            fps=24
        )

        # Inicializar Flask
        app = Flask(__name__)
        CORS(app)

        @app.route("/")
        def index():
            return jsonify({
                "status": "running",
                "service": "processing-server",
                "events_folder": args.folder_name
            })

        @app.route("/process_frame", methods=["POST"])
        def process_frame():
            """Endpoint para recibir frames de la Raspberry Pi"""
            try:
                frame_data = request.json
                if not frame_data:
                    return jsonify({"error": "No data provided"}), 400
                
                success = processor.process_frame_data(frame_data)
                
                if success:
                    return jsonify({"status": "processed"})
                else:
                    return jsonify({"error": "Failed to process frame"}), 500
                    
            except Exception as e:
                logging.error(f"Error in process_frame endpoint: {e}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @app.route("/stream")
        def stream():
            """Stream de video procesado"""
            def generate():
                while True:
                    frame = processor.get_current_frame()
                    if frame is not None:
                        # Añadir indicador de transmisión
                        current_time = int(time.time())
                        if current_time % 2:
                            cv2.circle(frame, (1238, 21), 12, (0, 255, 0), -1)  # Verde
                        else:
                            cv2.circle(frame, (1238, 21), 12, (0, 0, 255), -1)  # Rojo
                        
                        _, buffer = cv2.imencode('.jpg', frame)
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    
                    time.sleep(0.033)  # ~30 FPS
            
            return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

        @app.route("/events")
        def events():
            """Endpoint para obtener la lista de eventos en JSON"""
            return jsonify(processor.get_events_json())

        @app.route("/video/<path:video_path>")
        def get_video(video_path):
            """Endpoint para servir videos"""
            full_path = os.path.join(args.folder_name, video_path)
            if os.path.exists(full_path):
                def generate():
                    with open(full_path, 'rb') as f:
                        data = f.read(1024)
                        while data:
                            yield data
                            data = f.read(1024)
                
                return Response(generate(), mimetype='video/x-msvideo')
            else:
                return jsonify({"error": "Video not found"}), 404

        @app.route("/status")
        def status():
            """Status del servidor de procesamiento"""
            return jsonify({
                "status": "running",
                "events_count": processor.events,
                "storage_gb": round(processor.storage_manager.folder_size_gb(args.folder_name), 3),
                "has_current_frame": processor.current_processed_frame is not None
            })

        logging.info("Starting processing server on ports 8080 (web) and 8081 (raspberry)")
        
        # Iniciar servidor en puerto 8081 para recibir datos de raspberry
        from werkzeug.serving import make_server
        
        # Servidor principal en puerto 8080
        server = make_server('0.0.0.0', 8080, app, threaded=True)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Servidor para raspberry en puerto 8081
        server_8081 = make_server('0.0.0.0', 8081, app, threaded=True)
        server_8081.serve_forever()

    except Exception as e:
        logging.error(f"Error starting processing server: {e}", exc_info=True)
    finally:
        logging.info("Processing server stopped")