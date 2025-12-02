# ⚡ Configuración Rápida de IPs

## 📍 Dónde Poner Cada IP

### 1. GestorPedidos → MongoDB
**Archivo:** `GestorPedidos/provesi-orders-mongo/microservices/orders-mongo-service/.env`
```env
MONGO_URI=mongodb://[IP_MONGODB]:27017
```

### 2. ruta_optima → MongoDB
**Archivo:** `ruta_optima/.env`
```env
MONGO_URI=mongodb://[IP_MONGODB]:27017
```

### 3. Monitor → MongoDB (del gestor)
**Archivo:** `mnitor/.env`
```env
GESTOR_MONGO_URI=mongodb://[IP_MONGODB]:27017
```

### 4. Monitor → AWS RDS MySQL
**Archivo:** `mnitor/.env`
```env
LOG_DB_HOST=[ENDPOINT_RDS]
LOG_DB_USER=[USUARIO_RDS]
LOG_DB_PASSWORD=[PASSWORD_RDS]
```

### 5. Monitor → API GestorPedidos
**Archivo:** `mnitor/.env`
```env
GESTOR_API_URL=http://[IP_GESTOR]:5000
```

### 6. Orquestador → GestorPedidos
**Archivo:** `orquestador/.env`
```env
GESTOR_PEDIDOS_URL=http://[IP_GESTOR]:5000
```

### 7. Orquestador → ruta_optima
**Archivo:** `orquestador/.env`
```env
RUTA_OPTIMA_URL=http://[IP_RUTA_OPTIMA]:8000
```

---

## 🎯 Ejemplo Completo

Supongamos:
- MongoDB en: `172.31.15.20`
- RDS en: `monitor-db.abc123.us-east-1.rds.amazonaws.com`
- GestorPedidos en: `172.31.15.10`
- ruta_optima en: `172.31.15.11`

### GestorPedidos/.env
```env
MONGO_URI=mongodb://172.31.15.20:27017
MONGO_DB=provesi_wms
```

### ruta_optima/.env
```env
MONGO_URI=mongodb://172.31.15.20:27017
MONGO_DB=ruta_optima_db
```

### mnitor/.env
```env
GESTOR_MONGO_URI=mongodb://172.31.15.20:27017
GESTOR_MONGO_DB=provesi_wms
LOG_DB_HOST=monitor-db.abc123.us-east-1.rds.amazonaws.com
LOG_DB_PORT=3306
LOG_DB_USER=admin
LOG_DB_PASSWORD=tu_password
LOG_DB_NAME=LOGSEGURIDAD
GESTOR_API_URL=http://172.31.15.10:5000
```

### orquestador/.env
```env
GESTOR_PEDIDOS_URL=http://172.31.15.10:5000
RUTA_OPTIMA_URL=http://172.31.15.11:8000
```

---

Para más detalles, ver `GUIA_CONFIGURACION_IPS_COMPLETA.md`

