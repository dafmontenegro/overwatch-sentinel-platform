import os
import cv2
import time
import base64
import logging
import argparse
import multiprocessing
from datetime import datetime
from flask import Flask, Response, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import numpy as np

class VideoRecorder:
    def __init__(self, output_path, frame_size, fps=24):
        self.output_path = output_path
        self.frame_size = frame_size
        self.fps = fps
        self.fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.writer = None
        self.frame_count = 0
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        self.writer = cv2.VideoWriter(output_path, self.fourcc, fps, frame_size)
        logging.info(f"Video recorder initialized: {output_path}")

    def write_frame(self, frame):
        if self.writer:
            self.writer.write(frame)
            self.frame_count += 1

    def finalize(self):
        if self.writer:
            self.writer.release()
            duration = self.frame_count / self.fps
            logging.info(f"Video saved: {self.output_path} ({duration:.2f}s, {self.frame_count} frames)")
            return True
        return False

class EventManager:
    def __init__(self, events_folder="events", storage_capacity_gb=20):
        self.events_folder = events_folder
        self.storage_capacity_gb = storage_capacity_gb
        self.current_recording = None
        self.frame_buffer = []
        self.recording_metadata = {}
        
        # Create events folder
        os.makedirs(events_folder, exist_ok=True)
        logging.info(f"EventManager initialized: {events_folder} (max {storage_capacity_gb}GB)")

    def should_record(self, detections, safe_zone_coords):
        """Check if recording should start based on detections and safe zone"""
        if not detections:
            return False
        
        safe_zone_start, safe_zone_end = safe_zone_coords
        
        for detection in detections:
            bbox = detection['bbox']
            rect_start = (bbox['x'], bbox['y'])
            rect_end = (bbox['x'] + bbox['width'], bbox['y'] + bbox['height'])
            
            # Check safe zone invasion
            if self._safe_zone_invasion(rect_start, rect_end, safe_zone_start, safe_zone_end):
                return True
        
        return False

    def _safe_zone_invasion(self, rect_start, rect_end, safe_zone_start, safe_zone_end):
        """Check if detection rectangle invades safe zone"""
        if safe_zone_start[0] > rect_end[0] or safe_zone_end[0] < rect_start[0]:
            return False
        if safe_zone_start[1] > rect_end[1] or safe_zone_end[1] < rect_start[1]:
            return False
        return True

    def start_recording(self, timestamp):
        """Start a new recording session"""
        dt = datetime.fromtimestamp(timestamp)
        day = dt.strftime("%B%d")
        hour = dt.strftime("%Hhr")
        filename = dt.strftime("%B%d_%Hhr_%Mmin%Ssec.avi")
        
        video_path = os.path.join(self.events_folder, day, hour, filename)
        
        self.recording_metadata = {
            'start_time': timestamp,
            'day': day,
            'hour': hour,
            'filename': filename,
            'path': video_path
        }
        
        logging.info(f"Started recording: {video_path}")
        return video_path

    def add_frame_to_buffer(self, frame):
        """Add frame to recording buffer"""
        self.frame_buffer.append(frame)

    def finalize_recording(self, min_duration=1, max_duration=60):
        """Finalize current recording if conditions are met"""
        if not self.frame_buffer:
            return None
        
        frame_count = len(self.frame_buffer)
        duration = frame_count / 24  # Assuming 24 FPS
        
        if duration < min_duration:
            logging.info(f"Recording too short ({duration:.2f}s), discarding")
            self.frame_buffer.clear()
            return None
        
        # Limit duration
        if duration > max_duration:
            max_frames = int(max_duration * 24)
            self.frame_buffer = self.frame_buffer[-max_frames:]
        
        # Save video
        video_path = self.recording_metadata['path']
        frame_size = (self.frame_buffer[0].shape[1], self.frame_buffer[0].shape[0])
        
        recorder = VideoRecorder(video_path, frame_size)
        for frame in self.frame_buffer:
            recorder.write_frame(frame)
        
        success = recorder.finalize()
        
        if success:
            result = self.recording_metadata.copy()
            result['duration'] = duration
            result['frame_count'] = len(self.frame_buffer)
            
            # Clear buffer
            self.frame_buffer.clear()
            self.recording_metadata = {}
            
            return result
        
        return None

    def get_events_json(self):
        """Get events in JSON format"""
        events = []
        
        if not os.path.exists(self.events_folder):
            return events
        
        try:
            for day in sorted(os.listdir(self.events_folder)):
                day_path = os.path.join(self.events_folder, day)
                if not os.path.isdir(day_path):
                    continue
                
                day_events = {
                    'date': day,
                    'hours': []
                }
                
                for hour in sorted(os.listdir(day_path)):
                    hour_path = os.path.join(day_path, hour)
                    if not os.path.isdir(hour_path):
                        continue
                    
                    hour_events = {
                        'time': hour,
                        'videos': []
                    }
                    
                    for video_file in sorted(os.listdir(hour_path)):
                        if video_file.endswith('.avi'):
                            video_path = os.path.join(hour_path, video_file)
                            video_info = {
                                'filename': video_file,
                                'display_name': video_file.replace('.avi', '').split('_', 1)[1] if '_' in video_file else video_file,
                                'path': os.path.join(day, hour, video_file),
                                'size': os.path.getsize(video_path),
                                'modified': os.path.getmtime(video_path)
                            }
                            hour_events['videos'].append(video_info)
                    
                    if hour_events['videos']:
                        day_events['hours'].append(hour_events)
                
                if day_events['hours']:
                    events.append(day_events)
        
        except Exception as e:
            logging.error(f"Error reading events: {e}")
        
        return events

class SecurityProcessor:
    def __init__(self, allowed_hosts=None):
        # Hardware detection
        self.cpu_count = multiprocessing.cpu_count()
        logging.info(f"Server detected {self.cpu_count} CPU cores")
        
        # Configuration
        self.safe_zone_coords = ((880, 360), (1280, 720))
        self.frame_size = (1280, 720)
        
        # Components
        self.event_manager = EventManager()
        
        # State management
        self.current_frame = None
        self.last_detections = []
        self.recording_active = False
        self.last_detection_time = None
        self.detection_timeout = 3  # seconds
        self.connected_clients = set()
        
        # Performance monitoring
        self.frames_received = 0
        self.start_time = time.time()
        
        # Flask app
        self.app = Flask(__name__)
        CORS(self.app, origins=allowed_hosts if allowed_hosts else "*")
        
        # Socket.IO server using Flask-SocketIO with better configuration
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True,
            async_mode='threading',
            ping_timeout=60,
            ping_interval=25
        )
        
        self._setup_routes()
        self._setup_socket_events()

    def _setup_socket_events(self):
        @self.socketio.on('connect')
        def handle_connect():
            client_id = str(id(self.socketio))
            self.connected_clients.add(client_id)
            logging.info(f"Client connected: {client_id}. Total clients: {len(self.connected_clients)}")
            emit('connection_ack', {'status': 'connected', 'server_time': time.time()})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            client_id = str(id(self.socketio))
            self.connected_clients.discard(client_id)
            logging.info(f"Client disconnected: {client_id}. Total clients: {len(self.connected_clients)}")

        @self.socketio.on('frame_data')
        def handle_frame_data(data):
            self._process_frame_data(data)
            # Send acknowledgment
            emit('frame_ack', {'timestamp': time.time(), 'status': 'processed'})

        @self.socketio.on('ping')
        def handle_ping(data):
            emit('pong', {'timestamp': time.time()})

    def _process_frame_data(self, data):
        """Process incoming frame data from Raspberry Pi"""
        try:
            timestamp = data.get('timestamp', time.time())
            frame_b64 = data.get('frame')
            detections = data.get('detections', [])
            
            if not frame_b64:
                logging.warning("Received empty frame data")
                return
            
            # Decode frame
            frame_data = base64.b64decode(frame_b64)
            frame_array = np.frombuffer(frame_data, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            if frame is None:
                logging.warning("Failed to decode frame")
                return
            
            # Process frame
            processed_frame = self._process_frame(frame, detections, timestamp)
            self.current_frame = processed_frame
            self.last_detections = detections
            
            # Handle recording logic
            self._handle_recording(processed_frame, detections, timestamp)
            
            self.frames_received += 1
            
            # Log performance periodically
            if self.frames_received % 100 == 0:
                elapsed = time.time() - self.start_time
                fps = self.frames_received / elapsed if elapsed > 0 else 0
                logging.info(f"Processed {self.frames_received} frames, avg FPS: {fps:.2f}")
        
        except Exception as e:
            logging.error(f"Error processing frame data: {e}", exc_info=True)

    def _process_frame(self, frame, detections, timestamp):
        """Add visual overlays to frame"""
        processed_frame = frame.copy()
        
        # Draw detections
        for detection in detections:
            bbox = detection['bbox']
            category = detection['category']
            score = detection['score']
            
            # Draw bounding box
            start_point = (int(bbox['x']), int(bbox['y']))
            end_point = (int(bbox['x'] + bbox['width']), int(bbox['y'] + bbox['height']))
            cv2.rectangle(processed_frame, start_point, end_point, (0, 0, 255), 2)
            
            # Draw label
            label = f"{category} ({score:.2f})"
            label_position = (int(bbox['x'] + 7), int(bbox['y'] + 21))
            cv2.putText(processed_frame, label, label_position, 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Draw timestamp
        time_str = datetime.fromtimestamp(timestamp).strftime("%B%d/%Y %H:%M:%S")
        cv2.putText(processed_frame, time_str, (21, 42), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Draw safe zone
        cv2.rectangle(processed_frame, self.safe_zone_coords[0], self.safe_zone_coords[1], 
                     (0, 255, 255), 2)
        
        # Draw recording indicator
        if self.recording_active:
            cv2.circle(processed_frame, (1238, 21), 12, (0, 255, 0), -1)
        else:
            cv2.circle(processed_frame, (1238, 21), 12, (0, 0, 255), -1)
        
        return processed_frame

    def _handle_recording(self, frame, detections, timestamp):
        """Handle video recording logic"""
        should_record = self.event_manager.should_record(detections, self.safe_zone_coords)
        
        if should_record:
            if not self.recording_active:
                # Start new recording
                self.event_manager.start_recording(timestamp)
                self.recording_active = True
                logging.info("Recording started due to detection")
            
            self.last_detection_time = timestamp
            self.event_manager.add_frame_to_buffer(frame)
        
        elif self.recording_active:
            # Check if we should stop recording
            if timestamp - self.last_detection_time > self.detection_timeout:
                # Finalize recording
                result = self.event_manager.finalize_recording()
                if result:
                    logging.info(f"Recording saved: {result['filename']} ({result['duration']:.2f}s)")
                
                self.recording_active = False
                logging.info("Recording stopped due to timeout")
            else:
                # Continue recording
                self.event_manager.add_frame_to_buffer(frame)

    def _setup_routes(self):
        @self.app.route('/')
        def stream_video():
            return Response(self._generate_video_stream(), 
                          mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/events')
        def get_events():
            events = self.event_manager.get_events_json()
            return jsonify({
                'events': events,
                'total_days': len(events),
                'total_videos': sum(len(hour['videos']) for day in events for hour in day['hours'])
            })

        @self.app.route('/status')
        def get_status():
            uptime = time.time() - self.start_time
            return jsonify({
                'status': 'running',
                'uptime': uptime,
                'frames_processed': self.frames_received,
                'recording_active': self.recording_active,
                'last_detections': len(self.last_detections),
                'cpu_cores': self.cpu_count,
                'connected_clients': len(self.connected_clients)
            })

        @self.app.route('/health')
        def health_check():
            return jsonify({'status': 'healthy', 'timestamp': time.time()})

    def _generate_video_stream(self):
        """Generate video stream for web viewing"""
        while True:
            if self.current_frame is not None:
                ret, jpeg = cv2.imencode('.jpg', self.current_frame)
                if ret:
                    frame_bytes = jpeg.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.1)  # Limit stream rate

    def run(self, host='0.0.0.0', port=8080):
        """Run the server"""
        logging.info(f"Starting server on {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)

def main():
    parser = argparse.ArgumentParser(description="MacBook Security Server")
    parser.add_argument("--host", default="0.0.0.0", 
                       help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, 
                       help="Port to bind to")
    parser.add_argument("--allowed-hosts", nargs="*", 
                       help="Allowed hosts for CORS (default: all)")
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Log level")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    logging.info("Starting MacBook Security Server")
    logging.info(f"Allowed hosts: {args.allowed_hosts if args.allowed_hosts else 'All'}")
    
    # Create and run server
    processor = SecurityProcessor(allowed_hosts=args.allowed_hosts)
    
    try:
        processor.run(host=args.host, port=args.port)
    except KeyboardInterrupt:
        logging.info("Received shutdown signal")
    except Exception as e:
        logging.error(f"Server error: {e}", exc_info=True)

if __name__ == "__main__":
    main()