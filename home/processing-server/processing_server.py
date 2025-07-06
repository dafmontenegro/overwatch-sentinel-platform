import os
import cv2
import time
import base64
import shutil
import socket
import logging
import threading
import ipaddress
import numpy as np
from flask import Flask, Response, jsonify, request, abort
from flask_cors import CORS
from config_ps import Config


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
    def __init__(self):
        Config.validate_config()
        
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
        
        # Inicializar carpeta de eventos
        os.makedirs(Config.EVENTS_FOLDER, exist_ok=True)
        self.storage_manager.supervise_folder_capacity()
        
        logging.info("Security Processor initialized")
        logging.info(f"Safe zone: {Config.SAFE_ZONE_START} to {Config.SAFE_ZONE_END}")
        logging.info(f"Storage capacity: {Config.STORAGE_CAPACITY_GB} GB")
        logging.info(f"Events folder: {Config.EVENTS_FOLDER}")
        logging.info(f"Allowed IPs: {Config.ALLOWED_RASPBERRY_IPS}")

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
                logging.error("Failed to decode frame")
                return False
            
            # Obtener datos
            detections = frame_data['detections']
            timestamp_str = frame_data['timestamp']
            fps = frame_data.get('fps', Config.TARGET_FPS)
            detections_count = frame_data.get('detections_count', len(detections))
            
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
            
            # Dibujar timestamp
            cv2.putText(frame, timestamp_str, (21, 42), font, font_size, color, font_thickness)
            
            # Dibujar zona segura
            zone_color = (0, 255, 255)  # Amarillo
            if security_breach:
                zone_color = (0, 0, 255)  # Rojo si hay invasión
            cv2.rectangle(frame, Config.SAFE_ZONE_START, Config.SAFE_ZONE_END, zone_color, font_thickness)
            
            # Dibujar FPS
            cv2.putText(frame, f"FPS: {fps}", (Config.FRAME_WIDTH - 180, Config.FRAME_HEIGHT - 18), 
                       font, font_size, color, font_thickness)
            
            # Dibujar contador de detecciones
            # cv2.putText(frame, f"Detections: {detections_count}", (Config.FRAME_WIDTH - 250, 42), 
            #           font, font_size, color, font_thickness)
            
            # Guardar frame procesado
            self.current_processed_frame = frame
            
            # Lógica de seguridad y grabación
            time_localtime = time.strptime(timestamp_str, "%B%d/%Y %H:%M:%S")
            self._handle_security_logic(security_breach, time_localtime, frame)
            
            return True
            
        except Exception as e:
            logging.error(f"Error processing frame data: {e}", exc_info=True)
            return False

    def _handle_security_logic(self, security_breach, time_localtime, frame):
        """Maneja la lógica de seguridad y grabación de eventos"""
        if security_breach:
            if not self.frame_buffer:
                self.output["file_name"] = time.strftime("%B%d_%Hhr_%Mmin%Ssec", time_localtime)
                self.output["day"], self.output["hours"], self.output["mins"] = self.output["file_name"].split("_")
                self.output["path"] = os.path.join(Config.EVENTS_FOLDER, self.output["day"], 
                                                 self.output["hours"], f"{self.output['file_name']}.avi")
                logging.info(f"Security breach detected - starting recording: {self.output['file_name']}")
                
            self.last_detection_timestamp = time.time()
            self.frame_buffer.append(frame)
        else:
            if self.last_detection_timestamp and ((time.time() - self.last_detection_timestamp) >= Config.MAX_DETECTION_DELAY):
                if len(self.frame_buffer) >= Config.TARGET_FPS * Config.MIN_VIDEO_DURATION:
                    self.save_frame_buffer(self.output["path"])
                else:
                    logging.info(f"Recording too short ({len(self.frame_buffer)} frames) - discarding")
                
                self.last_detection_timestamp = None
                self.frame_buffer = []
                self.output = {}
            elif len(self.frame_buffer) >= Config.TARGET_FPS * Config.MAX_VIDEO_DURATION:
                logging.info(f"Max recording duration reached - saving video")
                self.save_frame_buffer(self.output["path"])

    def save_frame_buffer(self, path):
        """Guarda el buffer de frames como video"""
        if not self.frame_buffer:
            return
            
        output_seconds = int(len(self.frame_buffer) / Config.TARGET_FPS)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(path, fourcc, Config.TARGET_FPS, (Config.FRAME_WIDTH, Config.FRAME_HEIGHT))
        
        logging.warning(f"EVENT: {output_seconds} seconds {path}")
        
        for frame in self.frame_buffer:
            out.write(frame)
        out.release()
        
        self.events += 1
        self.frame_buffer = []
        
        if self.events % Config.EVENT_CHECK_INTERVAL == 0:
            storage_thread = threading.Thread(target=self.storage_manager.supervise_folder_capacity)
            storage_thread.daemon = True
            storage_thread.start()

    def get_events_json(self):
        """Retorna la lista de eventos en formato JSON"""
        if not os.path.exists(Config.EVENTS_FOLDER):
            return {"events": [], "message": "No events folder found"}
        
        events = []
        
        try:
            for day in sorted(os.listdir(Config.EVENTS_FOLDER)):
                day_path = os.path.join(Config.EVENTS_FOLDER, day)
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
                "storage_used_gb": round(self.storage_manager.folder_size_gb(Config.EVENTS_FOLDER), 3)
            }
            
        except Exception as e:
            logging.error(f"Error getting events: {e}", exc_info=True)
            return {"events": [], "error": str(e)}

    def get_current_frame(self):
        """Retorna el frame procesado actual"""
        return self.current_processed_frame

    def get_stats(self):
        """Retorna estadísticas del procesador"""
        uptime = time.time() - self.start_time
        return {
            "frames_received": self.frames_received,
            "events_count": self.events,
            "uptime_seconds": round(uptime, 2),
            "storage_used_gb": round(self.storage_manager.folder_size_gb(Config.EVENTS_FOLDER), 3),
            "storage_capacity_gb": Config.STORAGE_CAPACITY_GB,
            "last_frame_time": self.last_frame_time,
            "current_buffer_size": len(self.frame_buffer) if self.frame_buffer else 0
        }


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%B%d/%Y %H:%M:%S"
    )

    try:
        # Inicializar procesador de seguridad
        processor = SecurityProcessor()

        # Inicializar Flask
        app = Flask(__name__)
        CORS(app)

        @app.before_request
        def validate_ip():
            client_ip = request.remote_addr
            
            # Endpoints que solo puede acceder la Raspberry Pi
            raspberry_endpoints = ['process_frame']
            
            # Endpoints que solo pueden acceder clientes autorizados
            client_endpoints = ['stream', 'events', 'get_video', 'status']
            
            if request.endpoint in raspberry_endpoints:
                if not SecurityMiddleware.is_raspberry_allowed(client_ip):
                    logging.warning(f"Unauthorized Raspberry Pi access attempt from: {client_ip}")
                    abort(403)
            
            elif request.endpoint in client_endpoints:
                if not SecurityMiddleware.is_client_allowed(client_ip):
                    logging.warning(f"Unauthorized client access attempt from: {client_ip}")
                    abort(403)

        @app.route("/")
        def index():
            return jsonify({
                "status": "running",
                "service": "processing-server",
                "events_folder": Config.EVENTS_FOLDER,
                "config": {
                    "safe_zone": f"{Config.SAFE_ZONE_START} to {Config.SAFE_ZONE_END}",
                    "storage_capacity_gb": Config.STORAGE_CAPACITY_GB,
                    "target_fps": Config.TARGET_FPS,
                    "frame_resolution": f"{Config.FRAME_WIDTH}x{Config.FRAME_HEIGHT}",
                    "allowed_ips": Config.ALLOWED_RASPBERRY_IPS
                }
            })

        @app.route("/process_frame", methods=["POST"])
        def process_frame():
            """Endpoint para recibir frames de la Raspberry Pi (IP protegida)"""
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
                        
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, Config.STREAM_QUALITY])
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    
                    time.sleep(1.0 / Config.STREAM_FPS)
            
            return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

        @app.route("/events")
        def events():
            """Endpoint para obtener la lista de eventos en JSON"""
            return jsonify(processor.get_events_json())

        @app.route("/video/<path:video_path>")
        def get_video(video_path):
            """Endpoint para servir videos"""
            full_path = os.path.join(Config.EVENTS_FOLDER, video_path)
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
            stats = processor.get_stats()
            return jsonify({
                "status": "running",
                "has_current_frame": processor.current_processed_frame is not None,
                **stats
            })

        logging.info("Starting processing server on ports 8080 (web) and 8081 (raspberry)")
        logging.info(f"Safe zone configured: {Config.SAFE_ZONE_START} to {Config.SAFE_ZONE_END}")
        logging.info(f"Detection categories: {Config.DETECTION_CATEGORY_ALLOWLIST}")
        logging.info(f"Authorized IPs: {Config.ALLOWED_RASPBERRY_IPS}")
        
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