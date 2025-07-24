FROM nginx:1.25-alpine

# Instalar dependencias
RUN apk add --no-cache \
        curl \
        ca-certificates \
        nginx-mod-http-headers-more

# Directorios para logs y cache
RUN mkdir -p /var/log/nginx /var/cache/nginx /etc/nginx/ssl \
    && chown -R nginx:nginx /var/log/nginx /var/cache/nginx /etc/nginx/ssl

# Copiar configuraciones
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/    /etc/nginx/conf.d/

# Copiar certificados SSL
COPY ssl/mi_certificado.crt   /etc/nginx/ssl/mi_certificado.crt
COPY ssl/mi_clave_privada.key /etc/nginx/ssl/mi_clave_privada.key
RUN chmod 600 /etc/nginx/ssl/mi_*

# Health check
RUN echo '#!/bin/sh' > /health-check.sh \
 && echo 'curl -f http://localhost/health || exit 1' >> /health-check.sh \
 && chmod +x /health-check.sh

ENV PORT=80 \
    PORT_TLS=443
EXPOSE $PORT $PORT_TLS 

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD /health-check.sh

CMD ["nginx", "-g", "daemon off;"]