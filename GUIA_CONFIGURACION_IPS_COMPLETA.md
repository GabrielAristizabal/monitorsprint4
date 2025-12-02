# 🔧 Guía Completa de Configuración de IPs

Esta guía te indica **exactamente dónde** poner cada IP para que todos los servicios se comuniquen correctamente.

## 📍 Resumen de Instancias y Bases de Datos

Asumiendo que tienes:
- **Instancia MongoDB**: IP `172.31.15.20` (MongoDB instalado)
- **AWS RDS MySQL**: Endpoint `monitor-db.abc123.us-east-1.rds.amazonaws.com`
- **Instancia GestorPedidos**: IP `172.31.15.10`
- **Instancia ruta_optima**: IP `172.31.15.11`
- **Instancia Monitor**: IP `172.31.15.12`
- **Instancia Orquestador**: IP `172.31.15.13`

---

## 📂 Archivos a Configurar

### 1️⃣ **GestorPedidos**

**Archivo:** `GestorPedidos/provesi-orders-mongo/microservices/orders-mongo-service/.env`

**Crear el archivo:**
```bash
cd GestorPedidos/provesi-orders-mongo/microservices/orders-mongo-service
cp .env.example .env
nano .env
```

**Contenido:**
```env
# IP de la instancia donde está MongoDB
MONGO_URI=mongodb://172.31.15.20:27017
MONGO_DB=provesi_wms
PORT=5000
```

**⚠️ IMPORTANTE:** Reemplaza `172.31.15.20` con la IP real de tu instancia MongoDB.

---

### 2️⃣ **ruta_optima**

**Archivo:** `ruta_optima/.env`

**Crear el archivo:**
```bash
cd ruta_optima
cp .env.example .env
nano .env
```

**Contenido:**
```env
# IP de la instancia donde está MongoDB (puede ser la misma que GestorPedidos)
MONGO_URI=mongodb://172.31.15.20:27017
MONGO_DB=ruta_optima_db
PORT=8000
```

**⚠️ IMPORTANTE:** Reemplaza `172.31.15.20` con la IP real de tu instancia MongoDB.

---

### 3️⃣ **Monitor (mnitor)**

**Archivo:** `mnitor/.env`

**Crear el archivo:**
```bash
cd mnitor
cp env.example .env
nano .env
```

**Contenido:**
```env
# MongoDB del gestor (instancia donde está MongoDB)
GESTOR_MONGO_URI=mongodb://172.31.15.20:27017
GESTOR_MONGO_DB=provesi_wms

# MySQL en AWS RDS (LOGSEGURIDAD)
LOG_DB_HOST=monitor-db.abc123.us-east-1.rds.amazonaws.com
LOG_DB_PORT=3306
LOG_DB_USER=admin
LOG_DB_PASSWORD=tu_password_rds_aqui
LOG_DB_NAME=LOGSEGURIDAD

# API del GestorPedidos (IP de la instancia del gestor)
GESTOR_API_URL=http://172.31.15.10:5000

MONITOR_PORT=5001
MONITOR_INTERVAL=30
SECRET_KEY=change-this-secret-key-in-production
```

**⚠️ IMPORTANTE:** 
- Reemplaza `172.31.15.20` con la IP de tu instancia MongoDB
- Reemplaza `monitor-db.abc123.us-east-1.rds.amazonaws.com` con el endpoint real de tu RDS
- Reemplaza `172.31.15.10` con la IP de tu instancia GestorPedidos
- Reemplaza `tu_password_rds_aqui` con la contraseña real de RDS

---

### 4️⃣ **Orquestador**

**Archivo:** `orquestador/.env`

**Crear el archivo:**
```bash
cd orquestador
cp .env.example .env
nano .env
```

**Contenido:**
```env
# Puerto del orquestador
ORCHESTRATOR_PORT=8080

# IPs de las instancias donde están los microservicios
GESTOR_PEDIDOS_URL=http://172.31.15.10:5000
RUTA_OPTIMA_URL=http://172.31.15.11:8000

REGISTRY_PORT=8081
SERVICE_TTL=30
REQUEST_TIMEOUT=0.5
```

**⚠️ IMPORTANTE:**
- Reemplaza `172.31.15.10` con la IP de tu instancia GestorPedidos
- Reemplaza `172.31.15.11` con la IP de tu instancia ruta_optima

---

## 🗺️ Mapa de Conexiones

```
┌─────────────────────┐
│  Instancia MongoDB  │  IP: 172.31.15.20
│   (Puerto 27017)    │
└──────────┬──────────┘
           │
           ├─── GestorPedidos (172.31.15.10) ────┐
           │                                       │
           └─── ruta_optima (172.31.15.11)        │
                                                   │
┌─────────────────────┐                           │
│   AWS RDS MySQL     │                           │
│  (LOGSEGURIDAD)     │                           │
│  Endpoint: ...rds   │                           │
└──────────┬──────────┘                           │
           │                                       │
           └─── Monitor (172.31.15.12)            │
                                                   │
┌─────────────────────┐                           │
│   Orquestador       │                           │
│   (172.31.15.13)    │                           │
└──────────┬──────────┘                           │
           │                                       │
           ├───────────────────────────────────────┘
           │
           └─── Consulta ambos servicios
```

---

## 📋 Checklist de Configuración

### Paso 1: Obtener las IPs

- [ ] IP de la instancia MongoDB: `_____________`
- [ ] Endpoint de AWS RDS MySQL: `_____________`
- [ ] IP de la instancia GestorPedidos: `_____________`
- [ ] IP de la instancia ruta_optima: `_____________`
- [ ] IP de la instancia Monitor: `_____________`
- [ ] IP de la instancia Orquestador: `_____________`

### Paso 2: Crear archivos .env

- [ ] Crear `.env` en GestorPedidos
- [ ] Crear `.env` en ruta_optima
- [ ] Crear `.env` en mnitor
- [ ] Crear `.env` en orquestador

### Paso 3: Configurar IPs

- [ ] Configurar `MONGO_URI` en GestorPedidos
- [ ] Configurar `MONGO_URI` en ruta_optima
- [ ] Configurar `GESTOR_MONGO_URI` en Monitor
- [ ] Configurar `LOG_DB_HOST` en Monitor (endpoint RDS)
- [ ] Configurar `GESTOR_API_URL` en Monitor
- [ ] Configurar `GESTOR_PEDIDOS_URL` en Orquestador
- [ ] Configurar `RUTA_OPTIMA_URL` en Orquestador

### Paso 4: Verificar Security Groups

- [ ] MongoDB: Permitir puerto 27017 desde GestorPedidos, ruta_optima y Monitor
- [ ] RDS: Permitir puerto 3306 desde Monitor
- [ ] GestorPedidos: Permitir puerto 5000 desde Monitor y Orquestador
- [ ] ruta_optima: Permitir puerto 8000 desde Orquestador
- [ ] Orquestador: Permitir puerto 8080 desde donde necesites acceder

---

## 🔍 Cómo Obtener las IPs

### IP de Instancia EC2

1. Ve a AWS Console → EC2 → Instancias
2. Selecciona la instancia
3. Copia la **IP Privada IPv4** (formato: 172.31.x.x)

### Endpoint de RDS

1. Ve a AWS Console → RDS → Databases
2. Selecciona tu base de datos
3. Copia el **Endpoint** (formato: nombre.xxxxx.region.rds.amazonaws.com)

---

## ✅ Verificación de Conexiones

### Verificar MongoDB desde GestorPedidos

```bash
# En la instancia de GestorPedidos
mongo mongodb://172.31.15.20:27017/provesi_wms
```

### Verificar RDS desde Monitor

```bash
# En la instancia del Monitor
mysql -h monitor-db.abc123.us-east-1.rds.amazonaws.com -u admin -p LOGSEGURIDAD
```

### Verificar API del Gestor desde Monitor

```bash
# En la instancia del Monitor
curl http://172.31.15.10:5000/health
```

### Verificar Orquestador

```bash
# Desde cualquier lugar
curl http://172.31.15.13:8080/health
```

---

## 🔒 Configuración de Security Groups

### Security Group de MongoDB (Instancia EC2)

**Reglas de Entrada:**
- Tipo: Custom TCP
- Puerto: 27017
- Origen: 
  - Security Group de GestorPedidos, O
  - IP privada de GestorPedidos (172.31.15.10/32)
  - IP privada de ruta_optima (172.31.15.11/32)
  - IP privada de Monitor (172.31.15.12/32)

### Security Group de RDS

**Reglas de Entrada:**
- Tipo: MySQL/Aurora
- Puerto: 3306
- Origen:
  - Security Group de Monitor, O
  - IP privada de Monitor (172.31.15.12/32)

### Security Group de GestorPedidos

**Reglas de Entrada:**
- Tipo: Custom TCP
- Puerto: 5000
- Origen:
  - Security Group de Monitor y Orquestador, O
  - IP privada de Monitor (172.31.15.12/32)
  - IP privada de Orquestador (172.31.15.13/32)

### Security Group de ruta_optima

**Reglas de Entrada:**
- Tipo: Custom TCP
- Puerto: 8000
- Origen:
  - Security Group de Orquestador, O
  - IP privada de Orquestador (172.31.15.13/32)

### Security Group de Orquestador

**Reglas de Entrada:**
- Tipo: Custom TCP
- Puerto: 8080
- Origen: Tu IP pública (para acceso administrativo)

---

## 📝 Resumen de Variables por Servicio

| Servicio | Archivo .env | Variables Clave |
|----------|-------------|-----------------|
| **GestorPedidos** | `GestorPedidos/.../orders-mongo-service/.env` | `MONGO_URI` |
| **ruta_optima** | `ruta_optima/.env` | `MONGO_URI` |
| **Monitor** | `mnitor/.env` | `GESTOR_MONGO_URI`, `LOG_DB_HOST`, `GESTOR_API_URL` |
| **Orquestador** | `orquestador/.env` | `GESTOR_PEDIDOS_URL`, `RUTA_OPTIMA_URL` |

---

## 🚨 Troubleshooting

### Error: "Connection refused" a MongoDB
- Verifica que MongoDB esté corriendo en la instancia
- Verifica que el Security Group permita el puerto 27017
- Verifica que la IP en `MONGO_URI` sea correcta

### Error: "Access denied" a RDS
- Verifica usuario y contraseña en `LOG_DB_USER` y `LOG_DB_PASSWORD`
- Verifica que el Security Group de RDS permita conexiones desde Monitor
- Verifica que el endpoint de RDS sea correcto

### Error: "Timeout" en llamadas entre servicios
- Verifica que los Security Groups permitan el tráfico
- Verifica que las IPs en los `.env` sean correctas
- Verifica que los servicios estén corriendo

---

¿Necesitas ayuda con alguna configuración específica?

