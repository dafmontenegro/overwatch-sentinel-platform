#!/bin/bash

# Script para configurar la red compartida entre dispositivos

echo "Configurando red de seguridad..."

# Crear la red si no existe
docker network ls | grep -q security-network || docker network create security-network

echo "Red configurada correctamente"
echo "Red: security-network"
echo "Para verificar: docker network inspect security-network"