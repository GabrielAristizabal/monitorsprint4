# Orquestador de Microservicios

Orquestador que coordina la comunicación entre los microservicios usando service discovery.

## Características

- **Service Discovery/Registry**: Los servicios se registran automáticamente
- **Reporte de Rutas Optimizadas**: Genera reportes combinando datos de GestorPedidos y ruta_optima
- **Análisis de Stands**: Identifica stands donde no se estima correctamente el tiempo de preparación
- **Respuesta rápida**: Genera reportes en menos de 1 segundo

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

1. Copiar archivo de configuración:
```bash
cp .env.example .env
```

2. Editar `.env` con las IPs de los microservicios:
```env
GESTOR_PEDIDOS_URL=http://172.31.XX.XX:5000
RUTA_OPTIMA_URL=http://172.31.XX.XX:8000
```

## Ejecución

```bash
python -m orquestador.main
```

O con uvicorn:
```bash
uvicorn orquestador.main:app --host 0.0.0.0 --port 8080
```

## Endpoints

### Service Registry

- `POST /registry/register` - Registrar un servicio
- `POST /registry/heartbeat/{service_name}` - Enviar heartbeat
- `GET /registry/services` - Listar servicios registrados
- `GET /registry/service/{service_name}` - Obtener información de un servicio

### Reportes

- `GET /reports/rutas-optimizadas?month=YYYY-MM` - Genera reporte de rutas optimizadas

### Health

- `GET /health` - Health check del orquestador

## Registro de Servicios

Los microservicios deben registrarse al iniciar:

```python
import requests

requests.post("http://orquestador:8080/registry/register", json={
    "service_name": "gestor-pedidos",
    "host": "172.31.15.10",
    "port": 5000
})
```

Y enviar heartbeat periódicamente:

```python
requests.post(f"http://orquestador:8080/registry/heartbeat/gestor-pedidos")
```

## Ejemplo de Uso

### Generar Reporte

```bash
curl "http://localhost:8080/reports/rutas-optimizadas?month=2025-11"
```

Respuesta:
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

