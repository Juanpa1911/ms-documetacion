# Guía de Despliegue - Microservicio de Documentación

## Tabla de Contenidos
- [Requisitos Previos](#requisitos-previos)
- [Variables de Entorno](#variables-de-entorno)
- [Despliegue Local](#despliegue-local)
- [Despliegue con Docker Compose](#despliegue-con-docker-compose)
- [Despliegue en Producción](#despliegue-en-producción)
- [Configuración de Traefik](#configuración-de-traefik)
- [Troubleshooting](#troubleshooting)

---

## Requisitos Previos

### Software Necesario
- **Docker**: ≥ 20.10
- **Docker Compose**: ≥ 2.0
- **Python**: 3.12+ (solo para desarrollo local)
- **Redis**: 7+ (provisto vía Docker)
- **Traefik**: v3.5 (como reverse proxy)

### Red Docker
El servicio requiere una red Docker externa llamada `carlosred` (o personalizada).

**Crear la red**:
```bash
docker network create carlosred
```

**Verificar**:
```bash
docker network ls | grep carlosred
```

---

## Variables de Entorno

### Variables Requeridas

| Variable | Descripción | Ejemplo | Requerido |
|----------|-------------|---------|-----------|
| `REDIS_HOST` | Host de Redis | `redis` | ✅ |
| `REDIS_PORT` | Puerto de Redis | `6379` | ✅ |
| `REDIS_PASSWORD` | Contraseña de Redis | `secret123` | ❌ (opcional) |
| `ACADEMICA_HOST` | URL del microservicio académica | `http://academica:5001` | ✅ |
| `ALUMNOS_HOST` | URL del microservicio alumnos | `http://alumnos:5002` | ✅ |
| `FLASK_CONTEXT` | Entorno de ejecución | `production` / `development` / `testing` | ✅ |

### Variables Opcionales

| Variable | Descripción | Default | Uso |
|----------|-------------|---------|-----|
| `USE_MOCK_DATA` | Usar datos mock en lugar de servicios reales | `false` | Testing |
| `LOG_LEVEL` | Nivel de logging | `INFO` | Debugging |
| `REDIS_DB` | Base de datos Redis | `0` | Múltiples instancias |

### Archivo `.env` (Desarrollo)

Crear `.env` en la raíz del proyecto:

```bash
# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# Microservicios externos
ACADEMICA_HOST=http://academica.universidad.localhost
ALUMNOS_HOST=http://alumnos.universidad.localhost

# Configuración
FLASK_CONTEXT=development
USE_MOCK_DATA=true
LOG_LEVEL=DEBUG
```

**Nota**: El archivo `.env` no se debe commitear (incluido en `.gitignore`).

---

## Despliegue Local

### 1. Instalación de Dependencias

```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -e .
```

### 2. Ejecutar Redis Local (Docker)

```bash
docker run -d \
  --name redis-local \
  -p 6379:6379 \
  redis:7-alpine
```

### 3. Configurar Variables de Entorno

```bash
export FLASK_CONTEXT=development
export REDIS_HOST=localhost
export REDIS_PORT=6379
export USE_MOCK_DATA=true
export ACADEMICA_HOST=http://localhost:5001
export ALUMNOS_HOST=http://localhost:5002
```

### 4. Ejecutar la Aplicación

**Con Flask (desarrollo)**:
```bash
flask --app app run --debug --port 5000
```

**Con Granian (producción simulada)**:
```bash
granian --interface wsgi \
  --port 5000 \
  --workers 2 \
  --threads 2 \
  --log-level debug \
  wsgi:app
```

### 5. Verificar

```bash
# Health check
curl http://localhost:5000/api/v1/health

# Respuesta esperada:
# {"status":"ok","service":"documentos-service"}
```

---

## Despliegue con Docker Compose

### Arquitectura del Despliegue

```
┌──────────────────────────────────────────────────┐
│                   Traefik                        │
│  (Reverse Proxy + Load Balancer)                │
│  Puerto: 80 (HTTP), 443 (HTTPS)                 │
└──────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│         documentos-service (x2 réplicas)        │
│  - Replica 1: documentos.universidad.localhost  │
│  - Replica 2: documentos.universidad.localhost  │
│  Puerto interno: 5000                           │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│                   Redis                         │
│  Puerto: 6379                                   │
│  Persistencia: volume redis-data                │
└─────────────────────────────────────────────────┘
```

### docker-compose.yml

```yaml
services:
  documentos-service:
    build:
      context: .
      dockerfile: Dockerfile
    image: gestion-documentos:v1.0.1
    deploy:
      replicas: 2  # Load balancing
    networks:
      carlosred:
        aliases:
          - documentos.universidad.localhost
    environment:
      - REDIS_HOST=${REDIS_HOST}
      - REDIS_PORT=${REDIS_PORT}
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - ACADEMICA_HOST=${ACADEMICA_HOST}
      - ALUMNOS_HOST=${ALUMNOS_HOST}
      - FLASK_CONTEXT=${FLASK_CONTEXT:-production}
      - USE_MOCK_DATA=${USE_MOCK_DATA:-false}
    labels:
      # Traefik routing
      - "traefik.enable=true"
      - "traefik.http.routers.documentos-service.rule=Host(`documentos.universidad.localhost`)"
      - "traefik.http.routers.documentos-service.tls=true"
      - "traefik.http.routers.documentos-service.middlewares=documentos-service-ratelimit"
      - "traefik.http.services.documentos-service.loadbalancer.server.port=5000"
      
      # Circuit Breaker
      - "traefik.http.middlewares.documentos-service.circuitbreaker.expression=LatencyAtQuantileMS(50.0) > 100"
      - "traefik.http.middlewares.documentos-service.circuitbreaker.expression=ResponseCodeRatio(500, 600, 0, 600) > 0.25"
      - "traefik.http.middlewares.documentos-service.circuitbreaker.expression=networkErrorRatio() > 0.5"
      
      # Retry
      - "traefik.http.middlewares.documentos-service.retry.attempts=4"
      - "traefik.http.middlewares.documentos-service.retry.initialinterval=100ms"
      
      # Rate Limit
      - "traefik.http.middlewares.documentos-service-ratelimit.ratelimit.average=100"
      - "traefik.http.middlewares.documentos-service-ratelimit.ratelimit.burst=50"
      - "traefik.http.middlewares.documentos-service-ratelimit.ratelimit.period=1s"
      
      - "traefik.docker.network=carlosred"

networks:
  carlosred:
    external: true
```

### Pasos de Despliegue

#### 1. Verificar Red Docker

```bash
docker network inspect carlosred
```

#### 2. Construir Imagen

```bash
docker-compose build
```

**Output esperado**:
```
Building documentos-service
Step 1/10 : FROM python:3.13-slim
...
Successfully built <hash>
Successfully tagged gestion-documentos:v1.0.1
```

#### 3. Iniciar Servicios

```bash
docker-compose up -d
```

**Verificar réplicas**:
```bash
docker-compose ps

# Debería mostrar:
# - documentos-service-1
# - documentos-service-2
```

#### 4. Ver Logs

```bash
# Logs de todas las réplicas
docker-compose logs -f documentos-service

# Logs de una réplica específica
docker logs -f <container_id>
```

#### 5. Verificar Health

```bash
curl http://documentos.universidad.localhost/api/v1/health

# Si usa HTTPS:
curl -k https://documentos.universidad.localhost/api/v1/health
```

#### 6. Escalar (Opcional)

```bash
# Aumentar a 4 réplicas
docker-compose up -d --scale documentos-service=4

# Reducir a 1 réplica
docker-compose up -d --scale documentos-service=1
```

---

## Despliegue en Producción

### Consideraciones de Producción

#### 1. **Seguridad**

**Secrets Management**:
```bash
# NO usar .env en producción
# Usar Docker Secrets o variables de entorno del orquestador

# Ejemplo con Docker Swarm:
echo "my-redis-password" | docker secret create redis_password -

# En docker-compose.yml:
secrets:
  redis_password:
    external: true

environment:
  - REDIS_PASSWORD_FILE=/run/secrets/redis_password
```

**HTTPS Obligatorio**:
```yaml
labels:
  - "traefik.http.routers.documentos-service.tls=true"
  - "traefik.http.routers.documentos-service.tls.certresolver=letsencrypt"
```

#### 2. **Persistencia de Redis**

```yaml
services:
  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

volumes:
  redis-data:
    driver: local
```

#### 3. **Alta Disponibilidad**

**Redis Sentinel** (3 nodos):
```yaml
services:
  redis-master:
    image: redis:7-alpine
  
  redis-replica-1:
    image: redis:7-alpine
    command: redis-server --replicaof redis-master 6379
  
  redis-sentinel-1:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
```

**Múltiples Réplicas**:
```yaml
deploy:
  replicas: 5  # Mínimo 3 en producción
  update_config:
    parallelism: 1
    delay: 10s
  restart_policy:
    condition: on-failure
    max_attempts: 3
```

#### 4. **Monitoreo**

**Prometheus + Grafana**:
```yaml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

**Health Checks**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/api/v1/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

#### 5. **Recursos**

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

---

## Configuración de Traefik

### Traefik docker-compose.yml

```yaml
services:
  traefik:
    image: traefik:v3.5
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--metrics.prometheus=true"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik/acme.json:/acme.json
    networks:
      - carlosred

networks:
  carlosred:
    external: true
```

### Acceder al Dashboard

```bash
# Local
open http://localhost:8080

# En el dashboard verás:
# - Routers: documentos-service
# - Services: documentos-service (2 servers)
# - Middlewares: documentos-service-ratelimit
```

---

## Troubleshooting

### Problema 1: "Network carlosred not found"

**Síntomas**:
```
ERROR: Network carlosred declared as external, but could not be found.
```

**Solución**:
```bash
docker network create carlosred
docker-compose up -d
```

---

### Problema 2: "Address already in use"

**Síntomas**:
```
Error starting userland proxy: listen tcp4 0.0.0.0:5000: bind: address already in use
```

**Solución**:
```bash
# Encontrar proceso usando puerto 5000
lsof -i :5000
# o
netstat -tulpn | grep 5000

# Matar proceso
kill -9 <PID>

# O cambiar puerto en docker-compose.yml
ports:
  - "5001:5000"
```

---

### Problema 3: Redis Connection Failed

**Síntomas**:
```
Redis no disponible: Error 111 connecting to redis:6379. Connection refused.
```

**Solución**:
```bash
# Verificar que Redis esté corriendo
docker ps | grep redis

# Verificar conectividad desde el contenedor
docker exec <container_id> ping redis

# Verificar variables de entorno
docker exec <container_id> env | grep REDIS
```

---

### Problema 4: 503 Service Unavailable

**Síntomas**:
```
curl http://documentos.universidad.localhost/api/v1/health
# 503 Service Unavailable
```

**Posibles causas**:
1. **Circuit Breaker abierto**: Demasiados errores
2. **No hay réplicas saludables**: `docker-compose ps`
3. **Traefik no encuentra servicio**: Revisar labels

**Solución**:
```bash
# Ver logs
docker-compose logs documentos-service

# Reiniciar servicios
docker-compose restart documentos-service

# Ver estado de Traefik
curl http://localhost:8080/api/http/services
```

---

### Problema 5: Rate Limit Excedido (429)

**Síntomas**:
```
HTTP 429 Too Many Requests
```

**Solución temporal**:
```bash
# Aumentar límite en docker-compose.yml
labels:
  - "traefik.http.middlewares.documentos-service-ratelimit.ratelimit.average=200"
  - "traefik.http.middlewares.documentos-service-ratelimit.ratelimit.burst=100"

docker-compose up -d
```

**Solución permanente**: Implementar backoff exponencial en cliente.

---

### Problema 6: "File not found" en templates

**Síntomas**:
```
FileNotFoundError: template/certificado/certificado_pdf.html
```

**Solución**:
```bash
# Verificar que templates están en imagen
docker exec <container_id> ls -la /app/template

# Si faltan, revisar Dockerfile:
COPY template/ /app/template/
```

---

## Comandos Útiles

### Docker Compose

```bash
# Ver servicios corriendo
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar servicio específico
docker-compose restart documentos-service

# Reconstruir sin cache
docker-compose build --no-cache

# Eliminar todo (contenedores, volúmenes, redes)
docker-compose down -v

# Ver recursos consumidos
docker stats
```

### Docker

```bash
# Entrar a contenedor
docker exec -it <container_id> bash

# Ver logs de un contenedor
docker logs -f <container_id>

# Inspeccionar contenedor
docker inspect <container_id>

# Ver red
docker network inspect carlosred

# Limpiar sistema
docker system prune -a --volumes
```

### Testing en Producción

```bash
# Bombardear con requests (test de carga)
ab -n 1000 -c 10 http://documentos.universidad.localhost/api/v1/health

# Verificar rate limit
for i in {1..150}; do 
  curl -s -o /dev/null -w "%{http_code}\n" \
    http://documentos.universidad.localhost/api/v1/health
done | grep 429 | wc -l

# Verificar load balancing (ver IPs de réplicas)
for i in {1..10}; do
  curl -s http://documentos.universidad.localhost/api/v1/health
done
```

---

## Rollback

Si hay problemas después de un deploy:

```bash
# Volver a imagen anterior
docker tag gestion-documentos:v1.0.1 gestion-documentos:rollback
docker-compose pull  # Si usa registry
docker-compose up -d

# O especificar versión específica en docker-compose.yml:
image: gestion-documentos:v1.0.0
```

---

## Checklist Pre-Producción

- [ ] Variables de entorno configuradas (sin `.env`)
- [ ] Redis con persistencia habilitada
- [ ] Mínimo 3 réplicas del servicio
- [ ] HTTPS configurado con certificados válidos
- [ ] Health checks configurados
- [ ] Logs centralizados (ELK, Loki, etc.)
- [ ] Monitoreo activo (Prometheus + Grafana)
- [ ] Alertas configuradas (downtime, errores, latencia)
- [ ] Backups de Redis automatizados
- [ ] Rate limits ajustados a carga esperada
- [ ] Tests de carga ejecutados
- [ ] Documentación actualizada
- [ ] Plan de rollback definido

---

## Referencias
- [Arquitectura](./ARCHITECTURE.md)
- [API Documentation](./API.md)
- [Patrones de Microservicios](../PATRONES_MICROSERVICIOS.md)
- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [Redis Documentation](https://redis.io/docs/)
