#!/bin/bash

# Script de despliegue para instancia EC2
# Ejecutar en la instancia EC2 donde se desplegará el monitor

set -e

echo "Iniciando despliegue del microservicio de monitoreo..."

# Actualizar sistema
echo "Actualizando sistema..."
sudo yum update -y || sudo apt-get update -y

# Instalar Python 3 y pip si no están instalados
echo "Instalando Python 3 y dependencias..."
if command -v python3 &> /dev/null; then
    echo "Python 3 ya está instalado"
else
    sudo yum install -y python3 python3-pip || sudo apt-get install -y python3 python3-pip
fi

# Instalar MySQL client si no está instalado
if command -v mysql &> /dev/null; then
    echo "MySQL client ya está instalado"
else
    sudo yum install -y mysql || sudo apt-get install -y mysql-client
fi

# Crear directorio de aplicación
APP_DIR="/opt/monitor_service"
echo "Creando directorio de aplicación en $APP_DIR..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copiar archivos (asumiendo que ya están en el directorio actual)
echo "Copiando archivos..."
cp -r . $APP_DIR/

# Crear entorno virtual
echo "Creando entorno virtual..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Configurar archivo .env
if [ ! -f .env ]; then
    echo "Creando archivo .env desde ejemplo..."
    cp env.example .env
    echo ""
    echo "IMPORTANTE: Edita el archivo .env con las IPs y credenciales correctas:"
    echo "  nano $APP_DIR/.env"
    echo ""
    read -p "Presiona Enter después de editar el archivo .env..."
fi

# Configurar base de datos
echo "Configurando base de datos..."
chmod +x setup_database.sh
./setup_database.sh

# Crear servicio systemd
echo "Creando servicio systemd..."
sudo tee /etc/systemd/system/monitor-service.service > /dev/null <<EOF
[Unit]
Description=Microservicio de Monitoreo de Gestor de Pedidos
After=network.target mysql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Recargar systemd y habilitar servicio
sudo systemctl daemon-reload
sudo systemctl enable monitor-service.service

echo ""
echo "Despliegue completado!"
echo ""
echo "Para iniciar el servicio:"
echo "  sudo systemctl start monitor-service"
echo ""
echo "Para ver los logs:"
echo "  sudo journalctl -u monitor-service -f"
echo ""
echo "Para verificar el estado:"
echo "  sudo systemctl status monitor-service"
echo ""

