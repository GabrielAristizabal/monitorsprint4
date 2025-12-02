# 🔧 Guía de Configuración de IPs y Comunicación entre Microservicios

Esta guía te ayudará a configurar las IPs y conexiones entre los microservicios una vez que estén desplegados en las instancias EC2.

## 📋 Arquitectura de Microservicios

```
┌─────────────────┐
│  GestorPedidos  │  Puerto: 5000
│   (FastAPI)     │  MongoDB: provesi_wms
└────────┬────────┘
         │
         ├─── Monitoreado por ───┐
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │     Monitor     │  Puerto: 5001
         │              │     (Flask)     │  MySQL: LOGSEGURIDAD
         │              └─────────────────┘
         │
         ▼
┌─────────────────┐
│   ruta_optima   │  Puerto: 8000
│    (Django)     │  MongoDB: ruta_optima_db
└─────────────────┘
```

## 🗂️ Archivos de Configuración por Microservicio

### 1. **GestorPedidos** 

**Ubicación:** `GestorPedidos/provesi-orders-mongo/microservices/orders-mongo-service/.env`

**Crear archivo:**
```bash
cd GestorPedidos/provesi-orders-mongo/microservices/orders-mongo-service
cp .env.example .env
nano .env
```

**Variables a configurar:**
```env
# ⚠️ CAMBIAR: IP de la instancia donde está MongoDB
# Si MongoDB está en la misma instancia: mongodb://localhost:27017
# Si MongoDB está en otra instancia: mongodb://172.31.XX.XX:27017
MONGO_URI=mongodb://172.31.XX.XX:27017
MONGO_DB=provesi_wms

# Si MongoDB tiene autenticación:
# MONGO_URI=mongodb://usuario:password@172.31.XX.XX:27017/provesi_wms

# Puerto de la API (por defecto 5000)
PORT=5000
```

**Ejemplo con IP real:**
```env
MONGO_URI=mongodb://172.31.15.10:27017
MONGO_DB=provesi_wms
PORT=5000
```

---

### 2. **ruta_optima**

**Ubicación:** `ruta_optima/.env`

**Crear archivo:**
```bash
cd ruta_optima
cp .env.example .env
nano .env
```

**Variables a configurar:**
```env
# ⚠️ CAMBIAR: IP de la instancia donde está MongoDB
# Puede ser la misma que GestorPedidos o diferente
MONGO_URI=mongodb://172.31.XX.XX:27017
MONGO_DB=ruta_optima_db

# Si MongoDB tiene autenticación:
# MONGO_URI=mongodb://usuario:password@172.31.XX.XX:27017/ruta_optima_db

# Puerto de Django (por defecto 8000)
PORT=8000
```

**Ejemplo con IP real:**
```env
MONGO_URI=mongodb://172.31.15.10:27017
MONGO_DB=ruta_optima_db
PORT=8000
```

---

### 3. **Monitor (mnitor)**

**Ubicación:** `mnitor/.env`

**Crear archivo:**
```bash
cd mnitor
cp env.example .env
nano .env
```

**Variables a configurar:**
```env
# ⚠️ CAMBIAR: MongoDB del gestor (para monitorear)
GESTOR_MONGO_URI=mongodb://172.31.XX.XX:27017
GESTOR_MONGO_DB=provesi_wms

# ⚠️ CAMBIAR: MySQL para guardar logs (LOGSEGURIDAD)
LOG_DB_HOST=172.31.XX.XX
LOG_DB_PORT=3306
LOG_DB_USER=root
LOG_DB_PASSWORD=tu_password_aqui
LOG_DB_NAME=LOGSEGURIDAD

# ⚠️ CAMBIAR: URL de la API del gestor
GESTOR_API_URL=http://172.31.XX.XX:5000

# Configuración del monitor
MONITOR_PORT=5001
MONITOR_INTERVAL=30
```

**Ejemplo con IPs reales:**
```env
# MongoDB del gestor (misma instancia o diferente)
GESTOR_MONGO_URI=mongodb://172.31.15.10:27017
GESTOR_MONGO_DB=provesi_wms

# MySQL para logs (puede estar en la misma instancia del gestor)
LOG_DB_HOST=172.31.15.10
LOG_DB_PORT=3306
LOG_DB_USER=log_admin
LOG_DB_PASSWORD=miPasswordSeguro123
LOG_DB_NAME=LOGSEGURIDAD

# API del gestor (IP privada dentro de la VPC)
GESTOR_API_URL=http://172.31.15.10:5000

MONITOR_PORT=5001
MONITOR_INTERVAL=30
```

---

## 📍 Escenarios de Despliegue

### Escenario 1: Todo en la misma instancia

Si todos los microservicios están en la misma instancia EC2:

**GestorPedidos:**
```env
MONGO_URI=mongodb://localhost:27017
```

**ruta_optima:**
```env
MONGO_URI=mongodb://localhost:27017
```

**Monitor:**
```env
GESTOR_MONGO_URI=mongodb://localhost:27017
LOG_DB_HOST=localhost
GESTOR_API_URL=http://localhost:5000
```

---

### Escenario 2: Microservicios en instancias separadas

**Instancia 1 (IP: 172.31.15.10):**
- GestorPedidos
- MongoDB
- MySQL (LOGSEGURIDAD)

**Instancia 2 (IP: 172.31.15.11):**
- Monitor

**Instancia 3 (IP: 172.31.15.12):**
- ruta_optima

**Configuración:**

**GestorPedidos (Instancia 1):**
```env
MONGO_URI=mongodb://localhost:27017
```

**Monitor (Instancia 2):**
```env
GESTOR_MONGO_URI=mongodb://172.31.15.10:27017
LOG_DB_HOST=172.31.15.10
GESTOR_API_URL=http://172.31.15.10:5000
```

**ruta_optima (Instancia 3):**
```env
MONGO_URI=mongodb://172.31.15.10:27017
```

---

## 🔒 Configuración de Security Groups en AWS

Para que los microservicios se comuniquen, configura los Security Groups:

### Security Group de MongoDB

**Reglas de entrada:**
- Tipo: Custom TCP
- Puerto: 27017
- Origen: 
  - IP privada de GestorPedidos (172.31.15.10/32)
  - IP privada de ruta_optima (172.31.15.12/32)
  - IP privada de Monitor (172.31.15.11/32)
  - O mejor: Security Group de cada microservicio

### Security Group de MySQL (LOGSEGURIDAD)

**Reglas de entrada:**
- Tipo: MySQL/Aurora
- Puerto: 3306
- Origen: IP privada del Monitor (172.31.15.11/32) o su Security Group

### Security Group de GestorPedidos

**Reglas de entrada:**
- Tipo: Custom TCP
- Puerto: 5000
- Origen: IP privada del Monitor (172.31.15.11/32) o su Security Group

### Security Group de Monitor

**Reglas de entrada:**
- Tipo: Custom TCP
- Puerto: 5001
- Origen: Tu IP pública (para acceso administrativo)

**Reglas de salida:**
- Permitir todo (por defecto)

### Security Group de ruta_optima

**Reglas de entrada:**
- Tipo: Custom TCP
- Puerto: 8000
- Origen: IP privada del GestorPedidos o Security Group específico

---

## ✅ Verificación de Conectividad

### 1. Verificar MongoDB desde GestorPedidos

```bash
# En la instancia de GestorPedidos
mongo mongodb://172.31.XX.XX:27017/provesi_wms
# O si está local:
mongo
```

### 2. Verificar MySQL desde Monitor

```bash
# En la instancia del Monitor
mysql -h 172.31.XX.XX -u log_user -p -e "SHOW DATABASES;"
```

### 3. Verificar API del Gestor desde Monitor

```bash
# En la instancia del Monitor
curl http://172.31.XX.XX:5000/health
```

### 4. Verificar MongoDB desde ruta_optima

```bash
# En la instancia de ruta_optima
mongo mongodb://172.31.XX.XX:27017/ruta_optima_db
```

---

## 🔄 Flujo de Comunicación

1. **GestorPedidos** → MongoDB (guarda pedidos)
2. **Monitor** → MongoDB del gestor (lee pedidos para monitorear)
3. **Monitor** → MySQL LOGSEGURIDAD (guarda logs)
4. **Monitor** → API del Gestor (verifica salud)
5. **ruta_optima** → MongoDB (guarda rutas calculadas)

---

## 📝 Resumen de IPs a Configurar

| Microservicio | Variable | Descripción | Ejemplo |
|--------------|----------|-------------|---------|
| **GestorPedidos** | `MONGO_URI` | IP de MongoDB | `mongodb://172.31.15.10:27017` |
| **ruta_optima** | `MONGO_URI` | IP de MongoDB | `mongodb://172.31.15.10:27017` |
| **Monitor** | `GESTOR_MONGO_URI` | IP de MongoDB del gestor | `mongodb://172.31.15.10:27017` |
| **Monitor** | `LOG_DB_HOST` | IP de MySQL (LOGSEGURIDAD) | `172.31.15.10` |
| **Monitor** | `GESTOR_API_URL` | IP y puerto de la API del gestor | `http://172.31.15.10:5000` |

---

## 🚨 Troubleshooting

### Error: "Connection refused"
- Verifica que el servicio esté corriendo
- Verifica que el puerto esté abierto en el Security Group
- Verifica que la IP sea correcta (privada dentro de VPC)

### Error: "Authentication failed" (MongoDB)
- Verifica usuario y contraseña en `MONGO_URI`
- Formato: `mongodb://usuario:password@ip:puerto/database`

### Error: "Access denied" (MySQL)
- Verifica usuario y contraseña
- Verifica que el usuario tenga permisos desde la IP del monitor
- Ejecuta: `GRANT ALL ON LOGSEGURIDAD.* TO 'log_user'@'172.31.15.11' IDENTIFIED BY 'password';`

---

¿Necesitas ayuda con alguna configuración específica?

