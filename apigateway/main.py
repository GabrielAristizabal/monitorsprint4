# apigateway/main.py

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

import httpx
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Cargar variables de entorno
load_dotenv()

# URL del orquestador (ajústala a tu despliegue real)
ORQUESTADOR_URL = os.getenv("ORQUESTADOR_URL", "http://localhost:8080")

# Nombres de servicios tal y como se registran en el orquestador
# IMPORTANTE: Deben coincidir exactamente con los nombres usados al registrar
GESTOR_PEDIDOS_SERVICE_NAME = os.getenv("GESTOR_PEDIDOS_SERVICE_NAME", "gestor-pedidos")
MONITOR_SERVICE_NAME = os.getenv("MONITOR_SERVICE_NAME", "monitor")

# URLs de fallback si el service discovery falla
GESTOR_PEDIDOS_FALLBACK_URL = os.getenv("GESTOR_PEDIDOS_FALLBACK_URL", "http://localhost:5000")
MONITOR_FALLBACK_URL = os.getenv("MONITOR_FALLBACK_URL", "http://localhost:5001")

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


async def get_service_base_url(service_name: str, fallback_url: Optional[str] = None) -> str:
    """
    Pide al orquestador los datos del servicio (host/port)
    y construye la base URL. Si falla, usa el fallback.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{ORQUESTADOR_URL}/registry/service/{service_name}")
        
        if resp.status_code == 200:
            data = resp.json()
            # El orquestador devuelve: {"status": "success", "service": {...}}
            service_data = data.get("service", {})
            
            if service_data:
                # El servicio tiene host y port directamente
                host = service_data.get("host")
                port = service_data.get("port")
                
                if host and port:
                    # Asegurar que el puerto es un entero válido
                    try:
                        port_int = int(port)
                        if 1 <= port_int <= 65535:
                            return f"http://{host}:{port_int}"
                        else:
                            raise ValueError(f"Puerto fuera de rango: {port_int}")
                    except (ValueError, TypeError) as e:
                        print(f"⚠️ Error con puerto '{port}': {e}")
                        # Si el puerto es inválido, intentar usar la URL directamente
                        url = service_data.get("url")
                        if url:
                            return url
            
            # Si no tiene host/port, intentar usar la URL directamente
            url = service_data.get("url")
            if url:
                return url
                
    except (httpx.RequestError, httpx.TimeoutException) as e:
        print(f"⚠️ Error obteniendo servicio '{service_name}' del orquestador: {e}")
        # Si hay fallback, usarlo
        if fallback_url:
            print(f"✅ Usando URL de fallback para '{service_name}': {fallback_url}")
            return fallback_url
        raise HTTPException(
            status_code=502,
            detail=f"Error contactando al orquestador y no hay fallback configurado: {str(e)}"
        )
    
    # Si llegamos aquí, el servicio no está disponible
    if fallback_url:
        print(f"⚠️ Servicio '{service_name}' no encontrado en orquestador, usando fallback: {fallback_url}")
        return fallback_url
    
    raise HTTPException(
        status_code=502,
        detail=f"Servicio '{service_name}' no disponible en el orquestador y no hay fallback configurado"
    )


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
    try:
        body = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parseando JSON: {str(e)}")

    base_url = await get_service_base_url(GESTOR_PEDIDOS_SERVICE_NAME, GESTOR_PEDIDOS_FALLBACK_URL)
    target_url = f"{base_url}/orders"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(target_url, json=body)
            resp.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout llamando a Gestor de Pedidos")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error llamando a Gestor de Pedidos: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error del servicio: {e.response.text}")

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
    para generar el reporte de rutas optimizadas (resumen con stands problemáticos).
    """
    params = {"month": month}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{ORQUESTADOR_URL}/reports/rutas-optimizadas", params=params)
            resp.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout llamando al orquestador")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error llamando al orquestador: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error del orquestador: {e.response.text}")

    # Pasamos tal cual la respuesta del orquestador
    return JSONResponse(status_code=resp.status_code, content=resp.json())

@app.get("/reports/pedidos-con-rutas")
async def get_pedidos_con_rutas(
    month: str = Query(..., description="Mes en formato YYYY-MM, por ejemplo 2025-01")
):
    """
    Obtiene los últimos 10 pedidos del mes anterior con toda su información
    y las rutas optimizadas calculadas para cada uno.
    """
    params = {"month": month}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{ORQUESTADOR_URL}/reports/pedidos-con-rutas", params=params)
            resp.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout llamando al orquestador")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error llamando al orquestador: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error del orquestador: {e.response.text}")

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
    base_url = await get_service_base_url(MONITOR_SERVICE_NAME, MONITOR_FALLBACK_URL)
    target_url = f"{base_url}/logs"
    params = {"limit": limit, "suspicious_only": suspicious_only}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(target_url, params=params)
            resp.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout llamando al Monitor")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error llamando al Monitor: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error del servicio: {e.response.text}")

    return JSONResponse(status_code=resp.status_code, content=resp.json())


@app.get("/monitor/stats")
async def get_monitor_stats():
    """
    Stats agregadas de seguridad a través del gateway.
    """
    base_url = await get_service_base_url(MONITOR_SERVICE_NAME, MONITOR_FALLBACK_URL)
    target_url = f"{base_url}/stats"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(target_url)
            resp.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout llamando al Monitor")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error llamando al Monitor: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error del servicio: {e.response.text}")

    return JSONResponse(status_code=resp.status_code, content=resp.json())
