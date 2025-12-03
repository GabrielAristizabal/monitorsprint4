# apigateway/main.py

import os
from typing import Optional, Dict, Any

import httpx
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse

# URL del orquestador (ajústala a tu despliegue real)
ORQUESTADOR_URL = os.getenv("ORQUESTADOR_URL", "http://localhost:9000")

# Nombres de servicios tal y como se registran en el orquestador
GESTOR_PEDIDOS_SERVICE_NAME = os.getenv("GESTOR_PEDIDOS_SERVICE_NAME", "gestor_pedidos")
MONITOR_SERVICE_NAME = os.getenv("MONITOR_SERVICE_NAME", "monitor_seguridad")

app = FastAPI(
    title="API Gateway Provesi",
    description="Punto único de entrada para frontend, usando al orquestador para discovery y reportes.",
    version="1.0.0",
)


async def get_service_base_url(service_name: str) -> str:
    """
    Pide al orquestador los datos del servicio (host/port)
    y construye la base URL.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{ORQUESTADOR_URL}/registry/service/{service_name}")
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error contactando al orquestador: {str(e)}"
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Servicio '{service_name}' no disponible en el orquestador"
        )

    data = resp.json()
    # Ajusta estos campos a lo que devuelva tu orquestador (host/port)
    host = data.get("host")
    port = data.get("port")

    if not host or not port:
        raise HTTPException(
            status_code=500,
            detail=f"Respuesta inválida del orquestador para el servicio '{service_name}'"
        )

    return f"http://{host}:{port}"


@app.get("/health")
async def gateway_health() -> Dict[str, Any]:
    """
    Estado del gateway + estado del orquestador.
    """
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{ORQUESTADOR_URL}/health")
        orch_status = resp.json()
    except Exception as e:
        orch_status = {"status": "down", "error": str(e)}

    return {
        "gateway_status": "ok",
        "orquestador": orch_status,
    }


# ----------------------------
# 1. Endpoints para pedidos
# ----------------------------

@app.post("/orders")
async def create_order(request: Request):
    """
    Crea un pedido a través del Gestor de Pedidos,
    pero el frontend solo llama al gateway.
    """
    body = await request.json()

    base_url = await get_service_base_url(GESTOR_PEDIDOS_SERVICE_NAME)
    target_url = f"{base_url}/orders"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(target_url, json=body)
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error llamando a Gestor de Pedidos: {str(e)}")

    return JSONResponse(status_code=resp.status_code, content=resp.json())


# ----------------------------
# 2. Reporte de rutas optimizadas
#    (se delega al orquestador)
# ----------------------------

@app.get("/reports/rutas-optimizadas")
async def get_rutas_optimizadas(
    month: str = Query(..., description="Mes en formato YYYY-MM, por ejemplo 2025-01")
):
    """
    El frontend llama al gateway -> el gateway llama al orquestador
    para generar el reporte de rutas optimizadas.
    """
    params = {"month": month}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{ORQUESTADOR_URL}/reports/rutas-optimizadas", params=params)
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error llamando al orquestador: {str(e)}")

    # Pasamos tal cual la respuesta del orquestador
    return JSONResponse(status_code=resp.status_code, content=resp.json())


# ----------------------------
# 3. Endpoints de monitor
# ----------------------------

@app.get("/monitor/logs")
async def get_monitor_logs(
    limit: int = Query(50, ge=1, le=500),
    suspicious_only: bool = Query(False)
):
    """
    El frontend consulta logs de seguridad solo al gateway.
    El gateway reenvía la petición al monitor de seguridad.
    """
    base_url = await get_service_base_url(MONITOR_SERVICE_NAME)
    target_url = f"{base_url}/logs"
    params = {"limit": limit, "suspicious_only": suspicious_only}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(target_url, params=params)
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error llamando al Monitor: {str(e)}")

    return JSONResponse(status_code=resp.status_code, content=resp.json())


@app.get("/monitor/stats")
async def get_monitor_stats():
    """
    Stats agregadas de seguridad a través del gateway.
    """
    base_url = await get_service_base_url(MONITOR_SERVICE_NAME)
    target_url = f"{base_url}/stats"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(target_url)
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error llamando al Monitor: {str(e)}")

    return JSONResponse(status_code=resp.status_code, content=resp.json())
