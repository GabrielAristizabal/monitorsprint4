# Instrucciones de Despliegue - Microservicio de Monitoreo

## 📋 Resumen

Este microservicio monitorea el gestor de pedidos, registra todas las operaciones en la base de datos `LOGSEGURIDAD` y detecta intentos de escalamiento de privilegios indebido.

## 🚀 Pasos Rápidos de Despliegue

### 1. Subir archivos a la instancia EC2

```bash
# Desde tu máquina local, sube los archivos a EC2
scp -r monitor_service/ ec2-user@TU_IP_EC2:/home/ec2-user/
```

O usa Git:
```bash
# En la instancia EC2
git clone TU_REPOSITORIO
cd monitor_service
```

### 2. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar con las IPs reales
nano .env
```

**⚠️ IMPORTANTE:** Edita estas variables con las IPs de tus instancias:
- `GESTOR_DB_HOST` - IP privada de la instancia del gestor
- `LOG_DB_HOST` - IP donde está la BD de logs
- `GESTOR_API_URL` - URL de la API del gestor

Ver `CONFIGURACION_IPs.md` para más detalles.

### 3. Instalar dependencias

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 4. Configurar base de datos

```bash
# Dar permisos de ejecución
chmod +x setup_database.sh

# Ejecutar script (necesitas acceso a MySQL)
./setup_database.sh
```

O manualmente:
```bash
mysql -u root -p < database/schema.sql
```

### 5. Probar conectividad

```bash
# Ejecutar script de prueba
python test_connection.py
```

Este script verifica:
- ✅ Conexión a BD del gestor
- ✅ Conexión a BD de logs
- ✅ Conexión a API del gestor (opcional)

### 6. Iniciar el servicio

#### Opción A: Prueba manual
```bash
chmod +x start.sh
./start.sh
```

#### Opción B: Como servicio systemd (Recomendado para producción)
```bash
chmod +x deploy.sh
./deploy.sh
```

Luego:
```bash
sudo systemctl start monitor-service
sudo systemctl status monitor-service
```

## 🔍 Verificación

### Verificar que el servicio está corriendo

```bash
# Ver estado
sudo systemctl status monitor-service

# Ver logs en tiempo real
sudo journalctl -u monitor-service -f

# Probar endpoint de salud
curl http://localhost:5001/health
```

### Verificar logs en la base de datos

```bash
mysql -u log_user -p LOGSEGURIDAD

# Ver operaciones recientes
SELECT * FROM operaciones_log ORDER BY fecha_hora DESC LIMIT 10;

# Ver operaciones sospechosas
SELECT * FROM operaciones_log WHERE es_sospechosa = 1 ORDER BY fecha_hora DESC;
```

## 📊 Endpoints Disponibles

Una vez iniciado, el servicio expone estos endpoints:

- `GET /health` - Estado del servicio
- `POST /log` - Recibir logs del gestor
- `GET /logs` - Obtener logs registrados
- `GET /logs?suspicious_only=true` - Solo logs sospechosos
- `GET /stats` - Estadísticas de monitoreo

## 🔒 Configuración de Seguridad en AWS

### Security Groups

**En la instancia del Gestor:**
1. Permitir MySQL (puerto 3306) desde la IP privada del monitor
2. Permitir API (puerto 5000) desde la IP privada del monitor

**En la instancia del Monitor:**
1. Permitir API del monitor (puerto 5001) desde tu IP administrativa

### Usuarios de MySQL

Asegúrate de crear usuarios con permisos adecuados:

```sql
-- Usuario para que el monitor acceda a la BD del gestor (solo lectura)
CREATE USER 'monitor_read'@'IP_MONITOR' IDENTIFIED BY 'password';
GRANT SELECT ON pedidos.* TO 'monitor_read'@'IP_MONITOR';

-- Usuario para acceder a LOGSEGURIDAD
CREATE USER 'log_user'@'IP_MONITOR' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON LOGSEGURIDAD.* TO 'log_user'@'IP_MONITOR';

FLUSH PRIVILEGES;
```

## 🛠️ Comandos Útiles

### Reiniciar el servicio
```bash
sudo systemctl restart monitor-service
```

### Detener el servicio
```bash
sudo systemctl stop monitor-service
```

### Ver logs del servicio
```bash
sudo journalctl -u monitor-service -f
```

### Ver últimas 100 líneas de logs
```bash
sudo journalctl -u monitor-service -n 100
```

### Verificar configuración
```bash
# Ver variables de entorno cargadas
python -c "from config import Config; print(Config.GESTOR_DB_HOST)"
```

## 📝 Notas Importantes

1. **IPs Privadas vs Públicas**: 
   - Si el monitor y el gestor están en la misma VPC, usa IPs privadas
   - Si están en VPCs diferentes, necesitas VPC Peering o IPs públicas

2. **Intervalo de Monitoreo**:
   - Por defecto: 30 segundos
   - Cambiar en `.env`: `MONITOR_INTERVAL=60` (para 60 segundos)

3. **Base de Datos de Logs**:
   - Puede estar en la misma instancia que el gestor
   - O en una instancia separada
   - Solo asegúrate de que el monitor tenga acceso

4. **Detección de Operaciones Sospechosas**:
   - El monitor detecta automáticamente queries peligrosas
   - Se registran en `operaciones_log` con `es_sospechosa = 1`
   - También se pueden crear alertas en `alertas_seguridad`

## ❓ Troubleshooting

### El servicio no inicia
```bash
# Ver logs detallados
sudo journalctl -u monitor-service -n 50

# Verificar que Python puede importar módulos
python -c "import flask, pymysql, schedule"
```

### Error de conexión a base de datos
```bash
# Probar conexión manual
mysql -h IP_GESTOR -u usuario -p

# Verificar que MySQL escucha en todas las interfaces
# En el servidor MySQL:
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
# bind-address = 0.0.0.0
```

### El monitor no detecta operaciones
- Verifica que el intervalo de monitoreo no sea muy largo
- Revisa los logs del servicio
- Verifica que tenga acceso a la BD del gestor

## 📚 Documentación Adicional

- `README.md` - Documentación completa del proyecto
- `CONFIGURACION_IPs.md` - Guía detallada de configuración de IPs
- `database/schema.sql` - Esquema de la base de datos

## ✅ Checklist Final

Antes de considerar el despliegue completo:

- [ ] Archivo `.env` configurado con IPs reales
- [ ] Base de datos LOGSEGURIDAD creada
- [ ] Usuarios de MySQL creados con permisos adecuados
- [ ] Security Groups configurados en AWS
- [ ] `test_connection.py` ejecutado exitosamente
- [ ] Servicio iniciado y corriendo
- [ ] Endpoint `/health` responde correctamente
- [ ] Logs se están registrando en la base de datos
- [ ] Monitoreo periódico funcionando

