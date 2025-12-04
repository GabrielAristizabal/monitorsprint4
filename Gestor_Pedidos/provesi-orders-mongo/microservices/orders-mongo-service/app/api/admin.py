from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import os
import signal
import threading
import time

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

class BlockRequest(BaseModel):
    reason: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

def _delayed_shutdown(delay: float = 0.5):
    """
    Apaga el proceso de uvicorn después de un pequeño delay
    para que la respuesta 200 llegue al monitor.
    """
    time.sleep(delay)
    logger.warning("Apagando proceso de uvicorn por bloqueo remoto...")
    os.kill(os.getpid(), signal.SIGTERM)

@router.post("/block")
async def block_service(body: BlockRequest):
    """
    Endpoint llamado por el monitor cuando detecta elevación de privilegios.
    Responde 200 y, en segundo plano, termina el proceso.
    """
    logger.warning(f"Bloqueo remoto solicitado por monitor. Motivo: {body.reason} Extra: {body.extra}")
    t = threading.Thread(target=_delayed_shutdown, kwargs={"delay": 0.5}, daemon=True)
    t.start()
    return {"status": "stopping", "reason": body.reason}
