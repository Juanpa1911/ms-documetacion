# Microservicio de Documentación - SysAcad

## 👥 Autores

- **Juan Pablo Lopez Laszuk**
- **Mariano Piastrellini**
- **Ana Valentina Iriarte Lopez**
- **Carlos Esteban Moya**
- **Ricardo Alberto Sosa**
- **Cristobal Buttini**

---

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.1.2](https://img.shields.io/badge/flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-29%20passing-brightgreen.svg)](./test/)
[![Coverage](https://img.shields.io/badge/coverage-70%25+-success.svg)](./docs/ARCHITECTURE.md#testing)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

Microservicio para la generación de certificados de alumnos regulares en múltiples formatos (PDF, DOCX, ODT). Implementa patrones de resiliencia para alta disponibilidad en arquitecturas de microservicios.

## ✨ Características

- 🚀 **Alta Performance**: Granian WSGI server + Load Balancing (2+ réplicas)
- 🛡️ **Resiliencia**: Circuit Breaker, Retry, Rate Limit (100 req/s)
- ⚡ **Cache Inteligente**: Redis con TTL (5 minutos alumnos, 10 minutos especialidades)
- 📄 **Múltiples Formatos**: PDF, DOCX, ODT
- 🧪 **Testing Completo**: 29 tests unitarios + integración (coverage >70%)
- 📊 **Monitoreable**: Logging estructurado, métricas Traefik
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
curl http://documentos.universidad.localhost/api/v1/health
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

Ver [Guía de Despliegue](./docs/DEPLOYMENT.md) para más detalles.

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [**ARCHITECTURE.md**](./docs/ARCHITECTURE.md) | Arquitectura en capas, componentes, patrones, decisiones técnicas |
| [**API.md**](./docs/API.md) | Endpoints, request/response, ejemplos curl/Python, códigos de error |
| [**DEPLOYMENT.md**](./docs/DEPLOYMENT.md) | Despliegue local, Docker, producción, troubleshooting |
| [**PATRONES_MICROSERVICIOS.md**](./PATRONES_MICROSERVICIOS.md) | Implementación de patrones de resiliencia |

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

Ver [ARCHITECTURE.md](./docs/ARCHITECTURE.md) para más detalles.

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
curl -o certificado.pdf \
  http://documentos.universidad.localhost/api/v1/certificado/123/pdf
```

Ver [API.md](./docs/API.md) para documentación completa con ejemplos Python, códigos de error, etc.

---

## 💻 Desarrollo Local

### Requisitos
- Python 3.12+
- Redis (Docker o local)

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

Ver [DEPLOYMENT.md](./docs/DEPLOYMENT.md) para configuración avanzada, troubleshooting y producción.

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

- **Total tests**: 29
- **test_app.py**: 16 tests (endpoints, configuración, errores)
- **test_integration.py**: 13 tests (Redis, generación PDF/DOCX/ODT, cache)
- **Coverage**: >70% (configurado en `pyproject.toml`)

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

| Patrón | Implementación | Configuración |
|--------|----------------|---------------|
| **Load Balancing** | Traefik Round Robin | 2+ réplicas |
| **Retry** | Decorator + Traefik | 3 intentos (código), 4 intentos (Traefik) |
| **Rate Limit** | Traefik Middleware | 100 req/s, burst 50 |
| **Circuit Breaker** | Traefik | Latencia >100ms, errores >25% |
| **Cache** | Redis Cache-Aside | TTL 300s-600s |

Ver [PATRONES_MICROSERVICIOS.md](./PATRONES_MICROSERVICIOS.md) para detalles de implementación.

---

## 🤝 Contributing

### Reportar Bugs
[Abrir Issue](https://github.com/Juanpa1911/ms-documetacion/issues/new)

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