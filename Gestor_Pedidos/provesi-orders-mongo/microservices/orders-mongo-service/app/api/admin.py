# app/api/admin.py
from fastapi import APIRouter, Header, HTTPException
import os
import signal
import threading

router = APIRouter(prefix="/admin", tags=["admin"])

# Token que solo debe conocer el monitor
MONITOR_TOKEN = os.getenv("MONITOR_TOKEN", "cambia-este-token")

def _stop_process_gracefully():
    """
    Mata el proceso actual (uvicorn) con SIGINT después de responder al cliente.
    """
    pid = os.getpid()
    os.kill(pid, signal.SIGINT)

@router.post("/shutdown")
def shutdown_service(x_monitor_token: str = Header(..., alias="X-Monitor-Token")):
    # 1) Validar que la llamada venga del monitor
    if x_monitor_token != MONITOR_TOKEN:
        raise HTTPException(status_code=403, detail="Not allowed")

    # 2) Lanzar un thread para apagar el proceso después de responder
    threading.Thread(target=_stop_process_gracefully).start()

    return {"detail": "Shutdown iniciado por el monitor"}
