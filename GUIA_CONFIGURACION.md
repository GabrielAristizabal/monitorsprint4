# 🔧 Guía de Configuración del Monitor

## 📍 PARTE 1: Configurar la IP del Gestor

### Paso 1: Crear archivo `.env`

Si no existe, crea un archivo llamado `.env` en la raíz del proyecto (copia desde `env.example`):

```bash
cp env.example .env
```

### Paso 2: Editar `.env` con las IPs reales

**Archivo: `.env`** (líneas 3, 11, 19)

```env
# ⚠️ CAMBIAR ESTA IP - Base de datos del gestor
GESTOR_DB_HOST=172.31.XX.XX          # ← IP privada de la instancia EC2 del gestor
GESTOR_DB_PORT=3306
GESTOR_DB_USER=gestor_user            # ← Usuario de MySQL del gestor
GESTOR_DB_PASSWORD=tu_password_aqui   # ← Password de MySQL del gestor
GESTOR_DB_NAME=pedidos               # ← Nombre de la base de datos del gestor

# ⚠️ CAMBIAR ESTA IP - Base de datos de logs
LOG_DB_HOST=172.31.XX.XX             # ← IP donde está LOGSEGURIDAD (puede ser la misma)
LOG_DB_PORT=3306
LOG_DB_USER=log_user                 # ← Usuario para LOGSEGURIDAD
LOG_DB_PASSWORD=tu_password_aqui     # ← Password para LOGSEGURIDAD
LOG_DB_NAME=LOGSEGURIDAD

# ⚠️ CAMBIAR ESTA IP - API del gestor
GESTOR_API_URL=http://172.31.XX.XX:5000  # ← IP y puerto de la API del gestor

# Configuración del monitor
MONITOR_PORT=5001
MONITOR_INTERVAL=30                   # ← Cada cuántos segundos monitorea (30 = cada 30 seg)
```

**Ejemplo con IPs reales:**
```env
GESTOR_DB_HOST=172.31.15.10
GESTOR_DB_USER=admin
GESTOR_DB_PASSWORD=miPassword123
GESTOR_DB_NAME=pedidos

LOG_DB_HOST=172.31.15.10
LOG_DB_USER=log_admin
LOG_DB_PASSWORD=miPasswordLogs123
LOG_DB_NAME=LOGSEGURIDAD

GESTOR_API_URL=http://172.31.15.10:5000
```

---

## 📍 PARTE 2: Configurar QUÉ Monitorear

### Archivo: `main.py`

### 2.1. Tablas Permitidas (Líneas 147-150 y 182)

**Ubicación:** Función `is_suspicious_query()` en `main.py`

**Líneas 147-150:** Lista de tablas permitidas en operaciones SELECT
```python
# Operaciones permitidas (solo crear/registrar pedidos y reportes)
allowed_patterns = [
    'SELECT',  # Para reportes
    'INSERT INTO',  # Para crear pedidos
    'UPDATE',  # Para actualizar pedidos (si es necesario)
    'FROM pedidos',      # ← TABLA PERMITIDA
    'FROM productos',    # ← TABLA PERMITIDA
    'FROM clientes',     # ← TABLA PERMITIDA
    'FROM reportes'      # ← TABLA PERMITIDA
]
```

**Línea 182:** Tablas permitidas para INSERT/UPDATE
```python
# Verificar que las operaciones permitidas sean solo en tablas permitidas
if 'INSERT' in query_upper or 'UPDATE' in query_upper:
    if not any(allowed in query_upper for allowed in ['pedidos', 'productos', 'clientes']):
        # ↑ AQUÍ: Agrega o quita nombres de tablas permitidas
        return True
```

**Ejemplo:** Si tu gestor tiene tablas `inventario`, `almacen`, `movimientos`:
```python
# Líneas 147-150
allowed_patterns = [
    'SELECT',
    'INSERT INTO',
    'UPDATE',
    'FROM pedidos',
    'FROM productos',
    'FROM clientes',
    'FROM inventario',    # ← AGREGAR
    'FROM almacen',       # ← AGREGAR
    'FROM movimientos'    # ← AGREGAR
]

# Línea 182
if not any(allowed in query_upper for allowed in ['pedidos', 'productos', 'clientes', 'inventario', 'almacen', 'movimientos']):
    # ↑ AGREGAR las nuevas tablas aquí también
```

### 2.2. Operaciones Sospechosas (Líneas 154-173)

**Ubicación:** Función `is_suspicious_query()` en `main.py`

**Líneas 154-173:** Patrones de operaciones que se consideran sospechosas
```python
# Operaciones sospechosas (escalamiento de privilegios)
suspicious_patterns = [
    'DROP',              # ← Eliminar tablas/bases de datos
    'DELETE FROM',       # ← Eliminar registros (si no está permitido)
    'TRUNCATE',          # ← Vaciar tablas
    'ALTER TABLE',       # ← Modificar estructura
    'CREATE TABLE',      # ← Crear tablas
    'CREATE DATABASE',   # ← Crear bases de datos
    'GRANT',             # ← Otorgar privilegios
    'REVOKE',            # ← Revocar privilegios
    'FLUSH PRIVILEGES',  # ← Actualizar privilegios
    'SET PASSWORD',      # ← Cambiar passwords
    'CREATE USER',       # ← Crear usuarios
    'DROP USER',         # ← Eliminar usuarios
    'RENAME USER',       # ← Renombrar usuarios
    'SHOW GRANTS',       # ← Ver privilegios
    'INFORMATION_SCHEMA',# ← Acceso a metadatos
    'mysql.',            # ← Tablas del sistema MySQL
    'performance_schema',# ← Schema de performance
    'sys.'               # ← Schema del sistema
]
```

**Para agregar más operaciones sospechosas:**
```python
suspicious_patterns = [
    'DROP',
    'DELETE FROM',
    # ... (patrones existentes)
    'EXEC',              # ← AGREGAR: Ejecutar procedimientos
    'CALL',              # ← AGREGAR: Llamar funciones
    'LOAD DATA',         # ← AGREGAR: Cargar datos desde archivos
]
```

### 2.3. Permitir DELETE (si es necesario)

Si tu gestor necesita hacer DELETE en ciertas tablas, modifica la línea 156:

```python
# Opción A: Permitir DELETE solo en tablas específicas
# Elimina 'DELETE FROM' de suspicious_patterns y agrega validación:

if 'DELETE FROM' in query_upper:
    # Solo permitir DELETE en tablas específicas
    if not any(allowed in query_upper for allowed in ['pedidos', 'productos']):
        return True  # Es sospechoso si no es en tablas permitidas
```

---

## 📋 Resumen de Archivos a Modificar

| Archivo | Líneas | Qué Modificar |
|---------|--------|---------------|
| **`.env`** | 3, 11, 19 | IPs del gestor, BD de logs, API |
| **`main.py`** | 147-150 | Tablas permitidas en SELECT |
| **`main.py`** | 182 | Tablas permitidas en INSERT/UPDATE |
| **`main.py`** | 154-173 | Operaciones sospechosas (agregar/quitar) |

---

## ✅ Verificación

Después de hacer los cambios:

1. **Probar conexiones:**
   ```bash
   python test_connection.py
   ```

2. **Iniciar el monitor:**
   ```bash
   python main.py
   ```

3. **Verificar que monitorea correctamente:**
   ```bash
   curl http://localhost:5001/stats
   ```

---

## 🔍 Ejemplo Completo de Modificación

Si tu gestor tiene estas tablas: `pedidos`, `productos`, `clientes`, `inventario`, `almacen`

**En `main.py` línea 147-150:**
```python
allowed_patterns = [
    'SELECT',
    'INSERT INTO',
    'UPDATE',
    'FROM pedidos',
    'FROM productos',
    'FROM clientes',
    'FROM inventario',    # ← AGREGADO
    'FROM almacen'        # ← AGREGADO
]
```

**En `main.py` línea 182:**
```python
if not any(allowed in query_upper for allowed in ['pedidos', 'productos', 'clientes', 'inventario', 'almacen']):
    # ↑ AGREGADAS las nuevas tablas
    return True
```

