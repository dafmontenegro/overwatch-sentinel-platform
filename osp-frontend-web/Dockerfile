FROM node:18-alpine AS base

# Instalar dependencias necesarias para Alpine
RUN apk add --no-cache libc6-compat

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración de dependencias
COPY package*.json ./
COPY yarn.lock* ./

# Instalar dependencias
RUN npm ci --only=production && npm cache clean --force

# Etapa de construcción
FROM base AS builder
WORKDIR /app

# Copiar archivos de configuración
COPY package*.json ./
COPY yarn.lock* ./

# Instalar todas las dependencias (incluyendo devDependencies)
RUN npm ci

# Copiar código fuente
COPY . .

# Variables de entorno para el build
COPY .env .

# Construir la aplicación
RUN npm run build

# Etapa de producción
FROM node:18-alpine AS runner
WORKDIR /app

# Crear usuario no-root para seguridad
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copiar archivos necesarios desde la etapa de construcción
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/server.js ./
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/index.html ./

# Instalar solo dependencias de producción
RUN npm ci --only=production && npm cache clean --force

# Cambiar ownership de los archivos
RUN chown -R nextjs:nodejs /app
USER nextjs

# Exponer puerto
EXPOSE 5173

# Variables de entorno
ENV NODE_ENV=production
ENV PORT=5173

# Comando para iniciar la aplicación
CMD ["node", "server.js"]