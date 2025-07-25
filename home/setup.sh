#!/bin/bash

echo "=== Configuración inicial del Sistema de Seguridad Multi-PI ==="

# Crear estructura de carpetas
echo "📁 Creando estructura de carpetas..."
mkdir -p processing-server raspberry-pi events logs

# Verificar que los archivos principales existen
echo "🔍 Verificando archivos necesarios..."

# Archivos del servidor de procesamiento
if [ ! -f "processing-server/processing_server.py" ]; then
    echo "❌ Falta: processing-server/processing_server.py"
    MISSING=true
fi

if [ ! -f "processing-server/config_ps.py" ]; then
    echo "❌ Falta: processing-server/config_ps.py"
    MISSING=true
fi

if [ ! -f "processing-server/requirements.txt" ]; then
    echo "❌ Falta: processing-server/requirements.txt"
    MISSING=true
fi

# Archivos de Raspberry Pi
if [ ! -f "raspberry-pi/pi_detector.py" ]; then
    echo "❌ Falta: raspberry-pi/pi_detector.py"
    MISSING=true
fi

if [ ! -f "raspberry-pi/config_rp.py" ]; then
    echo "❌ Falta: raspberry-pi/config_rp.py"
    MISSING=true
fi

if [ ! -f "raspberry-pi/requirements.txt" ]; then
    echo "❌ Falta: raspberry-pi/requirements.txt"
    MISSING=true
fi

# Archivos Docker
if [ ! -f "Dockerfile.processing" ]; then
    echo "❌ Falta: Dockerfile.processing"
    MISSING=true
fi

if [ ! -f "Dockerfile.pi" ]; then
    echo "❌ Falta: Dockerfile.pi"
    MISSING=true
fi

if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Falta: docker-compose.yml"
    MISSING=true
fi

if [ "$MISSING" = true ]; then
    echo ""
    echo "❌ Faltan archivos necesarios. Por favor, asegúrate de tener todos los archivos en su lugar."
    echo ""
    echo "Estructura esperada:"
    echo "home/"
    echo "├── processing-server/"
    echo "│   ├── processing_server.py"
    echo "│   ├── config_ps.py"
    echo "│   └── requirements.txt"
    echo "├── raspberry-pi/"
    echo "│   ├── pi_detector.py"
    echo "│   ├── config_rp.py"
    echo "│   ├── requirements.txt"
    echo "│   └── test.mp4 (opcional)"
    echo "├── Dockerfile.processing"
    echo "├── Dockerfile.pi"
    echo "├── docker-compose.yml"
    echo "├── Makefile"
    echo "└── README.md"
    exit 1
fi

echo "✅ Todos los archivos necesarios están presentes"

# Crear video de prueba si no existe
if [ ! -f "raspberry-pi/test.mp4" ]; then
    echo "🎥 Creando video de prueba..."
    if command -v ffmpeg &> /dev/null; then
        ffmpeg -f lavfi -i testsrc=duration=30:size=1280x720:rate=24 -c:v libx264 -y raspberry-pi/test.mp4
        echo "✅ Video de prueba creado: raspberry-pi/test.mp4"
    else
        echo "⚠️  ffmpeg no encontrado. El sistema usará la cámara virtual de OpenCV."
        echo "   Para crear un video de prueba manualmente:"
        echo "   ffmpeg -f lavfi -i testsrc=duration=30:size=1280x720:rate=24 -c:v libx264 raspberry-pi/test.mp4"
    fi
fi

echo ""
echo "🚀 Sistema listo para usar!"
echo ""
echo "Próximos pasos:"
echo "1. make build    # Construir imágenes Docker"
echo "2. make up       # Iniciar servicios"
echo "3. make logs     # Ver logs en tiempo real"
echo "4. make urls     # Ver URLs del sistema"
echo ""
echo "Para más comandos: make help"