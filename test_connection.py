#!/usr/bin/env python3
"""
Script de prueba de conectividad
Verifica que todas las conexiones estén configuradas correctamente
"""

import sys
import pymysql
import requests
from config import Config

def test_gestor_db():
    """Prueba conexión a base de datos del gestor"""
    print("Probando conexión a BD del gestor...")
    try:
        conn = pymysql.connect(
            host=Config.GESTOR_DB_HOST,
            port=Config.GESTOR_DB_PORT,
            user=Config.GESTOR_DB_USER,
            password=Config.GESTOR_DB_PASSWORD,
            database=Config.GESTOR_DB_NAME,
            charset='utf8mb4'
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        conn.close()
        print("✅ Conexión a BD del gestor: OK")
        return True
    except Exception as e:
        print(f"❌ Error conectando a BD del gestor: {e}")
        return False

def test_log_db():
    """Prueba conexión a base de datos de logs"""
    print("Probando conexión a BD de logs (LOGSEGURIDAD)...")
    try:
        conn = pymysql.connect(
            host=Config.LOG_DB_HOST,
            port=Config.LOG_DB_PORT,
            user=Config.LOG_DB_USER,
            password=Config.LOG_DB_PASSWORD,
            database=Config.LOG_DB_NAME,
            charset='utf8mb4'
        )
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"   Tablas encontradas: {len(tables)}")
        conn.close()
        print("✅ Conexión a BD de logs: OK")
        return True
    except Exception as e:
        print(f"❌ Error conectando a BD de logs: {e}")
        return False

def test_gestor_api():
    """Prueba conexión a API del gestor"""
    print("Probando conexión a API del gestor...")
    try:
        response = requests.get(
            f"{Config.GESTOR_API_URL}/health",
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Conexión a API del gestor: OK")
            return True
        else:
            print(f"⚠️  API respondió con código: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"⚠️  No se pudo conectar a la API del gestor: {e}")
        print("   (Esto puede ser normal si la API no está disponible)")
        return False

def main():
    print("=" * 50)
    print("Prueba de Conectividad - Microservicio de Monitoreo")
    print("=" * 50)
    print()
    
    results = []
    results.append(("BD Gestor", test_gestor_db()))
    results.append(("BD Logs", test_log_db()))
    results.append(("API Gestor", test_gestor_api()))
    
    print()
    print("=" * 50)
    print("Resumen:")
    print("=" * 50)
    
    all_ok = True
    for name, result in results:
        status = "✅ OK" if result else "❌ FALLO"
        print(f"{name}: {status}")
        if not result:
            all_ok = False
    
    print()
    if all_ok:
        print("✅ Todas las conexiones están funcionando correctamente")
        return 0
    else:
        print("❌ Algunas conexiones fallaron. Revisa la configuración en .env")
        return 1

if __name__ == '__main__':
    sys.exit(main())

