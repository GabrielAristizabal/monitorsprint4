"""
Orquestador de Microservicios
Comunica y coordina los microservicios usando service discovery
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import uvicorn
from .config import Config
from .service_registry import ServiceRegistry
from .report_service import ReportService

# Inicializar registry con TTL desde configuración
registry = ServiceRegistry(ttl=Config.SERVICE_TTL)

app = FastAPI(title="Orquestador de Microservicios", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar servicios
report_service = ReportService()

# ==================== SERVICE REGISTRY ENDPOINTS ====================

@app.post("/registry/register")
async def register_service(service_name: str, host: str, port: int):
    """
    Registra un servicio en el registry.
    Los servicios deben llamar a este endpoint al iniciar.
    """
    registry.register(service_name, host, port)
    return {
        "status": "success",
        "message": f"Servicio {service_name} registrado",
        "service": registry.get_service(service_name)
    }

@app.post("/registry/heartbeat/{service_name}")
async def heartbeat(service_name: str):
    """Endpoint para heartbeat de servicios"""
    success = registry.heartbeat(service_name)
    if success:
        return {"status": "success", "message": f"Heartbeat recibido de {service_name}"}
    else:
        raise HTTPException(status_code=404, detail=f"Servicio {service_name} no encontrado")

@app.get("/registry/services")
async def list_services():
    """Lista todos los servicios registrados"""
    services = registry.list_services()
    return {
        "status": "success",
        "services": services,
        "count": len(services)
    }

@app.get("/registry/service/{service_name}")
async def get_service(service_name: str):
    """Obtiene información de un servicio específico"""
    service = registry.get_service(service_name)
    if service:
        return {"status": "success", "service": service}
    else:
        raise HTTPException(status_code=404, detail=f"Servicio {service_name} no encontrado")

@app.delete("/registry/service/{service_name}")
async def unregister_service(service_name: str):
    """Desregistra un servicio"""
    success = registry.unregister(service_name)
    if success:
        return {"status": "success", "message": f"Servicio {service_name} desregistrado"}
    else:
        raise HTTPException(status_code=404, detail=f"Servicio {service_name} no encontrado")

# ==================== REPORT ENDPOINTS ====================

@app.get("/reports/rutas-optimizadas")
async def get_rutas_optimizadas_report(month: str = Query(..., description="Mes en formato YYYY-MM")):
    """
    Genera reporte de rutas optimizadas para los últimos 10 pedidos del mes anterior.
    Identifica stands donde no se estima correctamente el tiempo de preparación.
    
    Requisitos:
    - Respuesta en menos de 1 segundo
    - Relaciona datos de GestorPedidos con ruta_optima
    - Compara tiempos estimados vs reales por stand
    """
    try:
        report = report_service.generate_route_report(month)
        
        # Verificar que el tiempo de procesamiento sea < 1 segundo
        if report.get('processing_time_ms', 0) > 1000:
            return {
                "status": "warning",
                "message": "El reporte tardó más de 1 segundo en generarse",
                **report
            }
        
        return {
            "status": "success",
            **report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/pedidos-con-rutas")
async def get_pedidos_con_rutas(month: str = Query(..., description="Mes en formato YYYY-MM")):
    """
    Obtiene los últimos 10 pedidos del mes anterior con toda su información
    y las rutas optimizadas calculadas para cada uno.
    """
    try:
        result = report_service.get_orders_with_routes_detailed(month)
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check del orquestador"""
    services = registry.list_services()
    return {
        "status": "healthy",
        "service": "orquestador",
        "registered_services": len(services),
        "services": [s['name'] for s in services]
    }

if __name__ == "__main__":
    uvicorn.run(
        "orquestador.main:app",
        host="0.0.0.0",
        port=Config.ORCHESTRATOR_PORT,
        reload=False
    )

