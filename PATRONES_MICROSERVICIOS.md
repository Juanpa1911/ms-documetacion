# Patrones de Microservicios - Documentación

Este documento detalla la implementación de los 5 patrones de resiliencia y escalabilidad aplicados al microservicio de gestión de documentos.

---

## 1. ✅ Balanceo de Carga (Load Balancing)

### Descripción
Distribuye las peticiones entrantes entre múltiples instancias del servicio para mejorar la disponibilidad y el rendimiento.

### Ubicación
**Archivo:** `docker-compose.yml` (línea 8)

```yaml
services:
  documentos-service:
    deploy:
      replicas: 2  # ← Dos instancias del servicio
```

### Cómo funciona
- **Traefik** detecta automáticamente las 2 réplicas del servicio
- Usa algoritmo **Round Robin** por defecto
- Si una instancia falla, el tráfico se redirige a la otra

### Verificación
```bash
docker compose ps
# Muestra: ms-documetacion-documentos-service-1 y -2
```

---

## 2. ✅ Retry (Reintentos)

### Descripción
Reintenta automáticamente operaciones fallidas con backoff exponencial para recuperarse de fallos transitorios.

### Ubicación

#### A. Nivel Aplicación (Python)
**Archivos:**
- `app/utils/retry_decorator.py` - Decorator genérico
- `app/repositories/alumno_repository.py` (línea 25)
- `app/repositories/especialidad_repository.py` (línea 25)

```python
@retry(max_attempts=4, delay=0.5, backoff=2.0, exceptions=(requests.RequestException,))
def _fetch_from_service(self, alumno_id: int) -> dict:
    """Obtiene el alumno desde el microservicio externo con retry automático"""
    url = f"{current_app.config['ALUMNO_SERVICE_URL']}/alumnos/{alumno_id}"
    timeout = current_app.config['REQUEST_TIMEOUT']
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()
```

**Configuración:**
- **4 intentos máximos**
- **Delay inicial:** 0.5 segundos
- **Backoff:** 2.0x (delays: 0.5s → 1.0s → 2.0s)
- **Excepciones capturadas:** `requests.RequestException`

#### B. Nivel Proxy (Traefik)
**Archivo:** `docker-compose.yml` (líneas 31-32)

```yaml
- "traefik.http.middlewares.documentos-service.retry.attempts=4"
- "traefik.http.middlewares.documentos-service.retry.initialinterval=100ms"
```

**Configuración:**
- **4 intentos** a nivel de proxy
- **Intervalo inicial:** 100ms

### Tests
**Archivo:** `test/test_retry.py`
- 7 tests unitarios ✅ (todos pasando)
- Tests de backoff exponencial
- Tests de logging
- Tests de reintentos exitosos/fallidos

### Verificación
```bash
# Ejecutar tests
python -m unittest test.test_retry.TestRetryDecorator -v

# Ver logs de reintentos (cuando hay fallos)
docker compose logs documentos-service | grep "intento"
```

---

## 3. ✅ Rate Limit (Limitación de Tasa)

### Descripción
Limita la cantidad de peticiones por segundo para proteger el servicio de sobrecargas y ataques DoS.

### Ubicación
**Archivo:** `docker-compose.yml` (líneas 25, 33-35)

```yaml
labels:
  # Activar el middleware
  - "traefik.http.routers.documentos-service.middlewares=documentos-service-ratelimit"
  
  # Configuración del rate limit
  - "traefik.http.middlewares.documentos-service-ratelimit.ratelimit.average=100"
  - "traefik.http.middlewares.documentos-service-ratelimit.ratelimit.burst=50"
  - "traefik.http.middlewares.documentos-service-ratelimit.ratelimit.period=1s"
```

### Configuración
- **Average:** 100 requests/segundo promedio
- **Burst:** 50 requests adicionales en picos
- **Period:** Ventana de 1 segundo

### Comportamiento
```
Timeline de 1 segundo:
├─────────────────────────────────────────┤
│ Request 1-100: ✅ Aceptadas             │
│ Request 101-150: ✅ Aceptadas (burst)   │
│ Request 151+: ❌ 429 Too Many Requests  │
└─────────────────────────────────────────┘
```

### Verificación
```bash
# Bombardear con 200 requests
for i in {1..200}; do 
  curl -sk "https://documentos.universidad.localhost/api/v1/health" & 
done
wait

# Resultado: Varias respuestas "429 Too Many Requests"
```

---

## 4. ✅ Circuit Breaker (Cortocircuito)

### Descripción
Abre el circuito (rechaza peticiones) cuando el servicio está degradado para evitar saturarlo y permitir recuperación.

### Ubicación
**Archivo:** `docker-compose.yml` (líneas 28-30)

```yaml
#Patron Circuit Breaker
- "traefik.http.middlewares.documentos-service.circuitbreaker.expression=LatencyAtQuantileMS(50.0) > 100"
- "traefik.http.middlewares.documentos-service.circuitbreaker.expression=ResponseCodeRatio(500, 600, 0, 600) > 0.25"
- "traefik.http.middlewares.documentos-service.circuitbreaker.expression=networkErrorRatio() > 0.5"
```

### Condiciones de Apertura

#### 1. Latencia Alta
- **Métrica:** p50 (mediana) de latencia
- **Umbral:** > 100ms
- **Acción:** Si el 50% de las peticiones tardan más de 100ms → Circuit OPEN

#### 2. Errores 5xx
- **Métrica:** Ratio de errores 500-599
- **Umbral:** > 25%
- **Acción:** Si más del 25% son errores de servidor → Circuit OPEN

#### 3. Errores de Red
- **Métrica:** Ratio de errores de conexión
- **Umbral:** > 50%
- **Acción:** Si más del 50% fallan por red → Circuit OPEN

### Estados del Circuit Breaker

```
┌─────────────┐
│   CLOSED    │ ← Estado normal (tráfico fluye)
│  (Normal)   │
└──────┬──────┘
       │ Condición cumplida
       ▼
┌─────────────┐
│    OPEN     │ ← Rechaza peticiones (503)
│  (Bloqueado)│
└──────┬──────┘
       │ Timeout (60s)
       ▼
┌─────────────┐
│ HALF-OPEN   │ ← Permite peticiones de prueba
│  (Probando) │
└──────┬──────┘
       │
       ├─ OK → CLOSED
       └─ Falla → OPEN
```

### Verificación
El circuit breaker se activa automáticamente cuando:
- El servicio responde lento consistentemente
- Hay muchos errores 500
- Hay problemas de conectividad

---

## 5. ✅ Cache de Objetos

### Descripción
Almacena en memoria (Redis) los resultados de llamadas a microservicios externos para reducir latencia y carga.

### Ubicación
**Archivos:**
- `app/repositories/redis_client.py` - Cliente Redis
- `app/repositories/alumno_repository.py` (líneas 33-55)
- `app/repositories/especialidad_repository.py` (líneas 33-55)

### Implementación

```python
def get_alumno_by_id(self, alumno_id: int) -> Optional[Alumno]:
    """Obtiene un alumno por ID usando cache Redis"""
    cache_key = self._get_cache_key(alumno_id)
    
    # 1. Intentar obtener del cache
    cached_data = self.redis_client.get(cache_key)
    if cached_data:
        return self.alumno_mapping.load(cached_data)
    
    # 2. Si no está en cache, consultar servicio externo
    alumno_data = self._fetch_from_service(alumno_id)
    
    # 3. Guardar en cache con TTL
    ttl = current_app.config['CACHE_ALUMNO_TTL']
    self.redis_client.set(cache_key, alumno_data, ttl)
    
    return self.alumno_mapping.load(alumno_data)
```

### Configuración
**Archivo:** `app/config/config.py`

```python
CACHE_ALUMNO_TTL = 300        # 5 minutos
CACHE_ESPECIALIDAD_TTL = 600  # 10 minutos
```

### Patrón Utilizado
**Cache-Aside (Lazy Loading)**
1. Aplicación verifica cache
2. Si existe → retorna dato (cache hit)
3. Si no existe → busca en BD/servicio, guarda en cache, retorna dato (cache miss)

### Claves de Cache
- **Alumnos:** `alumno:{id}`
- **Especialidades:** `especialidad:{id}`

### Conexión Redis
**Configuración en `docker-compose.yml`:**
```yaml
environment:
  - REDIS_HOST=${REDIS_HOST}
  - REDIS_PORT=${REDIS_PORT}
  - REDIS_PASSWORD=${REDIS_PASSWORD}
```

**Redis externo en red `carlosred`**

### Verificación
```bash
# Conectar a Redis externo
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD

# Ver claves de cache
KEYS alumno:*
KEYS especialidad:*

# Ver TTL de una clave
TTL alumno:13

# Ver valor
GET alumno:13
```

---

## Resumen de Implementación

| Patrón | Nivel | Tecnología | Archivo Principal |
|--------|-------|------------|-------------------|
| **Balanceo de Carga** | Infraestructura | Docker Compose + Traefik | `docker-compose.yml` |
| **Retry** | Aplicación + Proxy | Python Decorator + Traefik | `app/utils/retry_decorator.py` |
| **Rate Limit** | Proxy | Traefik Middleware | `docker-compose.yml` |
| **Circuit Breaker** | Proxy | Traefik Middleware | `docker-compose.yml` |
| **Cache** | Aplicación | Redis + Python | `app/repositories/redis_client.py` |

---

## Arquitectura de Resiliencia Completa

```
Usuario
  │
  ▼
┌─────────────────────────────────────────────────┐
│ TRAEFIK (Reverse Proxy)                         │
│ ├─ Rate Limit: 100 req/s + burst 50             │
│ ├─ Circuit Breaker: latencia/errores/red        │
│ ├─ Retry: 4 intentos, 100ms inicial             │
│ └─ Load Balancer: Round Robin entre 2 réplicas  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ DOCUMENTOS-SERVICE (Flask)                      │
│ ├─ 2 Réplicas (Alta Disponibilidad)             │
│ └─ Puerto 5000                                  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ REPOSITORIOS (Data Access Layer)                │
│ ├─ Retry: 3 intentos con backoff exponencial    │
│ ├─ Cache: Verifica Redis primero                │
│ └─ Llamadas HTTP a microservicios externos      │
└────────────────┬────────────────────────────────┘
                 │
         ┌───────┴───────┐
         ▼               ▼
    ┌────────┐    ┌──────────────┐
    │ REDIS  │    │ MS Alumnos   │
    │ Cache  │    │ MS Academia  │
    └────────┘    └──────────────┘
```

---

## Principios de Diseño Aplicados

### KISS (Keep It Simple, Stupid)
- Retry implementado con decorator simple
- Cache con patrón Cache-Aside estándar
- Configuración declarativa en YAML

### YAGNI (You Aren't Gonna Need It)
- Retry solo en I/O externo (no en toda la app)
- Rate limit a nivel proxy (no en código)
- Cache solo para datos frecuentes (alumnos/especialidades)

### DRY (Don't Repeat Yourself)
- Un decorator `@retry` reutilizable
- Cliente Redis centralizado
- Configuración en variables de entorno

### SOLID
- **SRP:** Cada componente tiene una responsabilidad única
- **OCP:** Extensible vía configuración sin modificar código
- **DIP:** Dependencia de abstracciones (interfaces Redis, HTTP)

### Clean Code
- Nombres descriptivos (`_fetch_from_service`, `get_alumno_by_id`)
- Logging claro en cada operación
- Documentación completa en docstrings

---

## Tests y Validación

### Tests Unitarios
- ✅ `test/test_retry.py` - 7 tests del patrón retry (todos pasando)
- ✅ `test/test_repositories.py` - Tests de repositorios con cache

### Tests de Integración
```bash
# Retry
python -m unittest test.test_retry.TestRetryDecorator -v

# Rate Limit
for i in {1..200}; do curl -sk "https://documentos.universidad.localhost/api/v1/health" & done

# Cache
redis-cli -h $REDIS_HOST KEYS alumno:*

# Load Balancing
docker compose ps  # Ver 2 réplicas corriendo
```