# Microservicio de Monitoreo - Gestor de Pedidos

Microservicio diseñado para monitorear todas las operaciones del gestor de pedidos, registrar logs en la base de datos `LOGSEGURIDAD` y detectar intentos de escalamiento de privilegios indebido.

## Características

- ✅ Monitoreo continuo de operaciones de base de datos
- ✅ Detección automática de operaciones sospechosas (escalamiento de privilegios)
- ✅ Registro de todos los movimientos en base de datos `LOGSEGURIDAD`
- ✅ API REST para consultar logs y estadísticas
- ✅ Alertas de seguridad por nivel (BAJA, MEDIA, ALTA, CRITICA)
- ✅ Monitoreo periódico configurable

## Operaciones Permitidas vs Sospechosas

### Operaciones Permitidas
- `SELECT` - Para generar reportes
- `INSERT INTO pedidos` - Para crear pedidos
- `UPDATE pedidos` - Para actualizar pedidos
- Acceso a tablas: `pedidos`, `productos`, `clientes`, `reportes`

### Operaciones Sospechosas (Detección de Escalamiento de Privilegios)
- `DROP TABLE/DATABASE` - Eliminación de estructuras
- `ALTER TABLE` - Modificación de estructura
- `GRANT/REVOKE` - Manipulación de privilegios
- `CREATE/DROP USER` - Gestión de usuarios
- Acceso a tablas del sistema: `INFORMATION_SCHEMA`, `mysql.*`, `performance_schema`
- `DELETE` no autorizado
- Cualquier operación fuera de las tablas permitidas

## Requisitos Previos

- Python 3.8+
- MySQL 5.7+ o MariaDB 10.3+
- Acceso a la base de datos del gestor de pedidos
- Acceso a la instancia EC2 del gestor (opcional, para monitoreo de API)

## Instalación y Configuración

### 1. Configurar Variables de Entorno

Copia el archivo `.env.example` a `.env` y edita las siguientes variables:

```bash
cp .env.example .env
nano .env
```

### Variables a Configurar (IMPORTANTE - CAMBIAR IPs):

```env
# IP de la instancia EC2 del gestor de pedidos (IP privada o pública)
GESTOR_DB_HOST=172.31.XX.XX

# IP de la instancia donde está la BD de logs (puede ser la misma o diferente)
LOG_DB_HOST=172.31.XX.XX

# IP de la API del gestor (IP pública o privada de la instancia EC2)
GESTOR_API_URL=http://172.31.XX.XX:5000
```

**Nota**: Reemplaza `172.31.XX.XX` con las IPs reales de tus instancias EC2.

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar Base de Datos

Ejecuta el script SQL para crear la base de datos `LOGSEGURIDAD`:

```bash
chmod +x setup_database.sh
./setup_database.sh
```

O manualmente:

```bash
mysql -u root -p < database/schema.sql
```

### 4. Ejecutar el Servicio

#### Opción A: Ejecución Directa

```bash
python main.py
```

#### Opción B: Usando Docker

```bash
docker-compose up -d
```

#### Opción C: Despliegue en EC2 (Recomendado)

```bash
chmod +x deploy.sh
./deploy.sh
```

Luego inicia el servicio:

```bash
sudo systemctl start monitor-service
sudo systemctl status monitor-service
```

## Uso

### Endpoints de la API

#### Health Check
```bash
GET http://localhost:5001/health
```

#### Recibir Logs del Gestor
```bash
POST http://localhost:5001/log
Content-Type: application/json

{
  "operation_type": "CREATE_ORDER",
  "details": {
    "order_id": 123,
    "user": "admin",
    "ip_origen": "192.168.1.1"
  },
  "is_suspicious": false
}
```

#### Obtener Logs
```bash
# Todos los logs (últimos 100)
GET http://localhost:5001/logs

# Solo logs sospechosos
GET http://localhost:5001/logs?suspicious_only=true

# Limitar cantidad
GET http://localhost:5001/logs?limit=50
```

#### Obtener Estadísticas
```bash
GET http://localhost:5001/stats
```

### Integración con el Gestor de Pedidos

Para que el gestor de pedidos envíe logs al monitor, agrega en el código del gestor:

```python
import requests

def log_operation(operation_type, details, is_suspicious=False):
    try:
        requests.post(
            'http://MONITOR_IP:5001/log',
            json={
                'operation_type': operation_type,
                'details': details,
                'is_suspicious': is_suspicious
            },
            timeout=2
        )
    except:
        pass  # No fallar si el monitor no está disponible
```

## Estructura de la Base de Datos

### Tabla: `operaciones_log`
- `id`: ID único
- `fecha_hora`: Timestamp de la operación
- `tipo_operacion`: Tipo de operación realizada
- `detalles`: JSON con detalles de la operación
- `es_sospechosa`: Boolean indicando si es sospechosa
- `ip_origen`: IP de origen
- `usuario`: Usuario que realizó la operación

### Tabla: `alertas_seguridad`
- Almacena alertas generadas por operaciones sospechosas
- Niveles: BAJA, MEDIA, ALTA, CRITICA

### Tabla: `reglas_monitoreo`
- Configuración de reglas de detección
- Permite personalizar qué se considera sospechoso

## Monitoreo y Logs

### Ver logs del servicio (systemd)
```bash
sudo journalctl -u monitor-service -f
```

### Ver logs del servicio (Docker)
```bash
docker logs -f monitor-service
```

### Consultar operaciones sospechosas en la BD
```sql
SELECT * FROM LOGSEGURIDAD.operaciones_log 
WHERE es_sospechosa = 1 
ORDER BY fecha_hora DESC;
```

## Configuración de Seguridad en EC2

### Security Groups

Asegúrate de configurar los Security Groups en AWS:

1. **Gestor de Pedidos**:
   - Puerto 3306 (MySQL) - Solo desde el monitor
   - Puerto 5000 (API) - Desde el monitor y clientes

2. **Monitor**:
   - Puerto 5001 (API Monitor) - Desde administradores
   - Puerto 3306 (MySQL) - Para acceder a LOGSEGURIDAD

### Ejemplo de Security Group Rules

```
Monitor -> Gestor DB: 
  Type: MySQL/Aurora
  Port: 3306
  Source: IP privada del monitor

Monitor -> Gestor API:
  Type: Custom TCP
  Port: 5000
  Source: IP privada del monitor
```

## Troubleshooting

### El monitor no puede conectar a la BD del gestor
- Verifica las IPs en `.env`
- Verifica Security Groups en AWS
- Verifica credenciales de base de datos
- Verifica que MySQL esté escuchando en la IP correcta

### No se detectan operaciones sospechosas
- Verifica que el monitor esté ejecutándose
- Revisa los logs del servicio
- Verifica la configuración de `MONITOR_INTERVAL`

### El servicio no inicia
- Verifica que Python 3 esté instalado
- Verifica que todas las dependencias estén instaladas
- Revisa los logs: `sudo journalctl -u monitor-service`

## Mantenimiento

### Backup de la base de datos de logs
```bash
mysqldump -u root -p LOGSEGURIDAD > backup_logs_$(date +%Y%m%d).sql
```

### Limpiar logs antiguos (opcional)
```sql
DELETE FROM LOGSEGURIDAD.operaciones_log 
WHERE fecha_hora < DATE_SUB(NOW(), INTERVAL 90 DAY);
```

## Soporte

Para problemas o preguntas, revisa los logs del servicio y la configuración de `.env`.

