-- Esquema de base de datos para LOGSEGURIDAD
-- Base de datos para almacenar todos los logs de operaciones del gestor de pedidos

CREATE DATABASE IF NOT EXISTS LOGSEGURIDAD CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE LOGSEGURIDAD;

-- Tabla principal de logs de operaciones
CREATE TABLE IF NOT EXISTS operaciones_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_operacion VARCHAR(100) NOT NULL,
    detalles JSON,
    es_sospechosa BOOLEAN DEFAULT FALSE,
    ip_origen VARCHAR(45),
    usuario VARCHAR(100),
    INDEX idx_fecha_hora (fecha_hora),
    INDEX idx_tipo_operacion (tipo_operacion),
    INDEX idx_es_sospechosa (es_sospechosa),
    INDEX idx_usuario (usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de alertas de seguridad
CREATE TABLE IF NOT EXISTS alertas_seguridad (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    nivel_alerta ENUM('BAJA', 'MEDIA', 'ALTA', 'CRITICA') DEFAULT 'MEDIA',
    tipo_alerta VARCHAR(100) NOT NULL,
    descripcion TEXT,
    operacion_id INT,
    resuelta BOOLEAN DEFAULT FALSE,
    fecha_resolucion DATETIME NULL,
    FOREIGN KEY (operacion_id) REFERENCES operaciones_log(id) ON DELETE SET NULL,
    INDEX idx_fecha_hora (fecha_hora),
    INDEX idx_nivel_alerta (nivel_alerta),
    INDEX idx_resuelta (resuelta)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de configuración de reglas de monitoreo
CREATE TABLE IF NOT EXISTS reglas_monitoreo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_regla VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    patron_deteccion TEXT,
    nivel_alerta ENUM('BAJA', 'MEDIA', 'ALTA', 'CRITICA') DEFAULT 'MEDIA',
    activa BOOLEAN DEFAULT TRUE,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar reglas de monitoreo por defecto
INSERT INTO reglas_monitoreo (nombre_regla, descripcion, patron_deteccion, nivel_alerta) VALUES
('DROP_TABLE', 'Detección de intentos de eliminar tablas', 'DROP', 'CRITICA'),
('ALTER_TABLE', 'Detección de intentos de modificar estructura de tablas', 'ALTER TABLE', 'ALTA'),
('GRANT_PRIVILEGES', 'Detección de intentos de otorgar privilegios', 'GRANT', 'CRITICA'),
('CREATE_USER', 'Detección de intentos de crear usuarios', 'CREATE USER', 'CRITICA'),
('SYSTEM_TABLES', 'Detección de acceso a tablas del sistema', 'INFORMATION_SCHEMA|mysql\.|performance_schema', 'ALTA'),
('DELETE_OPERATIONS', 'Detección de operaciones DELETE no autorizadas', 'DELETE FROM', 'MEDIA')
ON DUPLICATE KEY UPDATE descripcion=VALUES(descripcion);

-- Vista para operaciones sospechosas recientes
CREATE OR REPLACE VIEW vista_operaciones_sospechosas AS
SELECT 
    id,
    fecha_hora,
    tipo_operacion,
    detalles,
    ip_origen,
    usuario
FROM operaciones_log
WHERE es_sospechosa = TRUE
ORDER BY fecha_hora DESC;

-- Vista para estadísticas diarias
CREATE OR REPLACE VIEW vista_estadisticas_diarias AS
SELECT 
    DATE(fecha_hora) as fecha,
    COUNT(*) as total_operaciones,
    SUM(CASE WHEN es_sospechosa = TRUE THEN 1 ELSE 0 END) as operaciones_sospechosas,
    COUNT(DISTINCT tipo_operacion) as tipos_operacion_unicos,
    COUNT(DISTINCT usuario) as usuarios_unicos
FROM operaciones_log
GROUP BY DATE(fecha_hora)
ORDER BY fecha DESC;

