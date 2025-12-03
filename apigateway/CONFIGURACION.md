# 🔧 Configuración del API Gateway

## Problema: "Not Found" al llamar a `/reports/pedidos-con-rutas`

El API Gateway necesita conocer la URL del orquestador para poder reenviar las peticiones.

## ✅ Solución: Configurar ORQUESTADOR_URL

### Paso 1: Crear archivo `.env` en el directorio `apigateway`

```bash
cd apigateway
cp env.example .env
nano .env
```

### Paso 2: Configurar la URL del orquestador

**Si el gateway y el orquestador están en la misma VPC (recomendado):**
```env
# Usar IP privada del orquestador
ORQUESTADOR_URL=http://172.31.78.108:8080
```

**Si están en VPCs diferentes o necesitas acceso externo:**
```env
# Usar IP pública del orquestador
ORQUESTADOR_URL=http://34.204.174.35:8080
```

**Ejemplo completo de `.env`:**
```env
# URL del orquestador (IP privada si están en la misma VPC)
ORQUESTADOR_URL=http://172.31.78.108:8080

# Nombres de servicios
GESTOR_PEDIDOS_SERVICE_NAME=gestor-pedidos
MONITOR_SERVICE_NAME=monitor

# URLs de fallback (opcional, pero recomendado)
GESTOR_PEDIDOS_FALLBACK_URL=http://172.31.74.102:5000
MONITOR_FALLBACK_URL=http://172.31.XX.XX:5001
```

### Paso 3: Reiniciar el API Gateway

```bash
# Detener el gateway actual
pkill -f "uvicorn.*apigateway"

# Reiniciar con la nueva configuración
cd apigateway
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 9000 > gateway.log 2>&1 &

# Verificar que inició correctamente
tail -f gateway.log
```

### Paso 4: Verificar que funciona

```bash
# Health check del gateway
curl http://IP_PUBLICA_GATEWAY:9000/health

# Debería mostrar:
# {
#   "gateway_status": "ok",
#   "orquestador": {
#     "status": "healthy",
#     ...
#   }
# }

# Probar el endpoint de reportes
curl "http://IP_PUBLICA_GATEWAY:9000/reports/pedidos-con-rutas?month=2025-11"
```

## 🔍 Cómo encontrar la IP del orquestador

### IP Privada (recomendado si están en la misma VPC):
1. Ve a AWS Console → EC2 → Instancias
2. Selecciona la instancia del orquestador
3. Copia la **IP Privada IPv4** (formato: 172.31.x.x)

### IP Pública:
1. Ve a AWS Console → EC2 → Instancias
2. Selecciona la instancia del orquestador
3. Copia la **IPv4 Public IP** (formato: 34.x.x.x)

## 🐛 Troubleshooting

### Error: "No se pudo conectar al orquestador"

**Causa:** El gateway no puede alcanzar el orquestador.

**Soluciones:**
1. Verifica que el orquestador esté corriendo:
   ```bash
   # En la instancia del orquestador
   curl http://localhost:8080/health
   ```

2. Verifica que el `.env` tenga la IP correcta:
   ```bash
   # En la instancia del gateway
   cat apigateway/.env | grep ORQUESTADOR_URL
   ```

3. Verifica conectividad desde el gateway:
   ```bash
   # En la instancia del gateway
   curl http://IP_ORQUESTADOR:8080/health
   ```

4. Verifica Security Groups:
   - El Security Group del orquestador debe permitir tráfico en el puerto 8080 desde el Security Group del gateway

### Error: "Not Found" (404)

**Causa:** El endpoint no existe en el orquestador o la ruta es incorrecta.

**Soluciones:**
1. Verifica que el orquestador tenga el endpoint:
   ```bash
   # Probar directamente el orquestador
   curl "http://IP_ORQUESTADOR:8080/reports/pedidos-con-rutas?month=2025-11"
   ```

2. Verifica los logs del orquestador:
   ```bash
   # En la instancia del orquestador
   tail -f orquestador.log
   ```

3. Verifica los logs del gateway:
   ```bash
   # En la instancia del gateway
   tail -f apigateway/gateway.log
   ```

## 📋 Checklist de Configuración

- [ ] Archivo `.env` creado en `apigateway/`
- [ ] `ORQUESTADOR_URL` configurado con la IP correcta (privada o pública)
- [ ] Gateway reiniciado después de cambiar `.env`
- [ ] Health check del gateway funciona: `curl http://IP:9000/health`
- [ ] Health check del orquestador funciona desde el gateway
- [ ] Security Groups configurados correctamente
- [ ] Endpoint de reportes funciona: `curl "http://IP:9000/reports/pedidos-con-rutas?month=2025-11"`

