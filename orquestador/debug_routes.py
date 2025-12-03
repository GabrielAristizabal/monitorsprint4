"""
Script de diagnóstico para verificar rutas en ruta_optima
"""
import requests
import sys
from config import Config

def check_route_service(order_id: str):
    """Verifica si existe una ruta para un pedido"""
    url = Config.RUTA_OPTIMA_URL or "http://localhost:8000"
    endpoint = f"{url}/ruta/{order_id}/"
    
    print(f"🔍 Verificando ruta para pedido: {order_id}")
    print(f"📍 URL: {endpoint}")
    
    try:
        response = requests.get(endpoint, timeout=5)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ruta encontrada: {data.get('status')}")
            return data.get('ruta')
        elif response.status_code == 404:
            data = response.json()
            print(f"⚠️ Ruta no encontrada: {data.get('mensaje')}")
            return None
        else:
            print(f"❌ Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def list_all_routes():
    """Lista todas las rutas en la base de datos (requiere acceso directo a MongoDB)"""
    print("\n📋 Para ver todas las rutas en MongoDB, ejecuta:")
    print("   mongo <tu_uri_mongo>")
    print("   use <tu_db>")
    print("   db.calculated_routes.find().pretty()")
    print("\n   O verifica qué pedido_id se usó al guardar:")
    print("   db.calculated_routes.find({}, {pedido_id: 1}).pretty()")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python debug_routes.py <erp_order_id>")
        print("\nEjemplo:")
        print("  python debug_routes.py ORD-2025-01-001")
        sys.exit(1)
    
    order_id = sys.argv[1]
    check_route_service(order_id)
    list_all_routes()

