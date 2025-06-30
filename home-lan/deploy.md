# Guía de Despliegue - Sistema de Seguridad Distribuido

## Arquitectura del Sistema

El sistema ahora está dividido en dos componentes principales:

1. **Raspberry Pi (osp-raspberrypi-ms)**: Captura de video y detección de objetos
2. **MacBook Server (osp-home-ms)**: Procesamiento de video, grabación y interfaz web

## Comunicación

- **Protocolo**: Socket.IO sobre HTTP
- **Puerto**: 9999
- **Datos transmitidos**: Frames codificados en base64 + metadatos de detección

## Despliegue

### 1. MacBook Server (Ejecutar primero)

```bash
# Clonar archivos del servidor
cd /ruta/del/servidor
docker-compose up -d --build

# O manualmente:
docker build -t osp-home-ms .
docker run -d \
  --name security-server \
  -p 8080:8080 \
  -p 9999:9999 \
  -v $(pwd)/events:/app/events \
  -v $(pwd)/logs:/app/logs \
  -e ALLOWED_HOSTS=overwatch-sentinel-platform.local \
  osp-home-ms
```

### 2. Raspberry Pi (Ejecutar después)

```bash
# Clonar archivos de la Raspberry Pi
cd /ruta/del/detector
docker-compose up -d --build

# O manualmente:
docker build -t osp-raspberrypi-ms .
docker run -d \
  --name raspberry-detector \
  --privileged \
  --device /dev/video0:/dev/video0 \
  -v $(pwd)/logs:/app/logs \
  -e SERVER_HOST=macbook-air-5-2.local \
  -e SERVER_PORT=9999 \
  osp-raspberrypi-ms
```

### 3. Configuración de Red

Asegúrate de que ambos dispositivos estén en la misma red y puedan comunicarse:

```bash
# Desde la Raspberry Pi, verificar conectividad
ping macbook-air-5-2.local

# Desde el MacBook, verificar que el puerto esté abierto
netstat -an | grep 9999
```

## Endpoints Disponibles

### MacBook Server (puerto 8080)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Stream de video en tiempo real |
| `/events` | GET | Lista de eventos en formato JSON |
| `/status` | GET | Estado del sistema y estadísticas |
| `/health` | GET | Health check del servidor |

### Ejemplos de Uso

#### 1. Ver stream de video
```bash
# Navegador web
http://macbook-air-5-2.local:8080/

# O usando curl para verificar
curl -I http://macbook-air-5-2.local:8080/
```

#### 2. Obtener eventos grabados
```bash
curl http://macbook-air-5-2.local:8080/events | jq
```

Respuesta ejemplo:
```json
{
  "events": [
    {
      "date": "December17",
      "hours": [
        {
          "time": "14hr",
          "videos": [
            {
              "filename": "December17_14hr_30min15sec.avi",
              "display_name": "14hr_30min15sec",
              "path": "December17/14hr/December17_14hr_30min15sec.avi",
              "size": 1048576,
              "modified": 1703087415.0
            }
          ]
        }
      ]
    }
  ],
  "total_days": 1,
  "total_videos": 1
}
```

#### 3. Verificar estado del sistema
```bash
curl http://macbook-air-5-2.local:8080/status | jq
```

Respuesta ejemplo:
```json
{
  "status": "running",
  "uptime": 3600.5,
  "frames_processed": 86400,
  "recording_active": false,
  "last_detections": 2,
  "cpu_cores": 8
}
```

## Verificación del Sistema

### 1. Logs del Sistema

```bash
# Logs del servidor
docker logs security-server

# Logs de la Raspberry Pi
docker logs raspberry-detector

# Logs persistentes
tail -f ./logs/server.log
tail -f ./logs/detector.log
```

### 2. Verificar Comunicación Socket.IO

```bash
# Instalar herramientas de debug
npm install -g socket.io-client-tool

# Conectar al servidor
socket-io-client http://macbook-air-5-2.local:9999
```

### 3. Monitoreo de Performance

```bash
# Uso de CPU y memoria
docker stats security-server
docker stats raspberry-detector

# Espacio en disco (eventos)
du -sh ./events/
```

## Configuración Avanzada

### 1. Personalizar Detección

Editar en `raspberry_pi_detector.py`:
```python
self.object_detector = ObjectDetector(
    num_threads=self.cpu_count,
    score_threshold=0.5,          # Umbral de confianza
    max_results=3,                # Máximo detecciones por frame
    category_name_allowlist=["person", "dog", "cat"]  # Objetos a detectar
)
```

### 2. Configurar Zona Segura

Editar en `security_server.py`:
```python
self.safe_zone_coords = ((880, 360), (1280, 720))  # (x1,y1), (x2,y2)
```

### 3. Ajustar Grabación

```python
self.detection_timeout = 3  # Segundos sin detección para parar grabación
min_video_duration = 1      # Duración mínima del video
max_video_duration = 60     # Duración máxima del video
```

## Optimizaciones Implementadas

### Raspberry Pi
- **Carga optimizada de video de prueba**: Los frames se cargan una sola vez en memoria
- **Detección de hardware**: Uso automático de todos los cores de CPU disponibles
- **Reconexión automática**: Reintenta conexión con backoff exponencial
- **Compresión de video**: JPEG con 85% de calidad para transmisión

### MacBook Server
- **Procesamiento en memoria**: Sin acceso a disco durante streaming
- **Buffer inteligente**: Solo graba cuando hay detecciones
- **JSON optimizado**: Estructura eficiente para listado de eventos
- **Streaming HTTP**: Multipart response para video en tiempo real

## Troubleshooting

### Problemas Comunes

1. **Raspberry Pi no conecta al servidor**
   ```bash
   # Verificar DNS
   nslookup macbook-air-5-2.local
   
   # Verificar puerto
   telnet macbook-air-5-2.local 9999
   ```

2. **Cámara no detectada**
   ```bash
   # Listar dispositivos de video
   ls -la /dev/video*
   
   # Verificar permisos
   docker run --rm --privileged osp-raspberrypi-ms ls -la /dev/video0
   ```

3. **Problemas de memoria**
   ```bash
   # Verificar memoria disponible
   free -h
   
   # Ajustar límites de Docker
   docker run --memory=1g --cpus=2 osp-raspberrypi-ms
   ```

4. **Videos no se graban**
   ```bash
   # Verificar permisos de directorio
   ls -la ./events/
   
   # Verificar espacio en disco
   df -h
   ```

## Configuraciones de Red

### Para usar IP fija en lugar de hostname:

```bash
# Raspberry Pi
docker run -e SERVER_HOST=192.168.1.100 osp-raspberrypi-ms

# Servidor
docker run -e ALLOWED_HOSTS=192.168.1.50 osp-home-ms
```

### Para múltiples Raspberry Pis:

El servidor puede manejar múltiples conexiones simultáneamente. Cada Raspberry Pi debe configurarse con la misma dirección del servidor:

```bash
# Raspberry Pi #1
docker run -e SERVER_HOST=macbook-air-5-2.local --name detector-1 osp-raspberrypi-ms

# Raspberry Pi #2  
docker run -e SERVER_HOST=macbook-air-5-2.local --name detector-2 osp-raspberrypi-ms
```

El servidor automáticamente manejará múltiples streams y los distinguirá por Socket.IO session ID.