from threading import Thread
from fastapi import FastAPI, Header, HTTPException
import os
import time
from .api import health, orders, reports
from .api import admin as admin_router

app = FastAPI(title="Provesi Orders Mongo Service")

app.include_router(health.router)
app.include_router(orders.router)
app.include_router(reports.router)
app.include_router(admin_router.router)

ADMIN_TOKEN = os.getenv("GESTOR_ADMIN_TOKEN", "supersecreto123")

@app.post("/admin/shutdown")
def shutdown(x_admin_token: str = Header(...)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Apagamos el servidor en un hilo aparte para responder al monitor
    def stopper():
        time.sleep(0.2)
        os._exit(0)

    Thread(target=stopper, daemon=True).start()
    return {"status": "shutting_down"}