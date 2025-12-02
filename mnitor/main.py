"""
Microservicio de Monitoreo para Gestor de Pedidos
Monitorea todas las operaciones del gestor y detecta escalamiento de privilegios indebido
"""

import os
import time
import logging
import pymysql
from datetime import datetime
from typing import Dict, List, Optional
import json
import requests
from flask import Flask, request, jsonify
from threading import Thread
import schedule
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from config import Config

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class DatabaseMonitor:
    """Clase para monitorear la base de datos del gestor de pedidos"""
    
    def __init__(self, config: Dict):
        # Configuración MongoDB para el gestor (para monitoreo)
        self.gestor_mongo_uri = config.get('GESTOR_MONGO_URI', 'mongodb://localhost:27017')
        self.gestor_mongo_db = config.get('GESTOR_MONGO_DB', 'provesi_wms')
        
        # Configuración MySQL para logs (LOGSEGURIDAD)
        self.log_db_config = {
            'host': config.get('LOG_DB_HOST', 'localhost'),
            'port': int(config.get('LOG_DB_PORT', 3306)),
            'user': config.get('LOG_DB_USER', 'root'),
            'password': config.get('LOG_DB_PASSWORD', ''),
            'database': config.get('LOG_DB_NAME', 'LOGSEGURIDAD'),
            'charset': 'utf8mb4'
        }
        
        self.gestor_api_url = config.get('GESTOR_API_URL', 'http://localhost:5000')
        self.monitor_interval = int(config.get('MONITOR_INTERVAL', 30))  # segundos
        
        # Cliente MongoDB para monitorear el gestor
        self.gestor_client = None
        self._init_gestor_client()
    
    def _init_gestor_client(self):
        """Inicializa el cliente de MongoDB para monitorear el gestor"""
        try:
            self.gestor_client = MongoClient(self.gestor_mongo_uri)
            # Verificar conexión
            self.gestor_client.admin.command('ping')
            logger.info("Conexión a MongoDB del gestor establecida correctamente")
        except ConnectionFailure as e:
            logger.error(f"Error conectando a MongoDB del gestor: {e}")
    
    def get_gestor_db(self):
        """Obtiene la base de datos del gestor (MongoDB)"""
        if self.gestor_client is None:
            self._init_gestor_client()
        return self.gestor_client[self.gestor_mongo_db]
    
    def get_log_connection(self):
        """Obtiene conexión a la base de datos de logs (MySQL)"""
        try:
            return pymysql.connect(**self.log_db_config)
        except Exception as e:
            logger.error(f"Error conectando a la BD de logs (MySQL): {e}")
            return None
    
    def log_operation(self, operation_type: str, details: Dict, is_suspicious: bool = False):
        """Registra una operación en la base de datos de logs (MySQL - LOGSEGURIDAD)"""
        conn = self.get_log_connection()
        if not conn:
            logger.error("No se pudo conectar a la base de datos de logs (MySQL)")
            return False
        
        try:
            with conn.cursor() as cursor:
                sql = """
                INSERT INTO operaciones_log 
                (fecha_hora, tipo_operacion, detalles, es_sospechosa, ip_origen, usuario)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    datetime.now(),
                    operation_type,
                    json.dumps(details),
                    is_suspicious,
                    details.get('ip_origen', 'unknown'),
                    details.get('usuario', 'system')
                ))
                conn.commit()
                logger.info(f"Operación registrada: {operation_type} - Sospechosa: {is_suspicious}")
                return True
        except Exception as e:
            logger.error(f"Error registrando operación: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def check_database_operations(self):
        """Monitorea las operaciones en la base de datos del gestor (MongoDB)"""
        try:
            db = self.get_gestor_db()
            
            # Monitorear colecciones y operaciones recientes
            collections = db.list_collection_names()
            
            # Verificar operaciones recientes en la colección de pedidos
            orders_collection = db['orders']
            recent_orders_count = orders_collection.count_documents({
                'created_at': {
                    '$gte': datetime.utcnow().replace(second=0, microsecond=0)
                }
            })
            
            if recent_orders_count > 0:
                self.log_operation(
                    'ORDERS_CREATED',
                    {
                        'count': recent_orders_count,
                        'collection': 'orders'
                    },
                    is_suspicious=False
                )
            
            # Monitorear operaciones de administración sospechosas
            # En MongoDB, las operaciones administrativas se pueden detectar mediante:
            # - Cambios en colecciones del sistema
            # - Operaciones en bases de datos del sistema
            # - Cambios en usuarios y roles
            
            # Verificar si hay operaciones en colecciones del sistema
            system_collections = [col for col in collections if col.startswith('system.')]
            if system_collections:
                self.log_operation(
                    'SYSTEM_COLLECTION_ACCESS',
                    {
                        'collections': system_collections,
                        'warning': 'Acceso a colecciones del sistema detectado'
                    },
                    is_suspicious=True
                )
            
        except Exception as e:
            logger.error(f"Error monitoreando operaciones de BD: {e}")
            self.log_operation(
                'MONITORING_ERROR',
                {
                    'error': str(e),
                    'type': 'database_operations'
                },
                is_suspicious=False
            )
    
    def is_suspicious_operation(self, operation: Dict) -> bool:
        """
        Detecta si una operación de MongoDB es sospechosa (escalamiento de privilegios)
        """
        operation_type = operation.get('operation', '').upper()
        collection = operation.get('collection', '')
        command = operation.get('command', {})
        
        # Operaciones sospechosas en MongoDB
        suspicious_operations = [
            'DROP',  # Eliminar colecciones
            'DROPCOLLECTION',
            'DROPDATABASE',
            'CREATECOLLECTION',  # Crear colecciones nuevas (puede ser sospechoso)
            'CREATEUSER',
            'DROPUSER',
            'GRANTROLES',
            'REVOKEROLES',
            'UPDATEUSER',
            'SHUTDOWN',
            'FSYNC',
            'REPLSETGETSTATUS',
            'REPLSETINITIATE'
        ]
        
        # Verificar operaciones sospechosas
        for suspicious_op in suspicious_operations:
            if suspicious_op in operation_type:
                return True
        
        # Verificar acceso a colecciones del sistema
        if collection.startswith('system.') or collection.startswith('admin.'):
            return True
        
        # Verificar comandos administrativos
        if isinstance(command, dict):
            cmd_keys = [k.upper() for k in command.keys()]
            admin_commands = ['CREATEUSER', 'DROPUSER', 'GRANTROLES', 'REVOKEROLES', 
                            'SHUTDOWN', 'FSYNC', 'REPLSET']
            for admin_cmd in admin_commands:
                if any(admin_cmd in key for key in cmd_keys):
                    return True
        
        return False
    
    def monitor_api_calls(self):
        """Monitorea las llamadas a la API del gestor y detecta operaciones sospechosas"""
        try:
            # Verificar salud de la API
            response = requests.get(
                f"{self.gestor_api_url}/health",
                timeout=5
            )
            if response.status_code == 200:
                self.log_operation(
                    'API_CHECK',
                    {
                        'endpoint': '/health',
                        'status': 'ok',
                        'response_time': response.elapsed.total_seconds()
                    },
                    is_suspicious=False
                )
            
            # Monitorear operaciones recientes en la base de datos del gestor
            # para detectar patrones sospechosos
            db = self.get_gestor_db()
            
            # Verificar si hay cambios recientes en colecciones críticas
            orders_collection = db['orders']
            
            # Obtener últimos pedidos creados
            recent_orders = list(orders_collection.find()
                                .sort('created_at', -1)
                                .limit(5))
            
            for order in recent_orders:
                # Verificar si el pedido tiene características sospechosas
                is_suspicious = False
                suspicious_reasons = []
                
                # Verificar si hay demasiados items (posible ataque de DoS)
                items = order.get('items', [])
                if len(items) > 100:
                    is_suspicious = True
                    suspicious_reasons.append('Excesivo número de items')
                
                # Verificar campos inesperados
                allowed_fields = ['_id', 'erp_order_id', 'items', 'status', 'created_at']
                unexpected_fields = [k for k in order.keys() if k not in allowed_fields]
                if unexpected_fields:
                    is_suspicious = True
                    suspicious_reasons.append(f'Campos inesperados: {unexpected_fields}')
                
                if is_suspicious:
                    self.log_operation(
                        'SUSPICIOUS_ORDER',
                        {
                            'order_id': str(order.get('_id', 'unknown')),
                            'erp_order_id': order.get('erp_order_id', 'unknown'),
                            'reasons': suspicious_reasons,
                            'order_data': {k: v for k, v in order.items() if k != '_id'}
                        },
                        is_suspicious=True
                    )
                else:
                    self.log_operation(
                        'ORDER_CREATED',
                        {
                            'order_id': str(order.get('_id', 'unknown')),
                            'erp_order_id': order.get('erp_order_id', 'unknown'),
                            'items_count': len(items)
                        },
                        is_suspicious=False
                    )
                    
        except Exception as e:
            logger.warning(f"Error monitoreando API del gestor: {e}")
            self.log_operation(
                'API_MONITORING_ERROR',
                {
                    'error': str(e),
                    'type': 'api_monitoring'
                },
                is_suspicious=False
            )
    
    def check_file_system_access(self):
        """Monitorea accesos al sistema de archivos (si es posible)"""
        # Esto requeriría acceso al sistema de archivos de la instancia EC2
        # Por ahora, solo registramos que se ejecutó el check
        self.log_operation(
            'FILE_SYSTEM_CHECK',
            {
                'timestamp': datetime.now().isoformat(),
                'status': 'checked'
            },
            is_suspicious=False
        )
    
    def run_monitoring_cycle(self):
        """Ejecuta un ciclo completo de monitoreo"""
        logger.info("Iniciando ciclo de monitoreo...")
        
        # Monitorear operaciones de base de datos
        self.check_database_operations()
        
        # Monitorear llamadas API
        self.monitor_api_calls()
        
        # Verificar sistema de archivos
        self.check_file_system_access()
        
        logger.info("Ciclo de monitoreo completado")

# Inicializar el monitor usando Config
config_dict = {
    'GESTOR_MONGO_URI': Config.GESTOR_MONGO_URI,
    'GESTOR_MONGO_DB': Config.GESTOR_MONGO_DB,
    'LOG_DB_HOST': Config.LOG_DB_HOST,
    'LOG_DB_PORT': str(Config.LOG_DB_PORT),
    'LOG_DB_USER': Config.LOG_DB_USER,
    'LOG_DB_PASSWORD': Config.LOG_DB_PASSWORD,
    'LOG_DB_NAME': Config.LOG_DB_NAME,
    'GESTOR_API_URL': Config.GESTOR_API_URL,
    'MONITOR_INTERVAL': str(Config.MONITOR_INTERVAL)
}

monitor = DatabaseMonitor(config_dict)

# Endpoints de la API del monitor
@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud del servicio"""
    return jsonify({
        'status': 'healthy',
        'service': 'monitor',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/log', methods=['POST'])
def receive_log():
    """Endpoint para recibir logs del gestor de pedidos"""
    try:
        data = request.json
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No se recibieron datos'
            }), 400
        
        operation_type = data.get('operation_type', 'UNKNOWN')
        details = data.get('details', {})
        is_suspicious = data.get('is_suspicious', False)
        
        # Añadir información de la petición
        details['ip_origen'] = request.remote_addr
        details['user_agent'] = request.headers.get('User-Agent', 'unknown')
        
        # Verificar si la operación es sospechosa
        if monitor.is_suspicious_operation({
            'operation': operation_type,
            'collection': details.get('collection', ''),
            'command': details.get('command', {})
        }):
            is_suspicious = True
        
        monitor.log_operation(operation_type, details, is_suspicious)
        
        return jsonify({
            'status': 'success',
            'message': 'Log registrado correctamente'
        }), 200
    except Exception as e:
        logger.error(f"Error recibiendo log: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """Obtiene los logs registrados desde MySQL (LOGSEGURIDAD)"""
    try:
        conn = monitor.get_log_connection()
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la BD de logs'}), 500
        
        limit = request.args.get('limit', 100, type=int)
        suspicious_only = request.args.get('suspicious_only', 'false').lower() == 'true'
        
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            if suspicious_only:
                sql = """
                    SELECT * FROM operaciones_log 
                    WHERE es_sospechosa = 1 
                    ORDER BY fecha_hora DESC 
                    LIMIT %s
                """
            else:
                sql = """
                    SELECT * FROM operaciones_log 
                    ORDER BY fecha_hora DESC 
                    LIMIT %s
                """
            cursor.execute(sql, (limit,))
            logs = cursor.fetchall()
            
            # Convertir detalles de JSON string a dict
            for log in logs:
                if log.get('detalles'):
                    try:
                        log['detalles'] = json.loads(log['detalles'])
                    except:
                        pass
            
            return jsonify({
                'status': 'success',
                'logs': logs,
                'count': len(logs)
            }), 200
    except Exception as e:
        logger.error(f"Error obteniendo logs: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/stats', methods=['GET'])
def get_stats():
    """Obtiene estadísticas de monitoreo desde MySQL (LOGSEGURIDAD)"""
    try:
        conn = monitor.get_log_connection()
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la BD de logs'}), 500
        
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Total de operaciones
            cursor.execute("SELECT COUNT(*) as total FROM operaciones_log")
            total = cursor.fetchone()['total']
            
            # Operaciones sospechosas
            cursor.execute("SELECT COUNT(*) as total FROM operaciones_log WHERE es_sospechosa = 1")
            suspicious = cursor.fetchone()['total']
            
            # Operaciones por tipo
            cursor.execute("""
                SELECT tipo_operacion, COUNT(*) as cantidad 
                FROM operaciones_log 
                GROUP BY tipo_operacion
                ORDER BY cantidad DESC
            """)
            by_type = cursor.fetchall()
            
            return jsonify({
                'status': 'success',
                'stats': {
                    'total_operaciones': total,
                    'operaciones_sospechosas': suspicious,
                    'operaciones_por_tipo': by_type
                }
            }), 200
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

def run_scheduler():
    """Ejecuta el planificador de tareas de monitoreo"""
    schedule.every(Config.MONITOR_INTERVAL).seconds.do(monitor.run_monitoring_cycle)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    # Inicializar base de datos de logs si no existe
    logger.info("Iniciando microservicio de monitoreo...")
    
    # Iniciar hilo para monitoreo periódico
    monitor_thread = Thread(target=run_scheduler, daemon=True)
    monitor_thread.start()
    
    # Iniciar servidor Flask
    logger.info(f"Servidor de monitoreo iniciado en puerto {Config.MONITOR_PORT}")
    app.run(host='0.0.0.0', port=Config.MONITOR_PORT, debug=False)

