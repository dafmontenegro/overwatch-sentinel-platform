# Instrucciones de Prueba

## Arquitectura del Sistema

El sistema ahora está dividido en dos contenedores:

1. **Raspberry Pi Container** (`osp-raspberrypi`): 
   - Captura frames de la cámara
   - Ejecuta detección de objetos con TensorFlow Lite
   - Envía datos JSON al servidor de procesamiento
   - Puerto 8080 para endpoints de estado

2. **Processing Server Container** (`osp-processing-ms`):
   - Recibe frames y detecciones de la Raspberry Pi
   - Procesa la lógica de seguridad (zona segura, grabación)
   - Dibuja rectángulos y elementos visuales
   - Sirve el stream de video y API web
   - Puerto 8080 para interfaz web, puerto 8081 para recibir datos

## Estructura de Archivos

```
home/
├── docker-compose.yml
├── raspberry-pi/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pi_detector.py
│   └── test.mp4
├── processing-server/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── processing_server.py
├── events/          # Carpeta para videos (creada automáticamente)
└── logs/           # Carpeta para logs (creada automáticamente)
```

## Instrucciones de Prueba

### Construcción y Ejecución

```bash
# Construir las imágenes
docker-compose build

# Ejecutar en modo detached (segundo plano)
docker-compose up -d

# Ver los logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f osp-raspberrypi
docker-compose logs -f osp-processing-ms
```

### Verificación del Sistema

#### Endpoints de la Raspberry Pi (puerto 8080):
```bash
# Estado del servicio
curl http://localhost:8080/status

# Stream de video sin procesar (debugging)
open http://localhost:8080/raw_stream
```

#### Endpoints del Processing Server (puerto 8080):
```bash
# Estado del servidor
curl http://localhost:8080/status

# Stream de video procesado (principal)
open http://localhost:8080/stream

# Lista de eventos en JSON
curl http://localhost:8080/events | jq

# Reproducir un video específico
curl http://localhost:8080/video/[fecha]/[hora]/[archivo.avi]
```

### Prueba de Funcionalidad

1. **Verificar Stream Principal**:
   ```bash
   open http://localhost:8080/stream
   ```
   Deberías ver el video con:
   - Rectángulos rojos alrededor de personas/perros detectados
   - Rectángulo amarillo mostrando la zona segura
   - Timestamp en la esquina superior izquierda
   - FPS en la esquina inferior derecha
   - Círculo verde/rojo parpadeando (indicador de transmisión)

2. **Verificar Detección de Eventos**:
   ```bash
   # Verificar si se están creando eventos
   curl http://localhost:8080/events
   
   # Verificar estructura de carpetas
   ls -la events/
   ```

3. **Verificar Comunicación entre Contenedores**:
   ```bash
   # Logs del processing server deberían mostrar frames recibidos
   docker-compose logs osp-processing-ms | grep "process_frame"
   ```

### Prueba con Cámara Real

Para probar con una cámara USB real:

```bash
# Verificar cámaras disponibles
ls /dev/video*

# Modificar docker-compose.yml si es necesario:
# - /dev/video0:/dev/video0  # Cambiar por el dispositivo correcto
```

### Prueba en Red (Dos Dispositivos)

Para probar en dispositivos separados:

1. **En la Raspberry Pi**:
   ```bash
   # Modificar docker-compose.yml o variables de entorno
   export PROCESSING_SERVER_HOST=192.168.1.100  # IP del otro dispositivo
   
   # Ejecutar solo el contenedor de raspberry
   docker-compose up osp-raspberrypi
   ```

2. **En el Servidor de Procesamiento**:
   ```bash
   # Ejecutar solo el contenedor de procesamiento
   docker-compose up osp-processing-ms
   ```

### Comandos Útiles de Depuración

```bash
# Reiniciar servicios
docker-compose restart

# Ver uso de recursos
docker stats

# Ejecutar bash en un contenedor
docker-compose exec osp-raspberrypi bash
docker-compose exec osp-processing-ms bash

# Verificar conectividad de red entre contenedores
docker-compose exec osp-raspberrypi ping osp-processing-ms
docker-compose exec osp-processing-ms ping osp-raspberrypi

# Limpiar todo
docker-compose down
docker system prune -a
```

### Resultados Esperados

- **Stream principal**: `http://localhost:8080/stream`
- **API de eventos**: `http://localhost:8080/events`
- **Videos guardados**: En la carpeta `events/` organizados por fecha y hora
- **Logs**: En la carpeta `logs/` y también accesibles via `docker-compose logs`

El sistema debería mostrar detección en tiempo real, grabación automática cuando se detecta invasión de la zona segura, y una API JSON para acceder a los eventos grabados.