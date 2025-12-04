from fastapi import FastAPI
from .api import health, orders, reports
from .api import admin as admin_router

app = FastAPI(title="Provesi Orders Mongo Service")

app.include_router(health.router)
app.include_router(orders.router)
app.include_router(reports.router)
app.include_router(admin_router.router)