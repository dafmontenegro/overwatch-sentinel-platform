FROM nginx:1.25-alpine

# Instalar dependencias
RUN apk add --no-cache curl ca-certificates nginx-mod-http-headers-more

# Crear directorios necesarios
RUN mkdir -p /var/log/nginx /var/cache/nginx

# Copiar configuraciones
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# Establecer permisos
RUN chown -R nginx:nginx /var/log/nginx /var/cache/nginx

# Script de health check
RUN echo '#!/bin/sh' > /health-check.sh && \
    echo 'curl -f http://localhost/health || exit 1' >> /health-check.sh && \
    chmod +x /health-check.sh

EXPOSE 80

# NO VERIFICAR CONFIGURACIÓN DURANTE BUILD
# RUN nginx -t  # COMENTAR ESTA LÍNEA

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /health-check.sh

CMD ["nginx", "-g", "daemon off;"]