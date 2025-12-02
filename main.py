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
        self.gestor_db_config = {
            'host': config.get('GESTOR_DB_HOST', 'localhost'),
            'port': int(config.get('GESTOR_DB_PORT', 3306)),
            'user': config.get('GESTOR_DB_USER', 'root'),
            'password': config.get('GESTOR_DB_PASSWORD', ''),
            'database': config.get('GESTOR_DB_NAME', 'pedidos'),
            'charset': 'utf8mb4'
        }
        
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
        
    def get_connection(self, db_type: str = 'log'):
        """Obtiene conexión a la base de datos"""
        config = self.log_db_config if db_type == 'log' else self.gestor_db_config
        try:
            return pymysql.connect(**config)
        except Exception as e:
            logger.error(f"Error conectando a {db_type} DB: {e}")
            return None
    
    def log_operation(self, operation_type: str, details: Dict, is_suspicious: bool = False):
        """Registra una operación en la base de datos de logs"""
        conn = self.get_connection('log')
        if not conn:
            logger.error("No se pudo conectar a la base de datos de logs")
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
        """Monitorea las operaciones en la base de datos del gestor"""
        conn = self.get_connection('gestor')
        if not conn:
            logger.warning("No se pudo conectar a la base de datos del gestor")
            return
        
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                # Verificar operaciones recientes en tablas de pedidos
                # Asumiendo que hay una tabla de pedidos con timestamp
                cursor.execute("""
                    SELECT COUNT(*) as total_operaciones
                    FROM information_schema.tables 
                    WHERE table_schema = %s
                """, (self.gestor_db_config['database'],))
                
                # Monitorear queries recientes (si está habilitado el log de queries)
                # Esto requiere que MySQL tenga habilitado el general_log
                cursor.execute("SHOW PROCESSLIST")
                processes = cursor.fetchall()
                
                for process in processes:
                    if process['User'] == self.gestor_db_config['user']:
                        query = process.get('Info', '')
                        if query and self.is_suspicious_query(query):
                            self.log_operation(
                                'QUERY_SOSPECHOSA',
                                {
                                    'query': query,
                                    'process_id': process['Id'],
                                    'tiempo_ejecucion': process.get('Time', 0),
                                    'estado': process.get('State', '')
                                },
                                is_suspicious=True
                            )
        except Exception as e:
            logger.error(f"Error monitoreando operaciones de BD: {e}")
        finally:
            conn.close()
    
    def is_suspicious_query(self, query: str) -> bool:
        """Detecta si una query es sospechosa (escalamiento de privilegios)"""
        if not query:
            return False
        
        query_upper = query.upper().strip()
        
        # Operaciones permitidas (solo crear/registrar pedidos y reportes)
        allowed_patterns = [
            'SELECT',  # Para reportes
            'INSERT INTO',  # Para crear pedidos
            'UPDATE',  # Para actualizar pedidos (si es necesario)
            'FROM pedidos',
            'FROM productos',
            'FROM clientes',
            'FROM reportes'
        ]
        
        # Operaciones sospechosas (escalamiento de privilegios)
        suspicious_patterns = [
            'DROP',
            'DELETE FROM',  # Si no está permitido
            'TRUNCATE',
            'ALTER TABLE',
            'CREATE TABLE',
            'CREATE DATABASE',
            'GRANT',
            'REVOKE',
            'FLUSH PRIVILEGES',
            'SET PASSWORD',
            'CREATE USER',
            'DROP USER',
            'RENAME USER',
            'SHOW GRANTS',
            'INFORMATION_SCHEMA',  # Acceso a metadatos del sistema
            'mysql.',  # Acceso a tablas del sistema
            'performance_schema',
            'sys.'
        ]
        
        # Verificar si contiene patrones sospechosos
        for pattern in suspicious_patterns:
            if pattern in query_upper:
                return True
        
        # Verificar que las operaciones permitidas sean solo en tablas permitidas
        if 'INSERT' in query_upper or 'UPDATE' in query_upper:
            if not any(allowed in query_upper for allowed in ['pedidos', 'productos', 'clientes']):
                return True
        
        return False
    
    def monitor_api_calls(self):
        """Monitorea las llamadas a la API del gestor (si está disponible)"""
        try:
            # Intentar obtener logs de la API del gestor
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
        except Exception as e:
            logger.warning(f"No se pudo conectar a la API del gestor: {e}")
            self.log_operation(
                'API_CHECK',
                {
                    'endpoint': '/health',
                    'status': 'error',
                    'error': str(e)
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
    'GESTOR_DB_HOST': Config.GESTOR_DB_HOST,
    'GESTOR_DB_PORT': str(Config.GESTOR_DB_PORT),
    'GESTOR_DB_USER': Config.GESTOR_DB_USER,
    'GESTOR_DB_PASSWORD': Config.GESTOR_DB_PASSWORD,
    'GESTOR_DB_NAME': Config.GESTOR_DB_NAME,
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
        operation_type = data.get('operation_type', 'UNKNOWN')
        details = data.get('details', {})
        is_suspicious = data.get('is_suspicious', False)
        
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
    """Obtiene los logs registrados"""
    try:
        conn = monitor.get_connection('log')
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
    """Obtiene estadísticas de monitoreo"""
    try:
        conn = monitor.get_connection('log')
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

