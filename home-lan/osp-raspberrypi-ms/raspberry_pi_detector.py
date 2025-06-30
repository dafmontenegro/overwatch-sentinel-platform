import os
import cv2
import time
import json
import logging
import argparse
import threading
import multiprocessing
import socketio
import base64
from tflite_support.task import core
from tflite_support.task import vision
from tflite_support.task import processor

class ObjectDetector:
    def __init__(self, model_name="efficientdet_lite0.tflite", num_threads=None, score_threshold=0.3, max_results=1, category_name_allowlist=["person"]):
        if num_threads is None:
            num_threads = multiprocessing.cpu_count()
        
        logging.info(f"Initializing ObjectDetector with {num_threads} threads")
        base_options = core.BaseOptions(file_name=model_name, use_coral=False, num_threads=num_threads)
        detection_options = processor.DetectionOptions(max_results=max_results, score_threshold=score_threshold, category_name_allowlist=category_name_allowlist)
        options = vision.ObjectDetectorOptions(base_options=base_options, detection_options=detection_options)
        self.detector = vision.ObjectDetector.create_from_options(options)
        logging.info("ObjectDetector initialized successfully")

    def detect_objects(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        detections = self.detector.detect(vision.TensorImage.create_from_array(rgb_image)).detections
        
        results = []
        for detection in detections:
            box = detection.bounding_box
            results.append({
                'bbox': {
                    'x': box.origin_x,
                    'y': box.origin_y,
                    'width': box.width,
                    'height': box.height
                },
                'category': detection.categories[0].category_name,
                'score': detection.categories[0].score
            })
        
        return results

class OptimizedCamera:
    def __init__(self, frame_width=1280, frame_height=720, camera_number=0, fallback_video="test.mp4"):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.use_fallback = False
        self.video_capture = None
        self.fallback_frames = []
        self.current_frame_index = 0
        
        logging.info(f"Initializing camera with resolution {frame_width}x{frame_height}")
        
        # Try to initialize real camera first
        self.video_capture = cv2.VideoCapture(camera_number)
        
        if not self.video_capture.isOpened():
            logging.warning("Unable to access camera. Switching to fallback video mode.")
            self._load_fallback_video(fallback_video)
        else:
            logging.info("Real camera initialized successfully")
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
            
            # Get actual resolution
            actual_width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            logging.info(f"Camera resolution set to {actual_width}x{actual_height}")

    def _load_fallback_video(self, fallback_video):
        """Load all frames from fallback video into memory for optimal performance"""
        logging.info(f"Loading fallback video: {fallback_video}")
        
        if not os.path.exists(fallback_video):
            logging.error(f"Fallback video {fallback_video} not found")
            return
        
        temp_capture = cv2.VideoCapture(fallback_video)
        if not temp_capture.isOpened():
            logging.error(f"Unable to open fallback video: {fallback_video}")
            return
        
        frame_count = 0
        while True:
            ret, frame = temp_capture.read()
            if not ret:
                break
            
            # Resize frame to match desired resolution
            frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            self.fallback_frames.append(frame)
            frame_count += 1
        
        temp_capture.release()
        self.use_fallback = True
        logging.info(f"Loaded {frame_count} frames from fallback video")

    def get_frame(self):
        if self.use_fallback:
            if not self.fallback_frames:
                logging.error("No fallback frames available")
                return None
            
            frame = self.fallback_frames[self.current_frame_index]
            self.current_frame_index = (self.current_frame_index + 1) % len(self.fallback_frames)
            return frame.copy()
        else:
            success, frame = self.video_capture.read()
            if not success:
                logging.warning("Failed to capture frame from camera")
                return None
            return frame

    def is_opened(self):
        return self.use_fallback or (self.video_capture and self.video_capture.isOpened())

    def release(self):
        if self.video_capture:
            self.video_capture.release()
            logging.info("Camera released")
        self.fallback_frames.clear()

class RaspberryPiDetector:
    def __init__(self, server_host="security-server", server_port=8080):
        # Hardware detection
        self.cpu_count = multiprocessing.cpu_count()
        logging.info(f"Detected {self.cpu_count} CPU cores")
        
        # Initialize components
        self.camera = OptimizedCamera()
        self.object_detector = ObjectDetector(
            num_threads=self.cpu_count,
            score_threshold=0.5,
            max_results=3,
            category_name_allowlist=["person", "dog"]
        )
        
        # Socket.IO client with better configuration
        self.sio = socketio.Client(
            logger=True, 
            engineio_logger=True,
            reconnection=True,
            reconnection_attempts=0,  # Infinite attempts
            reconnection_delay=1,
            reconnection_delay_max=5,
            randomization_factor=0.5
        )
        self.server_url = f"http://{server_host}:{server_port}"
        self.connected = False
        self.connection_attempts = 0
        
        # Performance monitoring
        self.frame_count = 0
        self.start_time = time.time()
        self.last_fps_update = time.time()
        self.current_fps = 0
        self.last_ack_time = time.time()
        
        self._setup_socket_events()

    def _setup_socket_events(self):
        @self.sio.event
        def connect():
            self.connected = True
            self.connection_attempts = 0
            logging.info(f"Connected to server at {self.server_url}")

        @self.sio.event
        def disconnect():
            self.connected = False
            logging.warning("Disconnected from server")

        @self.sio.event
        def connect_error(data):
            self.connection_attempts += 1
            logging.error(f"Connection failed (attempt {self.connection_attempts}): {data}")

        @self.sio.event
        def connection_ack(data):
            logging.info(f"Connection acknowledged by server: {data}")

        @self.sio.event
        def frame_ack(data):
            self.last_ack_time = time.time()
            # logging.debug(f"Frame acknowledged: {data}")

        @self.sio.event
        def pong(data):
            logging.debug(f"Pong received: {data}")

    def _encode_frame(self, frame):
        """Encode frame to base64 for transmission"""
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return base64.b64encode(buffer).decode('utf-8')

    def _calculate_fps(self):
        """Calculate and update FPS"""
        current_time = time.time()
        if current_time - self.last_fps_update >= 5.0:  # Update every 5 seconds
            elapsed = current_time - self.start_time
            self.current_fps = round(self.frame_count / elapsed, 2) if elapsed > 0 else 0
            self.last_fps_update = current_time
            logging.info(f"Processing at {self.current_fps} FPS, frames sent: {self.frame_count}")

    def connect_to_server(self):
        """Connect to server with retry logic"""
        max_retries = 10
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                logging.info(f"Attempting to connect to server at {self.server_url} (attempt {attempt + 1}/{max_retries})")
                self.sio.connect(self.server_url, wait_timeout=10)
                return True
            except Exception as e:
                logging.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.5, 30)  # Exponential backoff with max 30s
        
        return False

    def send_ping(self):
        """Send periodic ping to maintain connection"""
        if self.connected:
            try:
                self.sio.emit('ping', {'timestamp': time.time()})
            except Exception as e:
                logging.error(f"Failed to send ping: {e}")

    def check_connection_health(self):
        """Check if connection is healthy"""
        current_time = time.time()
        if current_time - self.last_ack_time > 30:  # No ack for 30 seconds
            logging.warning("No frame acknowledgment received for 30 seconds")
            return False
        return True

    def process_and_send_frames(self):
        """Main processing loop"""
        if not self.connect_to_server():
            logging.error("Failed to connect to server after all retries")
            return

        logging.info("Starting frame processing and transmission")
        last_ping_time = time.time()
        
        while self.camera.is_opened():
            try:
                # Send periodic ping
                current_time = time.time()
                if current_time - last_ping_time > 10:  # Ping every 10 seconds
                    self.send_ping()
                    last_ping_time = current_time

                # Check connection health
                if not self.check_connection_health():
                    logging.warning("Connection appears unhealthy, attempting reconnection...")
                    if not self.connect_to_server():
                        time.sleep(5)
                        continue

                # Capture frame
                frame = self.camera.get_frame()
                if frame is None:
                    logging.warning("Failed to capture frame, retrying...")
                    time.sleep(0.1)
                    continue

                # Detect objects
                detection_start = time.time()
                detections = self.object_detector.detect_objects(frame)
                detection_time = time.time() - detection_start

                # Prepare data for transmission
                frame_data = {
                    'timestamp': time.time(),
                    'frame': self._encode_frame(frame),
                    'detections': detections,
                    'frame_size': {
                        'width': frame.shape[1],
                        'height': frame.shape[0]
                    },
                    'detection_time': detection_time,
                    'fps': self.current_fps,
                    'frame_number': self.frame_count
                }

                # Send to server
                if self.connected:
                    try:
                        self.sio.emit('frame_data', frame_data)
                        self.frame_count += 1
                        self._calculate_fps()
                    except Exception as e:
                        logging.error(f"Failed to send frame data: {e}")
                        self.connected = False
                else:
                    logging.warning("Not connected to server, attempting reconnection...")
                    if not self.connect_to_server():
                        time.sleep(1)
                        continue

                # Control frame rate (approximately 10-15 FPS)
                time.sleep(0.07)

            except KeyboardInterrupt:
                logging.info("Received interrupt signal, shutting down...")
                break
            except Exception as e:
                logging.error(f"Error in processing loop: {e}", exc_info=True)
                time.sleep(0.5)

    def shutdown(self):
        """Clean shutdown"""
        logging.info("Shutting down detector...")
        if self.sio.connected:
            self.sio.disconnect()
        self.camera.release()
        logging.info("Detector shutdown complete")

def main():
    parser = argparse.ArgumentParser(description="Raspberry Pi Object Detector")
    parser.add_argument("--server-host", default="security-server", 
                       help="Server hostname or IP address")
    parser.add_argument("--server-port", type=int, default=8080, 
                       help="Server port number")
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
    
    logging.info("Starting Raspberry Pi Object Detector")
    logging.info(f"Server: {args.server_host}:{args.server_port}")
    
    detector = RaspberryPiDetector(args.server_host, args.server_port)
    
    try:
        detector.process_and_send_frames()
    except KeyboardInterrupt:
        logging.info("Received shutdown signal")
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        detector.shutdown()

if __name__ == "__main__":
    main()