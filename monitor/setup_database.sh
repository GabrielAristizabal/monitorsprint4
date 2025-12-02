#!/bin/bash

# Script para configurar la base de datos LOGSEGURIDAD
# Ejecutar en la instancia EC2 donde está la base de datos

echo "Configurando base de datos LOGSEGURIDAD..."

# Variables de configuración (CAMBIAR según tu entorno)
DB_HOST="${DB_HOST:-localhost}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-}"

# Ejecutar script SQL
if [ -z "$DB_PASSWORD" ]; then
    mysql -h "$DB_HOST" -u "$DB_USER" < database/schema.sql
else
    mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" < database/schema.sql
fi

if [ $? -eq 0 ]; then
    echo "Base de datos LOGSEGURIDAD configurada correctamente"
else
    echo "Error configurando la base de datos"
    exit 1
fi

