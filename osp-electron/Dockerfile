# Imagen oficial preparada para electron-builder con Wine (Windows builds)
FROM electronuserland/builder:wine

# Establecer directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto
COPY . .

# Instalar dependencias
RUN npm install
RUN npm install --save-dev electron-packager
RUN npm install --save-dev electron-builder

# Ejecutar electron-builder (instalador .exe)
RUN npm run build

# Contenedor termina aquí, el artefacto se guarda en /app/dist
CMD ["ls", "dist"]