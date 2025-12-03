from fastapi import Request

# En esta versión mínima, solo definimos la estructura para futuras reglas de seguridad.
# Más adelante se puede implementar aquí la detección de elevación de privilegios.

async def register_security_event(request: Request, action: str, allowed: bool) -> None:
    # TODO: Persistir en una colección security_events de MongoDB.
    # Por ahora solo dejamos el gancho.
    return None
