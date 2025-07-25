# Makefile para el sistema de seguridad multi-PI

# Construir todas las imágenes
build:
	docker-compose build

# Iniciar todos los servicios
up:
	docker-compose up -d

# Ver logs en tiempo real
logs:
	docker-compose logs -f

# Ver logs de un servicio específico
logs-processing:
	docker-compose logs -f processing-server

logs-pi1:
	docker-compose logs -f pi1

logs-pi2:
	docker-compose logs -f pi2

# Parar todos los servicios
down:
	docker-compose down

# Parar y limpiar todo (incluyendo volúmenes)
clean:
	docker-compose down -v
	docker system prune -f

# Ver estado de los servicios
status:
	docker-compose ps

# Reconstruir y reiniciar
restart:
	docker-compose down
	docker-compose build
	docker-compose up -d

# Conectarse al contenedor del servidor de procesamiento
shell-processing:
	docker exec -it processing-server /bin/bash

# Conectarse al contenedor de pi1
shell-pi1:
	docker exec -it pi1 /bin/bash

# Conectarse al contenedor de pi2
shell-pi2:
	docker exec -it pi2 /bin/bash

# Ver recursos utilizados
stats:
	docker stats

# Crear video de prueba simple (requiere ffmpeg instalado localmente)
create-test-video:
	@mkdir -p raspberry-pi
	ffmpeg -f lavfi -i testsrc=duration=30:size=1280x720:rate=24 -c:v libx264 raspberry-pi/test.mp4

# Crear estructura de carpetas necesaria
setup:
	@mkdir -p processing-server raspberry-pi events logs
	@echo "Estructura de carpetas creada"
	@echo "Asegúrate de copiar los archivos correspondientes a cada carpeta:"
	@echo "  processing-server/: processing_server.py, config_ps.py, requirements.txt"
	@echo "  raspberry-pi/: pi_detector.py, config_rp.py, requirements.txt, test.mp4"

# Verificar estructura de archivos
check:
	@echo "=== Verificando estructura de archivos ==="
	@echo "Processing Server:"
	@ls -la processing-server/ 2>/dev/null || echo "  ❌ Carpeta processing-server no encontrada"
	@echo ""
	@echo "Raspberry Pi:"
	@ls -la raspberry-pi/ 2>/dev/null || echo "  ❌ Carpeta raspberry-pi no encontrada"
	@echo ""
	@echo "Archivos Docker:"
	@ls -la Dockerfile.* docker-compose.yml 2>/dev/null || echo "  ❌ Dockerfiles no encontrados"

# URLs útiles para testing
urls:
	@echo "=== URLs del Sistema ==="
	@echo "Servidor de Procesamiento: http://localhost:8080"
	@echo "  Status: http://localhost:8080/status"
	@echo "  Stream: http://localhost:8080/stream"
	@echo "  Eventos: http://localhost:8080/events"
	@echo ""
	@echo "Pi1: http://localhost:8081"
	@echo "  Status: http://localhost:8081/status"
	@echo ""
	@echo "Pi2: http://localhost:8082"
	@echo "  Status: http://localhost:8082/status"

# Ayuda
help:
	@echo "Comandos disponibles:"
	@echo "  setup          - Crear estructura de carpetas"
	@echo "  check          - Verificar archivos necesarios"
	@echo "  build          - Construir imágenes Docker"
	@echo "  up             - Iniciar servicios"
	@echo "  down           - Parar servicios"
	@echo "  restart        - Reiniciar todo el sistema"
	@echo "  logs           - Ver logs de todos los servicios"
	@echo "  logs-*         - Ver logs de un servicio específico"
	@echo "  shell-*        - Conectar a shell de un contenedor"
	@echo "  status         - Ver estado de servicios"
	@echo "  stats          - Ver uso de recursos"
	@echo "  clean          - Limpiar todo (datos incluidos)"
	@echo "  urls           - Mostrar URLs del sistema"
	@echo "  create-test-video - Crear video de prueba"

.PHONY: build up logs logs-processing logs-pi1 logs-pi2 down clean status restart shell-processing shell-pi1 shell-pi2 stats create-test-video setup check urls help