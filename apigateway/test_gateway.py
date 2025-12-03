"""
Script de prueba para verificar que el gateway funciona
"""
import requests
import sys

GATEWAY_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:9000"

print(f"🔍 Probando gateway en: {GATEWAY_URL}\n")

# Test 1: Health check
print("1. Health check...")
try:
    resp = requests.get(f"{GATEWAY_URL}/health", timeout=5)
    print(f"   ✅ Status: {resp.status_code}")
    print(f"   📄 Response: {resp.json()}")
except requests.exceptions.ConnectionError:
    print(f"   ❌ Error: No se pudo conectar a {GATEWAY_URL}")
    print(f"   💡 Verifica que el gateway esté corriendo y escuchando en el puerto correcto")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n✅ Gateway está funcionando correctamente!")

