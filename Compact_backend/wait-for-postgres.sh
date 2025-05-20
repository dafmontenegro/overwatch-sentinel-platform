#!/bin/sh

set -e

host="$1"
shift  # Elimina el primer argumento (host) para manejar el resto como el comando

echo "Esperando a PostgreSQL en $host..."

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "PostgreSQL no está disponible aún - esperando..."
  sleep 1
done

>&2 echo "PostgreSQL está listo - ejecutando el comando: $@"
exec "$@"  # Ejecuta el resto de los argumentos como comando