# Arquitectura del Microservicio de Documentación

## Tabla de Contenidos
- [Visión General](#visión-general)
- [Arquitectura de Capas](#arquitectura-de-capas)
- [Componentes Principales](#componentes-principales)
- [Patrones de Resiliencia](#patrones-de-resiliencia)
- [Flujo de Datos](#flujo-de-datos)
- [Decisiones Técnicas](#decisiones-técnicas)

---

## Visión General

El microservicio de documentación es responsable de generar certificados de alumnos regulares en múltiples formatos (PDF, DOCX, ODT). Implementa patrones de resiliencia para garantizar alta disponibilidad y rendimiento en un entorno de microservicios.

### Tecnologías Principales
- **Framework**: Flask 3.1.2
- **Lenguaje**: Python 3.12+
- **Server**: Granian (ASGI)
- **Cache**: Redis 7
- **Reverse Proxy**: Traefik v3.5
- **Testing**: unittest + coverage
- **Serialización**: Marshmallow 4.0.1
- **Generación de Documentos**:
  - PDF: WeasyPrint 65.1
  - DOCX: docxtpl 0.20.0
  - ODT: python-odt-template 0.5.1

---

## Arquitectura de Capas

El microservicio sigue una **arquitectura en capas** (layered architecture) con separación de responsabilidades:

```
┌─────────────────────────────────────────────────────┐
│                  Traefik (Gateway)                  │
│  Load Balancing | Rate Limit | Circuit Breaker     │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              Resources Layer (API)                  │
│  - certificado_resource.py                          │
│  - home.py                                          │
│  (Endpoints HTTP, validación de entrada)            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              Services Layer (Lógica)                │
│  - certificate_service.py                           │
│  - alumno_service.py                                │
│  - documentos_office_service.py                     │
│  (Orquestación, validación de negocio)              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│          Repositories Layer (Datos)                 │
│  - alumno_repository.py                             │
│  - especialidad_repository.py                       │
│  - redis_client.py                                  │
│  (Cache, integración con servicios externos)        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│          External Services + Cache                  │
│  - Redis (Cache Layer)                              │
│  - Microservicio de Alumnos                         │
│  - Microservicio de Académica                       │
└─────────────────────────────────────────────────────┘
```

### Responsabilidades por Capa

#### 1. **Resources Layer** (Capa de Presentación)
- Define endpoints HTTP
- Valida parámetros de entrada (IDs, formatos)
- Maneja serialización/deserialización HTTP
- Retorna respuestas con códigos de estado apropiados

**Archivos**: `app/resources/*.py`

#### 2. **Services Layer** (Capa de Lógica de Negocio)
- Implementa reglas de negocio
- Orquesta llamadas a repositorios
- Valida datos de negocio
- Maneja generación de documentos

**Archivos**: `app/services/*.py`

#### 3. **Repositories Layer** (Capa de Acceso a Datos)
- Abstrae acceso a servicios externos
- Implementa patrón Cache-Aside
- Maneja reintentos y timeouts
- Serializa/deserializa con Marshmallow

**Archivos**: `app/repositories/*.py`

#### 4. **Models Layer** (Capa de Dominio)
- Define entidades de dominio (Alumno, Especialidad, TipoDocumento)
- Usa dataclasses para inmutabilidad

**Archivos**: `app/models/*.py`

#### 5. **Mapping Layer** (Capa de Transformación)
- Transforma JSON a objetos de dominio
- Valida estructura de datos
- Usa Marshmallow Schemas

**Archivos**: `app/mapping/*.py`

---

## Componentes Principales

### 1. Certificate Service
**Responsabilidad**: Orquestar la generación de certificados.

```python
# Flujo de generación
1. Validar ID del alumno
2. Buscar alumno (cache o servicio externo)
3. Validar datos del alumno
4. Generar documento según formato (PDF/DOCX/ODT)
5. Retornar BytesIO del documento
```

**Características**:
- Validación con Marshmallow
- Manejo de errores custom (`DocumentGenerationException`)
- Logging detallado

### 2. Alumno Repository
**Responsabilidad**: Obtener datos de alumnos con cache.

**Patrón Cache-Aside**:
```python
1. Buscar en Redis (cache hit → retornar)
2. Si no existe (cache miss):
   a. Llamar a servicio externo con retry
   b. Guardar en Redis con TTL
   c. Retornar datos
```

**Configuración**:
- TTL: 300 segundos (5 minutos)
- Retry: 3 intentos con backoff exponencial
- Timeout: 5 segundos por request

### 3. Redis Client
**Responsabilidad**: Abstracción de operaciones de cache.

**Características**:
- Conexión con manejo de errores
- Serialización JSON automática
- TTL configurable por clave
- Fallback graceful si Redis no disponible

### 4. Documentos Office Service
**Responsabilidad**: Generar documentos en diferentes formatos.

**Formatos soportados**:
- **PDF**: WeasyPrint (HTML → PDF con CSS)
- **DOCX**: docxtpl (plantillas Jinja2 en .docx)
- **ODT**: python-odt-template (plantillas en .odt)

---

## Patrones de Resiliencia

Ver [PATRONES_MICROSERVICIOS.md](../PATRONES_MICROSERVICIOS.md) para detalles completos.

### Resumen de Patrones Implementados

| Patrón | Ubicación | Configuración |
|--------|-----------|---------------|
| **Load Balancing** | Traefik + Docker | 2 réplicas, Round Robin |
| **Retry** | Traefik + Decorator | 4 intentos (Traefik), 3 intentos (código) |
| **Rate Limit** | Traefik | 100 req/s, burst 50 |
| **Circuit Breaker** | Traefik | Latencia >100ms, errores >25% |
| **Cache** | Redis | TTL 300s-600s |

### Estrategia de Resiliencia

```
Usuario → Traefik → [Rate Limit] → [Load Balancer] 
                        ↓
            [Replica 1 | Replica 2]
                        ↓
            [Circuit Breaker Check]
                        ↓
                Service Logic
                        ↓
            [Cache Check] → Redis
                        ↓
            [Retry Logic] → External Service
```

---

## Flujo de Datos

### Flujo Completo: Generación de Certificado PDF

```
1. Request HTTP
   GET /api/v1/certificado/123/pdf
   
2. Traefik Gateway
   - Rate Limit check (100 req/s)
   - Load Balancing (Round Robin entre 2 réplicas)
   - Circuit Breaker check
   
3. certificado_resource.py
   - Validar ID > 0
   - Logging de request
   
4. certificate_service.py
   - Buscar alumno (↓)
   - Validar alumno con Marshmallow
   - Generar HTML desde template
   
5. alumno_repository.py
   - Buscar en Redis (alumno:123)
   - Si cache miss:
     a. @retry decorator (3 intentos)
     b. HTTP GET a ms-alumnos
     c. Deserializar con AlumnoMapping
     d. Guardar en Redis (TTL 300s)
   
6. documentos_office_service.py
   - Renderizar HTML con Jinja2
   - Convertir a PDF con WeasyPrint
   - Retornar BytesIO
   
7. Response HTTP
   - Content-Type: application/pdf
   - Status: 200 OK
   - Body: PDF bytes
```

---

## Decisiones Técnicas

### ¿Por qué Flask en lugar de FastAPI?

**Razones**:
- Proyecto educativo enfocado en arquitectura
- Ecosistema maduro y conocido
- Simplicidad para blueprints
- Granian proporciona performance ASGI

**Trade-off**: No hay validación automática Pydantic (usamos Marshmallow).

### ¿Por qué Marshmallow?

**Razones**:
- Separación clara entre serialización y validación
- Flexible para transformaciones complejas
- `@post_load` permite crear objetos de dominio
- Integración natural con Flask

### ¿Por qué Redis en lugar de caché in-memory?

**Razones**:
- Compartido entre réplicas del servicio
- TTL automático
- Persistencia opcional
- Preparado para escalado horizontal

**Trade-off**: Latencia adicional de red (mitigado con TTL apropiados).

### ¿Por qué dataclasses en lugar de clases normales?

**Razones**:
- Inmutabilidad con `frozen=True`
- Auto-generación de `__init__`, `__repr__`, `__eq__`
- Type hints integrados
- Menos boilerplate

### ¿Por qué Traefik en lugar de NGINX?

**Razones**:
- Configuración automática con labels Docker
- Circuit Breaker integrado
- Métricas out-of-the-box
- Dashboard web incluido

---

## Escalabilidad

### Horizontal
- **Réplicas**: Configurables en `docker-compose.yml` (`replicas: N`)
- **Load Balancing**: Automático con Traefik
- **Stateless**: Sin estado local, todo en Redis

### Vertical
- **Granian**: Servidor ASGI multi-worker
- **Configuración**: Workers configurables vía ENV

### Limitaciones
- Redis como single point of failure (mitigar con Redis Sentinel/Cluster)
- Templates cargados en memoria (considerar volumen compartido)

---

## Monitoreo y Observabilidad

### Logging
- **Nivel**: INFO en producción, DEBUG en desarrollo
- **Formato**: Timestamp + Level + Module + Message
- **Ubicación**: stdout (capturado por Docker logs)

### Métricas (futuras)
- Prometheus + Grafana
- Métricas de Traefik
- Custom metrics: tiempo de generación, cache hit ratio

### Tracing (futuro)
- OpenTelemetry
- Jaeger/Zipkin para distributed tracing

---

## Seguridad

### Actuales
- Validación de entrada (IDs, formatos)
- Manejo seguro de errores (sin exponer stack traces)
- HTTPS vía Traefik (configurado con TLS)

### Futuras Mejoras
- Autenticación JWT
- Rate limiting por usuario
- Validación de roles (RBAC)
- Sanitización de templates

---

## Testing

### Estrategia
- **Unitarios**: Lógica de servicios aislada
- **Integración**: Flujos con mocks de Redis/HTTP
- **E2E**: Generación completa de documentos

Ver [../test/README.md](../test/README.md) para más detalles sobre testing.

---

## Referencias
- [API Documentation](./API.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Microservices Patterns](../PATRONES_MICROSERVICIOS.md)
