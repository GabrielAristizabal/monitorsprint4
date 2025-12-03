from fastapi import FastAPI
from .api import health, orders, reports

app = FastAPI(title="Provesi Orders Mongo Service")

app.include_router(health.router)
app.include_router(orders.router)
app.include_router(reports.router)
