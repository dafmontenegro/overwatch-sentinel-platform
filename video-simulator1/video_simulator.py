import cv2
import time
import threading
from flask import Flask, Response, render_template
from flask_cors import CORS


class Camera:
    def __init__(self, video_source=0, width=640, height=480):
        # Usar cámara o archivo de video
        self.video_capture = cv2.VideoCapture(video_source)
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.width = width
        self.height = height
        
        # Si no se puede abrir la cámara, crear un frame negro
        if not self.video_capture.isOpened():
            self.frame = self.create_blank_frame()
        else:
            _, self.frame = self.video_capture.read()
            
        self.stopped = False
        
    def create_blank_frame(self):
        return cv2.rectangle(
            cv2.putText(
                cv2.rectangle(
                    cv2.resize(
                        cv2.cvtColor(
                            cv2.imread("placeholder.jpg") if cv2.imread("placeholder.jpg") is not None else 
                            cv2.imread("placeholder.png") if cv2.imread("placeholder.png") is not None else
                            255 * cv2.ones((self.height, self.width, 3), dtype=cv2.CV_8UC3),
                            cv2.COLOR_BGR2RGB if cv2.imread("placeholder.jpg") is not None or cv2.imread("placeholder.png") is not None else cv2.COLOR_RGB2BGR
                        ),
                        (self.width, self.height)
                    ),
                    (0, 0), (self.width, self.height), (0, 0, 0), 2
                ),
                "No camera detected", (50, self.height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
            ),
            (0, 0), (self.width, self.height), (0, 0, 0), 2
        )
    
    def start(self):
        threading.Thread(target=self.update, daemon=True).start()
        return self
    
    def update(self):
        while not self.stopped:
            if not self.video_capture.isOpened():
                self.stopped = True
                return
            
            ret, frame = self.video_capture.read()
            if not ret:
                self.stopped = True
                return
            
            # Añadir timestamp al frame
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # Añadir un indicador de transmisión en vivo
            cv2.circle(frame, (frame.shape[1] - 20, 20), 10, (0, 0, 255), -1)
            
            self.frame = frame
            time.sleep(0.01)  # Pequeña pausa para reducir uso de CPU
    
    def read(self):
        return self.frame
    
    def stop(self):
        self.stopped = True
        if self.video_capture.isOpened():
            self.video_capture.release()

# Inicializar Flask
app = Flask(__name__)
CORS(app) # Habilitar CORS para permitir solicitudes de otros dominios

# Inicializar cámara
# Puedes cambiar 0 por la ruta a un archivo de video para simular con un video pregrabado
camera = Camera(0, 640, 480).start()

def generate_frames():
    """Generador que produce frames para la transmisión HTTP"""
    while True:
        frame = camera.read()
        
        # Codificar el frame en JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
            
        # Convertir a formato de respuesta HTTP
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def home():
    """Página de inicio"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simulador de Video en Vivo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin-top: 50px;
            }
            h1 {
                color: #333;
            }
            .btn {
                display: inline-block;
                background-color: #4CAF50;
                color: white;
                padding: 15px 25px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 20px;
                cursor: pointer;
                border-radius: 5px;
                transition: background-color 0.3s;
            }
            .btn:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <h1>Simulador de Video en Vivo</h1>
        <a href="/video" class="btn">Ver Transmisión en Vivo</a>
    </body>
    </html>
    """

@app.route('/video')
def video():
    """Endpoint para la transmisión de video"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)
    finally:
        camera.stop()