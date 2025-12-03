"""
Service Registry para descubrimiento de servicios
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import threading
import time

class ServiceRegistry:
    """
    Registry simple para service discovery.
    Los servicios se registran automáticamente al iniciar.
    """
    
    def __init__(self, ttl: int = 30):
        self._services: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        self._ttl = ttl  # Tiempo de vida en segundos
        
    def register(self, service_name: str, host: str, port: int, metadata: Optional[Dict] = None):
        """
        Registra un servicio en el registry
        
        Args:
            service_name: Nombre del servicio (ej: 'gestor-pedidos', 'ruta-optima')
            host: IP o hostname del servicio
            port: Puerto del servicio
            metadata: Información adicional del servicio
        """
        with self._lock:
            service_key = f"{service_name}"
            self._services[service_key] = {
                'name': service_name,
                'host': host,
                'port': port,
                'url': f"http://{host}:{port}",
                'metadata': metadata or {},
                'registered_at': datetime.utcnow(),
                'last_heartbeat': datetime.utcnow(),
                'status': 'healthy'
            }
            print(f"✅ Servicio registrado: {service_name} en {host}:{port}")
    
    def heartbeat(self, service_name: str):
        """Actualiza el heartbeat de un servicio"""
        with self._lock:
            service_key = f"{service_name}"
            if service_key in self._services:
                self._services[service_key]['last_heartbeat'] = datetime.utcnow()
                self._services[service_key]['status'] = 'healthy'
                return True
            return False
    
    def get_service(self, service_name: str) -> Optional[Dict]:
        """
        Obtiene la información de un servicio
        
        Returns:
            Dict con información del servicio o None si no existe
        """
        with self._lock:
            service_key = f"{service_name}"
            service = self._services.get(service_key)
            
            if service:
                # Verificar si el servicio sigue activo
                time_since_heartbeat = (datetime.utcnow() - service['last_heartbeat']).total_seconds()
                if time_since_heartbeat > self._ttl:
                    service['status'] = 'unhealthy'
                    return None
                
                return service
            return None
    
    def get_service_url(self, service_name: str) -> Optional[str]:
        """Obtiene la URL de un servicio"""
        service = self.get_service(service_name)
        if service:
            return service['url']
        return None
    
    def list_services(self) -> List[Dict]:
        """Lista todos los servicios registrados"""
        with self._lock:
            # Filtrar servicios expirados
            now = datetime.utcnow()
            active_services = []
            
            for service_key, service in self._services.items():
                time_since_heartbeat = (now - service['last_heartbeat']).total_seconds()
                if time_since_heartbeat <= self._ttl:
                    active_services.append(service.copy())
                else:
                    service['status'] = 'unhealthy'
            
            return active_services
    
    def unregister(self, service_name: str):
        """Elimina un servicio del registry"""
        with self._lock:
            service_key = f"{service_name}"
            if service_key in self._services:
                del self._services[service_key]
                print(f"❌ Servicio desregistrado: {service_name}")
                return True
            return False
    
    def cleanup_expired(self):
        """Limpia servicios expirados"""
        with self._lock:
            now = datetime.utcnow()
            expired = []
            
            for service_key, service in self._services.items():
                time_since_heartbeat = (now - service['last_heartbeat']).total_seconds()
                if time_since_heartbeat > self._ttl:
                    expired.append(service_key)
            
            for key in expired:
                del self._services[key]
                print(f"🧹 Servicio expirado eliminado: {key}")

# Instancia global del registry
# Se inicializará con TTL desde Config en main.py
registry = None

