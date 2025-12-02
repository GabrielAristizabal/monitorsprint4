#!/bin/bash

# Script simple para iniciar el monitor manualmente
# Útil para pruebas antes de configurar como servicio systemd

echo "Iniciando microservicio de monitoreo..."

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Verificar que existe .env
if [ ! -f .env ]; then
    echo "ERROR: Archivo .env no encontrado"
    echo "Copia env.example a .env y configura las variables:"
    echo "  cp env.example .env"
    echo "  nano .env"
    exit 1
fi

# Iniciar el servicio
python main.py

