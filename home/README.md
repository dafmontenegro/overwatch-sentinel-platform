# Sistema de Seguridad Multi-PI con Docker

Este sistema simula un entorno de seguridad con múltiples Raspberry Pi enviando datos a un servidor de procesamiento central.

## Estructura del Proyecto

```
home/
├── processing-server/
│   ├── processing_server.py
│   ├── config_ps.py
│   └── requirements.txt
├── raspberry-pi/
│   ├── pi_detector.py
│   ├── config_rp.py
│   ├── requirements.txt
│   └── test.mp4              # Video de prueba (opcional)
├── Dockerfile.processing      # Imagen del servidor de procesamiento
├── Dockerfile.pi             # Imagen de Raspberry Pi simulada
├── docker-compose.yml        # Configuración de servicios
├── Makefile                  # Comandos útiles
├── README.md
├── events/                   # Carpeta de eventos (se crea automáticamente)
└── logs/                     # Carpeta de logs (se crea automáticamente)
```

## Servicios

- **processing-server**: Puerto 8080 - Servidor central de procesamiento
- **pi1**: Puerto 8081 - Raspberry Pi 1 simulada
- **pi2**: Puerto 8082 - Raspberry Pi 2 simulada

## Instalación y Uso

### 1. Preparar el entorno

```bash
# Crear video de prueba (opcional)
make create-test-video

# O usar cualquier video MP4 de 1280x720 y colocarlo en raspberry-pi/test.mp4
cp tu_video.mp4 raspberry-pi/test.mp4
```

### 2. Construir y ejecutar

```bash
# Construir todas las imágenes
make build

# Iniciar todos los servicios
make up

# Ver logs en tiempo real
make logs
```

### 3. Verificar funcionamiento

```bash
# Ver estado de servicios
make status

# Ver URLs importantes
make urls
```

## URLs del Sistema

### Servidor de Procesamiento (Puerto 8080)
- **Principal**: http://localhost:8080
- **Status**: http://localhost:8080/status
- **Stream de video**: http://localhost:8080/stream
- **Eventos grabados**: http://localhost:8080/events
- **Stream PI específica**: http://localhost:8080/stream/pi1

### Raspberry Pi 1 (Puerto 8081)
- **Principal**: http://localhost:8081
- **Status**: http://localhost:8081/status
- **Logs**: http://localhost:8081/logs

### Raspberry Pi 2 (Puerto 8082)
- **Principal**: http://localhost:8082
- **Status**: http://localhost:8082/status
- **Logs**: http://localhost:8082/logs

## Comandos Útiles

```bash
# Ver logs específicos
make logs-processing
make logs-pi1
make logs-pi2

# Acceder a shell de contenedores
make shell-processing
make shell-pi1
make shell-pi2

# Reiniciar sistema completo
make restart

# Parar servicios
make down

# Limpiar todo (incluyendo volúmenes)
make clean

# Ver recursos utilizados
make stats
```

## Configuración

### Zona Segura
En `processing-server/config_ps.py`:
```python
SAFE_ZONE_START = (640, 0)    # Mitad derecha de la pantalla
SAFE_ZONE_END = (1280, 720)
```

### Raspberry PIs
En `processing-server/config_ps.py`:
```python
RASPBERRY_PI_IDS = ["pi1", "pi2"]  # Agregar más PIs aquí
```

### Servidor de Procesamiento
En `raspberry-pi/config_rp.py`:
```python
PROCESSING_SERVER_HOSTNAME = os.getenv("PROCESSING_SERVER_HOSTNAME", "http://localhost:8080")
```

## Persistencia de Datos

- **Eventos**: Se guardan en `./events/` (volume Docker)
- **Logs**: Se guardan en `./logs/` (volume Docker)

## Detección de Objetos

El sistema detecta:
- Personas (`person`)
- Bicicletas (`bicycle`)

Con un threshold de confianza mínimo del 50%.

## Grabación de Eventos

- **Duración mínima**: 2 segundos
- **Duración máxima**: 10 segundos  
- **Delay sin detección**: 3 segundos para finalizar grabación
- **Formato**: MP4 con codec H.264

## Archivos de Configuración por Carpeta

### processing-server/
- `processing_server.py` - Servidor principal
- `config_ps.py` - Configuración del servidor
- `requirements.txt` - Dependencias del servidor

### raspberry-pi/
- `pi_detector.py` - Detector de la Raspberry Pi
- `config_rp.py` - Configuración de la Pi
- `requirements.txt` - Dependencias de la Pi
- `test.mp4` - Video de prueba (opcional)

## Troubleshooting

### Problema: No hay detecciones
```bash
# Verificar que el modelo se descargó correctamente
make shell-pi1
ls -la efficientdet_lite0.tflite
```

### Problema: Error de ffmpeg
```bash
# Verificar instalación de ffmpeg en el contenedor
make shell-processing
ffmpeg -version
```

### Problema: No se conectan las PIs
```bash
# Verificar red Docker
docker network ls
docker network inspect security-network_security-network
```

### Ver logs detallados
```bash
# Logs completos con timestamps
docker-compose logs --timestamps

# Seguir logs de un servicio específico
docker-compose logs -f processing-server
```

## Desarrollo

Para agregar una nueva Raspberry Pi:

1. Agregar el ID en `processing-server/config_ps.py`:
```python
RASPBERRY_PI_IDS = ["pi1", "pi2", "pi3"]
```

2. Agregar servicio en `docker-compose.yml`:
```yaml
pi3:
  build:
    context: .
    dockerfile: Dockerfile.pi
  container_name: pi3
  ports:
    - "8083:8080"
  environment:
    - PROCESSING_SERVER_HOSTNAME=http://processing-server:8080
    - PI_ID=pi3
  networks:
    - security-network
```

3. Reiniciar el sistema:
```bash
make restart
```

## Estructura de Archivos Requerida

Asegúrate de tener esta estructura antes de ejecutar:

```bash
# Crear estructura básica
mkdir -p processing-server raspberry-pi events logs

# Verificar archivos requeridos
ls processing-server/  # Debe contener: processing_server.py, config_ps.py, requirements.txt
ls raspberry-pi/       # Debe contener: pi_detector.py, config_rp.py, requirements.txt
```