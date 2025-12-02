# Guía de Configuración de IPs y Variables de Entorno

## ⚠️ IMPORTANTE: Variables que DEBES Cambiar

Antes de desplegar el microservicio de monitoreo, debes configurar las siguientes variables con las IPs reales de tus instancias EC2.

### 1. Archivo `.env`

Copia el archivo `env.example` a `.env` y edita las siguientes variables:

```bash
cp env.example .env
nano .env
```

### 2. Variables a Configurar

#### Base de Datos del Gestor de Pedidos

```env
GESTOR_DB_HOST=172.31.XX.XX  # ⚠️ CAMBIAR: IP privada de la instancia EC2 del gestor
GESTOR_DB_PORT=3306
GESTOR_DB_USER=gestor_user    # ⚠️ CAMBIAR: Usuario de BD del gestor
GESTOR_DB_PASSWORD=password   # ⚠️ CAMBIAR: Password de BD del gestor
GESTOR_DB_NAME=pedidos        # ⚠️ CAMBIAR si tu BD tiene otro nombre
```

**Cómo obtener la IP:**
- En AWS Console → EC2 → Instancias → Selecciona la instancia del gestor
- Copia la **IP Privada IPv4** (formato: 172.31.x.x o 10.x.x.x)

#### Base de Datos de Logs (LOGSEGURIDAD)

```env
LOG_DB_HOST=172.31.XX.XX      # ⚠️ CAMBIAR: IP de la instancia donde está LOGSEGURIDAD
LOG_DB_PORT=3306
LOG_DB_USER=log_user          # ⚠️ CAMBIAR: Usuario para acceder a LOGSEGURIDAD
LOG_DB_PASSWORD=password      # ⚠️ CAMBIAR: Password para LOGSEGURIDAD
LOG_DB_NAME=LOGSEGURIDAD
```

**Nota:** Si LOGSEGURIDAD está en la misma instancia que el gestor, usa la misma IP privada.

#### API del Gestor de Pedidos

```env
GESTOR_API_URL=http://172.31.XX.XX:5000  # ⚠️ CAMBIAR: IP y puerto de la API del gestor
```

**Opciones:**
- Si el monitor está en la misma VPC: Usa la **IP privada** (172.31.x.x)
- Si el monitor está en otra VPC: Usa la **IP pública** o configura VPC Peering
- Si hay un Load Balancer: Usa la URL del Load Balancer

#### Configuración del Monitor

```env
MONITOR_PORT=5001             # Puerto donde escuchará el monitor (puedes cambiarlo)
MONITOR_INTERVAL=30           # Intervalo de monitoreo en segundos (30 = cada 30 seg)
```

## Ejemplo de Configuración Completa

Supongamos que tienes:

- **Instancia Gestor EC2**: IP privada `172.31.15.10`, IP pública `54.123.45.67`
- **Instancia Monitor EC2**: IP privada `172.31.15.11`
- **Base de datos LOGSEGURIDAD**: En la misma instancia del gestor (`172.31.15.10`)

Tu archivo `.env` debería verse así:

```env
# Base de datos del gestor
GESTOR_DB_HOST=172.31.15.10
GESTOR_DB_PORT=3306
GESTOR_DB_USER=gestor_user
GESTOR_DB_PASSWORD=mi_password_seguro
GESTOR_DB_NAME=pedidos

# Base de datos de logs (misma instancia que el gestor)
LOG_DB_HOST=172.31.15.10
LOG_DB_PORT=3306
LOG_DB_USER=log_user
LOG_DB_PASSWORD=mi_password_logs
LOG_DB_NAME=LOGSEGURIDAD

# API del gestor (usando IP privada dentro de la VPC)
GESTOR_API_URL=http://172.31.15.10:5000

# Configuración del monitor
MONITOR_PORT=5001
MONITOR_INTERVAL=30
```

## Configuración de Security Groups en AWS

Para que el monitor pueda conectarse, configura los Security Groups:

### Security Group del Gestor de Pedidos

**Regla de entrada para MySQL:**
- Tipo: MySQL/Aurora
- Puerto: 3306
- Origen: IP privada del monitor (`172.31.15.11/32`) o Security Group del monitor

**Regla de entrada para API:**
- Tipo: Custom TCP
- Puerto: 5000
- Origen: IP privada del monitor o Security Group del monitor

### Security Group del Monitor

**Regla de entrada para API del Monitor:**
- Tipo: Custom TCP
- Puerto: 5001
- Origen: Tu IP pública (para acceso administrativo) o Security Group específico

**Regla de salida:**
- Permitir todo el tráfico saliente (por defecto)

## Verificación de Conectividad

Antes de iniciar el servicio, verifica la conectividad:

### 1. Desde la instancia del monitor, prueba conexión a BD del gestor:

```bash
mysql -h 172.31.15.10 -u gestor_user -p -e "SHOW DATABASES;"
```

### 2. Prueba conexión a la API del gestor:

```bash
curl http://172.31.15.10:5000/health
```

### 3. Prueba conexión a LOGSEGURIDAD:

```bash
mysql -h 172.31.15.10 -u log_user -p -e "USE LOGSEGURIDAD; SHOW TABLES;"
```

## Troubleshooting de Conectividad

### Error: "Can't connect to MySQL server"

1. Verifica que la IP en `.env` sea correcta
2. Verifica Security Groups en AWS
3. Verifica que MySQL esté escuchando en todas las interfaces:
   ```sql
   -- En el servidor MySQL
   SHOW VARIABLES LIKE 'bind_address';
   -- Debe ser 0.0.0.0 o la IP específica
   ```
4. Verifica que el usuario tenga permisos para conectarse desde la IP del monitor:
   ```sql
   -- En el servidor MySQL
   CREATE USER 'gestor_user'@'172.31.15.11' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON pedidos.* TO 'gestor_user'@'172.31.15.11';
   FLUSH PRIVILEGES;
   ```

### Error: "Connection refused" en la API

1. Verifica que la API del gestor esté ejecutándose
2. Verifica que el puerto sea correcto (5000)
3. Verifica Security Groups
4. Verifica que la API esté escuchando en `0.0.0.0` y no solo en `localhost`

## Checklist Pre-Despliegue

- [ ] Archivo `.env` creado y configurado con IPs reales
- [ ] Credenciales de base de datos verificadas
- [ ] Security Groups configurados correctamente
- [ ] Conectividad a BD del gestor verificada
- [ ] Conectividad a BD de logs verificada
- [ ] Conectividad a API del gestor verificada
- [ ] Base de datos LOGSEGURIDAD creada (ejecutar `schema.sql`)
- [ ] Usuarios de MySQL creados con permisos adecuados

