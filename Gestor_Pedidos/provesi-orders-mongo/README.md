Provesi WMS – Orders Service con MongoDB
=======================================

Este proyecto contiene un microservicio de gestión de pedidos para el WMS de Provesi,
usando FastAPI y MongoDB (vía Motor). Incluye estructura preparada para:

- Crear pedidos.
- Exponer un endpoint de salud.
- Exponer un endpoint de reporte de rutas optimizadas de los últimos 10 pedidos.
- Aislar el algoritmo de rutas en un módulo independiente (facilidad de modificación).
- Estructura para futuras reglas de seguridad y detección de elevación de privilegios.

Para ejecutar localmente:

    pip install -r microservices/orders-mongo-service/requirements.txt
    uvicorn microservices.orders-mongo-service.app.main:app --reload

(asegúrate de que el módulo sea importable ajustando el PYTHONPATH o ejecutando desde la raíz del proyecto)
