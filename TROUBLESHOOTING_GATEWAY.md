# 🔧 Troubleshooting del API Gateway

## Problema: No se puede acceder desde otro PC usando IP pública

### Paso 1: Verificar que el gateway está corriendo

En la instancia del gateway:

```bash
# Verificar que el proceso está corriendo
ps aux | grep uvicorn

# Verificar que está escuchando en el puerto 9000
sudo netstat -tulpn | grep 9000
# o
sudo ss -tulpn | grep 9000
```

**Deberías ver algo como:**
```
tcp  0  0  0.0.0.0:9000  0.0.0.0:*  LISTEN  PID/uvicorn
```

Si no ves nada, el gateway no está corriendo o no está escuchando en el puerto correcto.

### Paso 2: Verificar que escucha en 0.0.0.0

El comando debe ser:
```bash
uvicorn main:app --host 0.0.0.0 --port 9000
```

**NO usar:**
```bash
uvicorn main:app --host localhost --port 9000  # ❌ Solo escucha localmente
uvicorn main:app --host 127.0.0.1 --port 9000  # ❌ Solo escucha localmente
```

### Paso 3: Verificar desde la misma instancia

En la instancia del gateway:

```bash
# Probar localmente
curl http://localhost:9000/health

# Probar con la IP privada
curl http://172.31.XX.XX:9000/health
```

Si funciona localmente pero no desde fuera, es un problema de Security Group o firewall.

### Paso 4: Verificar Security Group

En AWS Console → EC2 → Instancias → Selecciona tu instancia del gateway:

1. Ve a la pestaña "Security"
2. Click en el Security Group
3. Ve a "Inbound rules"
4. Verifica que hay una regla:
   - **Type:** Custom TCP
   - **Port:** 9000
   - **Source:** Tu IP pública o 0.0.0.0/0

**Si no existe, créala:**
- Click "Edit inbound rules"
- Click "Add rule"
- Type: Custom TCP
- Port: 9000
- Source: Tu IP pública (ej: 186.86.110.100/32) o 0.0.0.0/0
- Click "Save rules"

### Paso 5: Verificar IP pública correcta

En AWS Console → EC2 → Instancias:
- Selecciona tu instancia del gateway
- Copia la **IPv4 Public IP**

Asegúrate de usar esta IP, no la privada.

### Paso 6: Verificar firewall local (si aplica)

Si la instancia tiene un firewall local (ufw, firewalld, etc.):

```bash
# En Ubuntu/Debian
sudo ufw status
sudo ufw allow 9000/tcp

# En Amazon Linux 2
sudo firewall-cmd --list-ports
sudo firewall-cmd --permanent --add-port=9000/tcp
sudo firewall-cmd --reload
```

### Paso 7: Ver logs del gateway

En la instancia del gateway:

```bash
# Si está corriendo con nohup
tail -f gateway.log

# Si está corriendo directamente, ver los logs en la terminal
# Deberías ver algo como:
# INFO:     Uvicorn running on http://0.0.0.0:9000
```

### Paso 8: Probar con diferentes métodos

**Desde tu PC:**

```bash
# Método 1: curl
curl http://IP_PUBLICA:9000/health

# Método 2: telnet (verifica conectividad)
telnet IP_PUBLICA 9000
# Si conecta, presiona Ctrl+] y luego escribe "quit"

# Método 3: Desde navegador
# Abre: http://IP_PUBLICA:9000/health
```

### Paso 9: Verificar que no hay otro proceso usando el puerto

```bash
# En la instancia del gateway
sudo lsof -i :9000
# o
sudo fuser 9000/tcp
```

Si hay otro proceso, deténlo o cambia el puerto del gateway.

### Paso 10: Probar con IP privada desde otra instancia EC2

Si tienes acceso a otra instancia EC2 en la misma VPC:

```bash
# Desde otra instancia EC2
curl http://IP_PRIVADA_GATEWAY:9000/health
```

Si funciona desde otra instancia EC2 pero no desde tu PC, el problema es el Security Group (no permite tu IP pública).

## Comandos de diagnóstico rápidos

```bash
# En la instancia del gateway - Verificar proceso
ps aux | grep uvicorn

# Verificar puerto
sudo netstat -tulpn | grep 9000

# Verificar logs
tail -f gateway.log

# Reiniciar gateway
pkill -f "uvicorn main"
cd ~/apigateway
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 9000 > gateway.log 2>&1 &

# Probar localmente
curl http://localhost:9000/health
```

## Solución rápida: Reiniciar gateway correctamente

```bash
# 1. Detener gateway actual
pkill -f "uvicorn main"

# 2. Ir al directorio
cd ~/apigateway
source venv/bin/activate

# 3. Iniciar con logs visibles primero (para ver errores)
uvicorn main:app --host 0.0.0.0 --port 9000

# Si funciona, presiona Ctrl+C y luego inicia en background:
nohup uvicorn main:app --host 0.0.0.0 --port 9000 > gateway.log 2>&1 &
```

## Errores comunes

### Error: "Connection refused"
- Gateway no está corriendo
- Gateway no está escuchando en 0.0.0.0
- Security Group bloquea el puerto

### Error: "Timeout"
- Security Group no permite tu IP
- Firewall local bloqueando
- Gateway no está respondiendo (revisa logs)

### Error: "Connection timed out"
- Security Group incorrecto
- IP pública incorrecta
- Gateway no está corriendo

## Checklist final

- [ ] Gateway corriendo: `ps aux | grep uvicorn`
- [ ] Escuchando en 0.0.0.0: `sudo netstat -tulpn | grep 9000`
- [ ] Funciona localmente: `curl http://localhost:9000/health`
- [ ] Security Group permite puerto 9000
- [ ] IP pública correcta
- [ ] No hay firewall local bloqueando
- [ ] Logs no muestran errores

¿Qué error específico ves cuando intentas acceder?

