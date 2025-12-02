# ⚡ Guía Rápida de Configuración de IPs

## 📝 Archivos a Crear/Modificar en Cada Instancia

### 1️⃣ **GestorPedidos** 

**Ubicación del archivo:** 
```
GestorPedidos/provesi-orders-mongo/microservices/orders-mongo-service/.env
```

**Crear el archivo:**
```bash
cd GestorPedidos/provesi-orders-mongo/microservices/orders-mongo-service
nano .env
```

**Crear el archivo:**
```bash
cd GestorPedidos/provesi-orders-mongo/microservices/orders-mongo-service
cp .env.example .env
nano .env
```

**Contenido del archivo `.env`:**
```env
# ⚠️ CAMBIAR: IP de la instancia donde está MongoDB
MONGO_URI=mongodb://172.31.XX.XX:27017
MONGO_DB=provesi_wms
```

**Ejemplo:**
```env
MONGO_URI=mongodb://172.31.15.20:27017
MONGO_DB=provesi_wms
```

---

### 2️⃣ **ruta_optima**

**Ubicación del archivo:**
```
ruta_optima/.env
```

**Crear el archivo:**
```bash
cd ruta_optima
cp .env.example .env
nano .env
```

**Contenido del archivo `.env`:**
```env
# ⚠️ CAMBIAR: IP de la instancia donde está MongoDB
MONGO_URI=mongodb://172.31.XX.XX:27017
MONGO_DB=ruta_optima_db
```

**Ejemplo:**
```env
MONGO_URI=mongodb://172.31.15.20:27017
MONGO_DB=ruta_optima_db
```

---

### 4️⃣ **Orquestador**

**Ubicación del archivo:**
```
orquestador/.env
```

**Crear el archivo:**
```bash
cd orquestador
cp env.example .env
nano .env
```

**Contenido del archivo `.env`:**
```env
# ⚠️ CAMBIAR: IPs de las instancias donde están los microservicios
GESTOR_PEDIDOS_URL=http://172.31.XX.XX:5000
RUTA_OPTIMA_URL=http://172.31.XX.XX:8000
```

**Ejemplo:**
```env
GESTOR_PEDIDOS_URL=http://172.31.15.10:5000
RUTA_OPTIMA_URL=http://172.31.15.11:8000
```

---

### 3️⃣ **Monitor (mnitor)**

**Ubicación del archivo:**
```
mnitor/.env
```

**Crear el archivo:**
```bash
cd mnitor
cp env.example .env
nano .env
```

**Contenido del archivo `.env` (modificar estas líneas):**
```env
# ⚠️ CAMBIAR: MongoDB del gestor (IP de la instancia donde está MongoDB)
GESTOR_MONGO_URI=mongodb://172.31.XX.XX:27017
GESTOR_MONGO_DB=provesi_wms

# ⚠️ CAMBIAR: AWS RDS MySQL (Endpoint completo de RDS)
LOG_DB_HOST=nombre-instancia.xxxxx.us-east-1.rds.amazonaws.com
LOG_DB_PORT=3306
LOG_DB_USER=admin
LOG_DB_PASSWORD=tu_password_rds_aqui
LOG_DB_NAME=LOGSEGURIDAD

# ⚠️ CAMBIAR: URL de la API del gestor (IP de la instancia GestorPedidos)
GESTOR_API_URL=http://172.31.XX.XX:5000
```

**Ejemplo completo:**
```env
GESTOR_MONGO_URI=mongodb://172.31.15.20:27017
GESTOR_MONGO_DB=provesi_wms

LOG_DB_HOST=monitor-db.abc123.us-east-1.rds.amazonaws.com
LOG_DB_PORT=3306
LOG_DB_USER=admin
LOG_DB_PASSWORD=miPasswordRDS123
LOG_DB_NAME=LOGSEGURIDAD

GESTOR_API_URL=http://172.31.15.10:5000

MONITOR_PORT=5001
MONITOR_INTERVAL=30
```

---

## 🎯 Resumen: Qué IPs Cambiar

| Microservicio | Archivo | Variable | Cambiar por |
|--------------|---------|----------|-------------|
| **GestorPedidos** | `.env` | `MONGO_URI` | IP de MongoDB |
| **ruta_optima** | `.env` | `MONGO_URI` | IP de MongoDB |
| **Monitor** | `.env` | `GESTOR_MONGO_URI` | IP de instancia MongoDB |
| **Monitor** | `.env` | `LOG_DB_HOST` | Endpoint de AWS RDS MySQL |
| **Monitor** | `.env` | `GESTOR_API_URL` | IP:5000 del gestor |
| **Orquestador** | `.env` | `GESTOR_PEDIDOS_URL` | IP:5000 del gestor |
| **Orquestador** | `.env` | `RUTA_OPTIMA_URL` | IP:8000 de ruta_optima |

---

## 📍 Casos Comunes

### Si todo está en la misma instancia:
- Usa `localhost` o `127.0.0.1` en todas las configuraciones

### Si están en instancias separadas:
- Usa las **IPs privadas** (172.31.x.x) dentro de la misma VPC
- Usa las **IPs públicas** solo si están en VPCs diferentes

---

## ✅ Verificar que Funciona

### Probar GestorPedidos:
```bash
curl http://localhost:5000/health
```

### Probar Monitor:
```bash
curl http://localhost:5001/health
```

### Probar ruta_optima:
```bash
curl http://localhost:8000/
```

---

Para más detalles, ver `CONFIGURACION_IPS.md`

