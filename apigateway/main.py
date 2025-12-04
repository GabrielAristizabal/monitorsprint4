import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

import httpx
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ===============================
# Cargar variables de entorno
# ===============================
load_dotenv()

ORQUESTADOR_URL = os.getenv("ORQUESTADOR_URL", "http://localhost:8080")
GESTOR_PEDIDOS_SERVICE_NAME = os.getenv("GESTOR_PEDIDOS_SERVICE_NAME", "gestor-pedidos")
MONITOR_SERVICE_NAME = os.getenv("MONITOR_SERVICE_NAME", "monitor")

GESTOR_PEDIDOS_FALLBACK_URL = os.getenv("GESTOR_PEDIDOS_FALLBACK_URL", "http://localhost:8001")
MONITOR_FALLBACK_URL = os.getenv("MONITOR_FALLBACK_URL", "http://localhost:5001")

# ===============================
# FastAPI app
# ===============================
app = FastAPI(
    title="API Gateway Provesi",
    description="Punto único de entrada para frontend, usando al orquestador para discovery y reportes.",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===============================
# Service Discovery Helper
# ===============================
async def get_service_base_url(service_name: str, fallback_url: Optional[str] = None) -> str:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{ORQUESTADOR_URL}/registry/service/{service_name}")

        if resp.status_code == 200:
            data = resp.json()
            service_data = data.get("service", {})

            host = service_data.get("host")
            port = service_data.get("port")

            if host and port:
                return f"http://{host}:{int(port)}"

            if service_data.get("url"):
                return service_data["url"]

    except Exception as e:
        print(f"⚠️ Descubrimiento falló: {e}")

    print(f"➡️ Usando fallback: {fallback_url}")
    return fallback_url


# ===============================
# Health Check
# ===============================
@app.get("/health")
async def gateway_health():
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            orch_resp = await client.get(f"{ORQUESTADOR_URL}/health")
            orch_status = orch_resp.json()
    except:
        orch_status = {"status": "down"}

    return {"gateway_status": "ok", "orquestador": orch_status}


# ===============================
# 1. Orders - Create Order
# ===============================
@app.post("/orders")
async def create_order(request: Request):
    body = await request.json()

    base_url = await get_service_base_url(GESTOR_PEDIDOS_SERVICE_NAME, GESTOR_PEDIDOS_FALLBACK_URL)
    url = f"{base_url}/orders"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, json=body)

    return JSONResponse(status_code=resp.status_code, content=resp.json())


# ===============================
# 2. Reports - Rutas optimizadas
# ===============================
@app.get("/reports/rutas-optimizadas")
async def get_rutas_optimizadas(month: str = Query(...)):
    url = f"{ORQUESTADOR_URL}/reports/rutas-optimizadas"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params={"month": month})

    return resp.json()


# ===============================
# 3. Reports - Pedidos con rutas (TU ENDPOINT)
# ===============================
@app.get("/reports/pedidos-con-rutas")
async def get_pedidos_con_rutas(month: str = Query(...)):
    url = f"{ORQUESTADOR_URL}/reports/pedidos-con-rutas"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params={"month": month})

    return resp.json()


# ===============================
# 4. Monitor - Seguridad
# ===============================
@app.get("/monitor/logs")
async def get_monitor_logs(limit: int = 50, suspicious_only: bool = False):
    base_url = await get_service_base_url(MONITOR_SERVICE_NAME, MONITOR_FALLBACK_URL)
    url = f"{base_url}/logs"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params={"limit": limit, "suspicious_only": suspicious_only})

    return resp.json()


@app.get("/monitor/stats")
async def get_monitor_stats():
    base_url = await get_service_base_url(MONITOR_SERVICE_NAME, MONITOR_FALLBACK_URL)
    url = f"{base_url}/stats"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)

    return resp.json()
