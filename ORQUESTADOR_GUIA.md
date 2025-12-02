# 🎯 Guía del Orquestador

## 📋 Resumen

El orquestador coordina la comunicación entre los microservicios usando **service discovery** y genera reportes combinando datos de múltiples servicios.

## 🏗️ Arquitectura

```
┌─────────────────┐
│  Orquestador    │  Puerto: 8080
│   (FastAPI)     │
└────────┬────────┘
         │
         ├── Service Registry
         │   └── Descubrimiento de servicios
         │
         ├── GestorPedidos ────┐
         │                     │
         └── ruta_optima ──────┤
                               │
                               ▼
                    ┌──────────────────┐
                    │  Reporte de Rutas │
                    │  Optimizadas      │
                    └──────────────────┘
```

## 🚀 Instalación

```bash
cd orquestador
pip install -r requirements.txt
```

## ⚙️ Configuración

1. Crear archivo `.env`:
```bash
cp .env.example .env
nano .env
```

2. Configurar IPs de los microservicios:
```env
GESTOR_PEDIDOS_URL=http://172.31.XX.XX:5000
RUTA_OPTIMA_URL=http://172.31.XX.XX:8000
```

## ▶️ Ejecución

```bash
python -m orquestador.main
```

O con uvicorn:
```bash
uvicorn orquestador.main:app --host 0.0.0.0 --port 8080
```

## 📡 Registro de Servicios

Los microservicios deben registrarse al iniciar. Hay dos formas:

### Opción 1: Usando el script

```bash
python orquestador/register_service.py gestor-pedidos 172.31.15.10 5000 http://172.31.XX.XX:8080
```

### Opción 2: Desde el código del microservicio

```python
import requests
import threading
import time

def register_and_heartbeat():
    # Registrar servicio
    requests.post("http://orquestador:8080/registry/register", params={
        "service_name": "gestor-pedidos",
        "host": "172.31.15.10",
        "port": 5000
    })
    
    # Enviar heartbeat cada 10 segundos
    while True:
        requests.post("http://orquestador:8080/registry/heartbeat/gestor-pedidos")
        time.sleep(10)

# Iniciar en thread separado
threading.Thread(target=register_and_heartbeat, daemon=True).start()
```

## 🔌 Endpoints del Orquestador

### Service Registry

#### Registrar Servicio
```bash
POST /registry/register?service_name=gestor-pedidos&host=172.31.15.10&port=5000
```

#### Enviar Heartbeat
```bash
POST /registry/heartbeat/gestor-pedidos
```

#### Listar Servicios
```bash
GET /registry/services
```

#### Obtener Servicio
```bash
GET /registry/service/gestor-pedidos
```

### Reportes

#### Generar Reporte de Rutas Optimizadas
```bash
GET /reports/rutas-optimizadas?month=2025-11
```

**Respuesta:**
```json
{
  "status": "success",
  "month": "2025-11",
  "orders_count": 10,
  "stands_con_problema": [
    {
      "stand_id": "Pasillo 1 - Stand 3",
      "tiempo_estimado_promedio": 8.5,
      "tiempo_real_promedio": 12.3,
      "desviacion_promedio": 3.8,
      "desviacion_porcentual": 44.7,
      "pedidos_analizados": 5
    }
  ],
  "processing_time_ms": 245.67
}
```

**Características:**
- ✅ Respuesta en menos de 1 segundo
- ✅ Combina datos de GestorPedidos y ruta_optima
- ✅ Identifica stands con desviación > 15%
- ✅ Genera tiempos reales aleatorios y los guarda en el gestor

### Health Check

```bash
GET /health
```

## 🔄 Flujo del Reporte

1. **Orquestador** recibe petición de reporte
2. **Orquestador** consulta **GestorPedidos** para obtener últimos 10 pedidos del mes anterior
3. **Orquestador** consulta **ruta_optima** para obtener rutas calculadas de cada pedido
4. **Orquestador** genera tiempos reales aleatorios (80%-150% del estimado)
5. **Orquestador** guarda tiempos reales en **GestorPedidos**
6. **Orquestador** compara tiempos estimados vs reales por stand
7. **Orquestador** identifica stands con desviación > 15%
8. **Orquestador** retorna reporte en < 1 segundo

## 📝 Endpoints Nuevos en Microservicios

### GestorPedidos

#### Obtener últimos 10 pedidos del mes anterior
```bash
GET /orders/last-10-previous-month?month=2025-11
```

#### Actualizar pedido con tiempos reales
```bash
PUT /orders/{order_id}/real-times
Body: [{"sku": "...", "tiempo_real_pick": 12.5, ...}]
```

### ruta_optima

#### Obtener ruta por pedido_id
```bash
GET /ruta/{pedido_id}/
```

## 🔒 Security Groups

Asegúrate de que el Security Group del orquestador permita:
- **Entrada**: Puerto 8080 desde donde necesites acceder
- **Salida**: Puertos 5000 (GestorPedidos) y 8000 (ruta_optima)

## ✅ Verificación

### 1. Verificar que el orquestador está corriendo
```bash
curl http://localhost:8080/health
```

### 2. Registrar un servicio
```bash
curl -X POST "http://localhost:8080/registry/register?service_name=gestor-pedidos&host=172.31.15.10&port=5000"
```

### 3. Listar servicios registrados
```bash
curl http://localhost:8080/registry/services
```

### 4. Generar reporte
```bash
curl "http://localhost:8080/reports/rutas-optimizadas?month=2025-11"
```

## 🐛 Troubleshooting

### Error: "Servicio no disponible"
- Verifica que el servicio esté registrado: `GET /registry/services`
- Verifica que el servicio esté enviando heartbeats
- Verifica la URL de fallback en `.env`

### Error: "Timeout"
- Aumenta `REQUEST_TIMEOUT` en `.env` (pero debe ser < 1 segundo total)
- Verifica conectividad entre orquestador y microservicios

### Error: "No se encontraron pedidos"
- Verifica que haya pedidos en el mes anterior en GestorPedidos
- Verifica que los pedidos tengan rutas calculadas en ruta_optima

---

Para más detalles, ver `orquestador/README.md`

