# Microservicio de Documentación - SysAcad

## 👥 Autores

- **Juan Pablo Lopez Laszuk**
- **Mariano Piastrellini**
- **Ana Valentina Iriarte Lopez**
- **Carlos Esteban Moya**
- **Ricardo Alberto Sosa**
- **Cristobal Buttini**

IMPORTANTE: Profe no nos quedo claro como teníamos que recibir y procesar los datos que recibiriamos de los otros microservicios ya que no
tuvimos oportunidad de conectarlo con alguno de unestros compañeros a pesar de los pedimos, trabajamos con los datos hardcodeados con mocks
y funciono todo, de igual manera dejamos las conexiones hacia los otros microservicios del modo que creemos correcto pero no pudimos 
probarlo desde ya muchas gracias y apiadece de nosotros, felices fiestas? 🤨😅

---

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.1.2](https://img.shields.io/badge/flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-75%20passing-brightgreen.svg)](./test/)
[![Coverage](https://img.shields.io/badge/coverage-70%25+-success.svg)](./docs/ARCHITECTURE.md#testing)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

Microservicio para la generación de certificados de alumnos regulares en múltiples formatos (PDF, DOCX, ODT). Implementa patrones de resiliencia para alta disponibilidad en arquitecturas de microservicios.

## ✨ Características

- 🚀 **Alta Performance**: Granian WSGI server + Load Balancing (2+ réplicas) - 100% éxito en load tests
- 🛡️ **Resiliencia**: Circuit Breaker, Retry, Rate Limit (100 req/s)
- ⚡ **Cache Inteligente**: Redis con TTL (5 minutos alumnos, 10 minutos especialidades)
- 📄 **Múltiples Formatos**: PDF, DOCX, ODT
- 🧪 **Testing Completo**: 75 tests unitarios + integración (coverage >70%)
- 📊 **Performance Validada**: k6 tests (7,010 req load, 4,660 req spike)
- 🖥️ **Optimizado**: CPU 0-3% idle, RAM 193-352 MiB, Docker 675 MB
- 🔐 **Seguro**: Validación de entrada, manejo de errores robusto

## 📋 Tabla de Contenidos

- [Quick Start](#-quick-start)
- [Documentación](#-documentación)
- [Arquitectura](#-arquitectura)
- [API Endpoints](#-api-endpoints)
- [Desarrollo Local](#-desarrollo-local)
- [Despliegue](#-despliegue)
- [Testing](#-testing)
- [Tecnologías](#-tecnologías)
- [Contributing](#-contributing)

---

## 🚀 Quick Start

### Opción 1: Docker Compose (Recomendado)

```bash
# 1. Crear red Docker
docker network create carlosred

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 3. Levantar servicios
docker-compose up -d

# 4. Verificar
curl -k https://documentos.universidad.localhost/api/v1/health
# O con HTTP: curl http://documentos.universidad.localhost/api/v1/health
```

### Opción 2: Desarrollo Local

```bash
# 1. Instalar dependencias
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# 2. Configurar variables
export FLASK_CONTEXT=development
export REDIS_HOST=localhost
export USE_MOCK_DATA=true

# 3. Ejecutar
flask --app app run --debug
```

Ver [Guía de Despliegue](./Documentacion/DEPLOYMENT.md) para más detalles.

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [**ARCHITECTURE.md**](./Documentacion/ARCHITECTURE.md) | Arquitectura en capas, componentes, patrones, 12-factor app, TDD |
| [**API.md**](./Documentacion/API.md) | Endpoints, request/response, ejemplos curl/Python, códigos de error |
| [**DEPLOYMENT.md**](./Documentacion/DEPLOYMENT.md) | Despliegue local, Docker, producción, troubleshooting |
| [**PATRONES_MICROSERVICIOS.md**](./Documentacion/PATRONES_MICROSERVICIOS.md) | Patrones de resiliencia (Retry, Cache, Circuit Breaker, DRY/KISS/SOLID) |
| [**pruebas-k6.md**](./performance/pruebas-k6.md) | Resultados de performance testing (smoke, load, spike) |

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────┐
│         Traefik Gateway             │
│  Rate Limit | Circuit Breaker       │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   Documentos Service (x2 réplicas)  │
│   Resources → Services → Repos      │
└─────────────────────────────────────┘
                 ↓
┌──────────────┬──────────────────────┐
│ Redis Cache  │  External Services   │
│ (TTL 5-10m)  │  (ms-alumnos, etc.)  │
└──────────────┴──────────────────────┘
```

**Capas**:

1. **Resources**: Endpoints HTTP, validación de entrada
2. **Services**: Lógica de negocio, orquestación
3. **Repositories**: Acceso a datos, cache-aside pattern
4. **Models**: Entidades de dominio (dataclasses)

Ver [ARCHITECTURE.md](./Documentacion/ARCHITECTURE.md) para más detalles.

---

## 🔌 API Endpoints

### Health Check

```bash
GET /api/v1/health
# Response: {"status": "ok", "service": "documentos-service"}
```

### Generar Certificado PDF

```bash
GET /api/v1/certificado/{id}/pdf
# Response: application/pdf (binary)
```

### Generar Certificado DOCX

```bash
GET /api/v1/certificado/{id}/docx
# Response: application/vnd.openxmlformats-officedocument.wordprocessingml.document
```

### Generar Certificado ODT

```bash
GET /api/v1/certificado/{id}/odt
# Response: application/vnd.oasis.opendocument.text
```

**Ejemplo**:

```bash
# Con HTTPS (requiere -k por certificado autofirmado)
curl -k -o certificado.pdf \
  https://documentos.universidad.localhost/api/v1/certificado/1/pdf

# Con HTTP (sin SSL)
curl -o certificado.pdf \
  http://documentos.universidad.localhost/api/v1/certificado/1/pdf
```

Ver [API.md](./docs/API.md) para documentación completa con ejemplos Python, códigos de error, etc.

---

## 💻 Desarrollo Local

### 📦 Requisitos del Sistema

#### Requisitos Mínimos

- **Python**: 3.12 o superior
- **Docker**: 20.10+ (para contenedores)
- **Docker Compose**: 2.0+ (para orquestación)
- **Redis**: 7.0+ (para cache)
- **RAM**: 2GB mínimo (4GB recomendado)
- **Disco**: 500MB espacio libre

#### Dependencias de Sistema (para desarrollo local sin Docker)

**Linux (Ubuntu/Debian)**:

```bash
sudo apt-get update
sudo apt-get install -y \
  python3.12 python3.12-venv python3-pip \
  libpango-1.0-0 libpangoft2-1.0-0 libcairo2 \
  libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info \
  build-essential
```

**Windows**:

- Python 3.12+ desde [python.org](https://www.python.org/downloads/)
- GTK3 Runtime desde [GTK for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer)
- Visual C++ Build Tools (para WeasyPrint)

#### Dependencias Python (Principales)

Las siguientes dependencias se instalan automáticamente desde `pyproject.toml`:

**Framework y Servidor**:

- `flask==3.1.2` - Framework web minimalista
- `granian>=1.0.0` - Servidor ASGI de alta performance

**Generación de Documentos**:

- `weasyprint==65.1` - Conversión HTML → PDF
- `docxtpl==0.20.0` - Generación de archivos DOCX con templates
- `python-odt-template==0.5.1` - Generación de archivos ODT

**Persistencia y Cache**:

- `redis==4.5.5` - Cliente Redis para cache distribuido

**Utilidades**:

- `marshmallow==4.0.1` - Serialización y validación de datos
- `requests==2.32.5` - Cliente HTTP para llamadas a microservicios
- `python-dotenv==1.1.1` - Gestión de variables de entorno

**Testing y Calidad**:

- `pytest>=8.0.0` - Framework de testing
- `pytest-cov>=4.1.0` - Análisis de cobertura de código
- `pyrefly==0.38.2` - Análisis estático de código

**Versión Python requerida**: `>=3.12`

> **Nota**: Todas las dependencias se instalan automáticamente con `pip install -e .`  
> Ver [`pyproject.toml`](./pyproject.toml) para la lista completa.

### Setup

```bash
# 1. Clonar repositorio
git clone https://github.com/Juanpa1911/ms-documetacion.git
cd ms-documetacion

# 2. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -e .

# 4. Levantar Redis (Docker)
docker run -d --name redis-local -p 6379:6379 redis:7-alpine

# 5. Configurar variables de entorno
export FLASK_CONTEXT=development
export REDIS_HOST=localhost
export REDIS_PORT=6379
export USE_MOCK_DATA=true

# 6. Ejecutar aplicación
flask --app app run --debug --port 5000

# 7. Verificar
curl http://localhost:5000/api/v1/health
```

---

## 🐳 Despliegue

### Docker Compose (Producción)

```bash
# 1. Crear red Docker
docker network create carlosred

# 2. Configurar .env
REDIS_HOST=redis
REDIS_PORT=6379
FLASK_CONTEXT=production
USE_MOCK_DATA=false

# 3. Desplegar
docker-compose up -d

# 4. Verificar réplicas
docker-compose ps
# Debería mostrar 2 réplicas de documentos-service

# 5. Ver logs
docker-compose logs -f documentos-service

# 6. Escalar (opcional)
docker-compose up -d --scale documentos-service=4
```

Ver [DEPLOYMENT.md](./Documentacion/DEPLOYMENT.md) para configuración avanzada, troubleshooting y producción.

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
python -m unittest discover -s test -p "test_*.py"

# Tests específicos
python -m unittest test.test_app
python -m unittest test.test_integration

# Con coverage
pip install coverage
coverage run -m unittest discover -s test
coverage report
coverage html  # Genera reporte en htmlcov/
```

### Estadísticas

- **Total tests**: 75 tests (100% pasando)
- **test_app.py**: 16 tests (endpoints, configuración, errores)
- **test_integration.py**: 13 tests (Redis, generación PDF/DOCX/ODT, cache)
- **test_retry.py**: 10 tests (patrón retry con backoff exponencial)
- **test_error_handlers.py**: 5 tests (manejo de errores HTTP)
- **test_exceptions.py**: 11 tests (excepciones personalizadas)
- **test_middleware.py**: 6 tests (logging y error middleware)
- **test_repositories.py**: 8 tests (repositorios con cache, Redis client)
- **test_validator_alumno.py**: 6 tests (validación de datos de alumno)
- **Coverage**: >70% (configurado en `pyproject.toml`)

### Performance Testing (k6)

```bash
# Smoke test (validación básica)
k6 run performance/scripts/smoke-test.js

# Load test (carga sostenida - 50 VUs, 9 min)
k6 run performance/scripts/load-test.js

# Spike test (picos de tráfico - 100 VUs)
k6 run performance/scripts/spike-test.js
```

**Resultados validados**:
- ✅ Smoke: 100% éxito (15 requests)
- ✅ Load: 100% éxito (7,010 requests, 0% errores)
- ✅ Spike: 83.18% éxito (4,660 requests, 15% rate limited)

Ver [pruebas-k6.md](./performance/pruebas-k6.md) para análisis completo.

### Entorno de Testing

**Hardware**:
- CPU: Intel Core i5-12450HX (12 núcleos, 55W TDP)
- RAM: 16GB DDR5 @ 4800 MT/s
- Storage: NVMe 1TB

**Software**:
- OS: Linux (Kubuntu 24.04) - Docker nativo sin virtualización
- Docker: 2 réplicas × 4 workers Granian

**Nota**: Resultados representan rendimiento real en producción Linux. En Windows (WSL2/Hyper-V) esperar +20-30% overhead por virtualización.


---

## 🛠️ Tecnologías

### Backend

- **Flask 3.1.2**: Framework web
- **Granian**: Servidor ASGI de alta performance
- **Marshmallow 4.0.1**: Serialización y validación
- **Redis 7**: Cache distribuido

### Generación de Documentos

- **WeasyPrint 65.1**: HTML → PDF
- **docxtpl 0.20.0**: DOCX con templates Jinja2
- **python-odt-template 0.5.1**: ODT templates

### Infraestructura

- **Traefik v3.5**: Reverse proxy, load balancer
- **Docker + Docker Compose**: Containerización
- **Redis**: Cache layer

### Testing & Quality

- **unittest**: Framework de testing
- **coverage**: Análisis de cobertura
- **GitHub Actions**: CI/CD

---

## 📊 Patrones de Resiliencia

| Patrón              | Implementación      | Configuración                             |
| ------------------- | ------------------- | ----------------------------------------- |
| **Load Balancing**  | Traefik Round Robin | 2+ réplicas                               |
| **Retry**           | Decorator + Traefik | 3 intentos (código), 4 intentos (Traefik) |
| **Rate Limit**      | Traefik Middleware  | 100 req/s, burst 50                       |
| **Circuit Breaker** | Traefik             | Latencia >100ms, errores >25%             |
| **Cache**           | Redis Cache-Aside   | TTL 300s-600s                             |

Ver [PATRONES_MICROSERVICIOS.md](./Documentacion/PATRONES_MICROSERVICIOS.md) para detalles de implementación.

---

## 🤝 Contributing

### Desarrollo

```bash
# 1. Fork del repositorio
# 2. Crear rama feature
git checkout -b feature/nueva-funcionalidad

# 3. Hacer cambios y commitear
git commit -m "feat: agregar nueva funcionalidad"

# 4. Ejecutar tests
python -m unittest discover

# 5. Push y crear Pull Request
git push origin feature/nueva-funcionalidad
```

### Guidelines

- Seguir arquitectura en capas existente
- Agregar tests para nuevas funcionalidades
- Mantener coverage >70%
- Documentar cambios en docstrings

---

## 📄 Licencia

[MIT License](./LICENSE)

---

## 🔗 Enlaces Útiles

- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [Redis Documentation](https://redis.io/docs/)
- [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint/)

---
