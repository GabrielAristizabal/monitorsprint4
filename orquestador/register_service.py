"""
Script de ejemplo para registrar un servicio en el orquestador
Los microservicios deben llamar a este script o implementar esta lógica al iniciar
"""
import requests
import time
import sys
from typing import Optional

def register_service(service_name: str, host: str, port: int, orchestrator_url: str = "http://localhost:8080"):
    """
    Registra un servicio en el orquestador
    
    Args:
        service_name: Nombre del servicio (ej: 'gestor-pedidos', 'ruta-optima')
        host: IP o hostname del servicio
        port: Puerto del servicio
        orchestrator_url: URL del orquestador
    """
    try:
        response = requests.post(
            f"{orchestrator_url}/registry/register",
            params={
                "service_name": service_name,
                "host": host,
                "port": port
            },
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Servicio {service_name} registrado exitosamente")
            return True
        else:
            print(f"❌ Error registrando servicio: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al orquestador: {e}")
        return False

def send_heartbeat(service_name: str, orchestrator_url: str = "http://localhost:8080"):
    """Envía heartbeat al orquestador"""
    try:
        response = requests.post(
            f"{orchestrator_url}/registry/heartbeat/{service_name}",
            timeout=2
        )
        return response.status_code == 200
    except:
        return False

def start_heartbeat_loop(service_name: str, interval: int = 10, orchestrator_url: str = "http://localhost:8080"):
    """
    Inicia un loop para enviar heartbeat periódicamente
    
    Args:
        service_name: Nombre del servicio
        interval: Intervalo en segundos entre heartbeats
        orchestrator_url: URL del orquestador
    """
    print(f"🔄 Iniciando heartbeat loop para {service_name} (cada {interval}s)")
    
    while True:
        try:
            if send_heartbeat(service_name, orchestrator_url):
                print(f"💓 Heartbeat enviado: {service_name}")
            else:
                print(f"⚠️ Error enviando heartbeat: {service_name}")
            time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n🛑 Deteniendo heartbeat loop para {service_name}")
            break
        except Exception as e:
            print(f"❌ Error en heartbeat loop: {e}")
            time.sleep(interval)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python register_service.py <service_name> <host> <port> [orchestrator_url]")
        print("Ejemplo: python register_service.py gestor-pedidos 172.31.15.10 5000")
        sys.exit(1)
    
    service_name = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])
    orchestrator_url = sys.argv[4] if len(sys.argv) > 4 else "http://localhost:8080"
    
    # Registrar servicio
    if register_service(service_name, host, port, orchestrator_url):
        # Iniciar heartbeat loop
        start_heartbeat_loop(service_name, interval=10, orchestrator_url=orchestrator_url)
    else:
        sys.exit(1)

