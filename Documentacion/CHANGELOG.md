# Changelog


---

## [1.0.1] - 2025-12-06

### Added
- ✨ Health check profundo para Redis y servicios externos
- 📊 Documentación completa de uso de recursos (`performance/RECURSOS.md`)
- 📝 Análisis detallado de proceso de compilación Docker
- 🧪 Pruebas de rendimiento k6 con análisis completo
- 📄 Generación validada de certificados en formato ODT
- 🔍 Endpoint `/docs` con información del servicio

### Fixed
- 🐛 Corrección de Marshmallow schemas en mappings:
  - Cambio de `documento` → `nrodocumento`
  - Cambio de `tipoDocumento` → `tipo_documento` con campo `sigla`
  - Ajuste de `letra` a un solo carácter
  - Conversión de `facultad` de objeto anidado a string
- 🔧 Configuración de REDIS_HOST para Docker (`redis` en lugar de `localhost`)
- 🔧 Mappings actualizados para dataclasses con `init=False`
- 🐛 Imports de WeasyPrint corregidos en `documentos_office_service.py`
- 🐛 Validación de ID de alumno movida a la capa de recursos

### Changed
- ♻️ Refactorización de servicios y repositorios con inyección de dependencias
- ♻️ Mejoras en `certificate_service.py` para mejor manejo de errores
- ♻️ Mejoras en `certificado_resource.py` con validaciones más robustas
- ♻️ Mejoras en `certificado_validator.py` con mensajes más claros
- ♻️ Refactorización y orden en validaciones (datos alumno, ID, contexto)
- 📝 Actualización de `pyproject.toml` con dependencias correctas
- 🔧 Variable `USE_MOCK_DATA` configurada en `true` por defecto

### Performance
- ⚡ Tests de carga completados exitosamente:
  - Smoke Test: 100% éxito (15 requests)
  - Load Test: 100% éxito (7,010 requests, 50 VUs, 9 min)
  - Spike Test: 83.18% éxito (4,660 requests, 100 VUs)
- 📊 Métricas de recursos documentadas:
  - CPU: 0-3% en operación normal, 2.6% bajo carga
  - Memoria: 193-235 MiB idle, 352 MiB bajo carga
  - Imagen Docker: 675 MB optimizada

### Tests
- ✅ 75 tests unitarios pasando (100%)
- ✅ 10 tests del patrón retry implementados
- ✅ Tests de integración con Redis
- ✅ Tests de generación de documentos (PDF, DOCX, ODT)
- ✅ Coverage >70%

---

## [1.0.0] - 2025-11-XX

### Added - Release Inicial

#### Core Features
- 🚀 Microservicio de generación de certificados de alumnos regulares
- 📄 Soporte multi-formato:
  - PDF (WeasyPrint)
  - DOCX (docxtpl)
  - ODT (python-odt-template)
- 🏗️ Arquitectura en capas:
  - Resources (API endpoints)
  - Services (lógica de negocio)
  - Repositories (acceso a datos)
  - Models (entidades de dominio)
  - Mapping (transformación Marshmallow)

#### Patrones de Resiliencia
- 🔄 **Retry Pattern**: Decorator con backoff exponencial (3 intentos)
- 🚦 **Rate Limiting**: Traefik middleware (100 req/s, burst 50)
- 🔌 **Circuit Breaker**: Traefik (latencia >100ms, errores >25%)
- ⚖️ **Load Balancing**: Traefik Round Robin con 2 réplicas
- ⚡ **Cache**: Redis con patrón Cache-Aside (TTL 300s-600s)

#### Infraestructura
- 🐳 Docker + Docker Compose configurado
- 🔀 Traefik v3.5 como reverse proxy
- 📦 Redis 7 para caché distribuido
- 🔧 Granian WSGI server (4 workers por réplica)
- 🌐 Configuración de red Docker (`carlosred`)

#### API Endpoints
- `GET /api/v1/health` - Health check
- `GET /api/v1/certificado/{id}/pdf` - Generar certificado PDF
- `GET /api/v1/certificado/{id}/docx` - Generar certificado DOCX
- `GET /api/v1/certificado/{id}/odt` - Generar certificado ODT

#### Testing & Quality
- 🧪 Suite de tests con unittest
- 📊 Coverage configurado (>70%)
- 🔍 Tests unitarios y de integración
- 🐛 Manejo de errores personalizado
- 📝 Logging estructurado con middleware

#### Documentación
- 📚 `README.md` completo con guías de inicio rápido
- 🏛️ `docs/ARCHITECTURE.md` - Arquitectura detallada
- 📡 `docs/API.md` - Documentación de endpoints
- 🚀 `docs/DEPLOYMENT.md` - Guía de despliegue
- 🛡️ `PATRONES_MICROSERVICIOS.md` - Patrones implementados

#### Configuración
- ⚙️ Variables de entorno con `.env` y `.env.example`
- 🐍 `pyproject.toml` con dependencias versionadas
- 🔒 `.gitignore` configurado correctamente
- 📋 `Dockerfile` optimizado con capas cacheables
- 🔧 `wsgi.py` para servidor Granian

#### Dependencies
```toml
Python >= 3.12
flask = 3.1.2
granian >= 1.0.0
marshmallow = 4.0.1
weasyprint = 65.1
docxtpl = 0.20.0
python-odt-template = 0.5.1
redis = 4.5.5
requests = 2.32.5
python-dotenv = 1.1.1
pytest >= 8.0.0
pytest-cov >= 4.1.0
```

#### Team
- 👥 Equipo de desarrollo:
  - Juan Pablo Lopez Laszuk
  - Mariano Piastrellini
  - Ana Valentina Iriarte Lopez
  - Carlos Esteban Moya
  - Ricardo Alberto Sosa
  - Cristobal Buttini

---

## [Unreleased]

### Planned Features
- [ ] Integración con microservicio de alumnos real (actualmente usando mocks)
- [ ] Integración con microservicio de gestión académica
- [ ] Autenticación y autorización con JWT
- [ ] Firma digital de certificados PDF
- [ ] API de batch processing para múltiples certificados
- [ ] WebSocket para notificaciones en tiempo real
- [ ] Internacionalización (i18n) - Certificados en inglés
- [ ] Plantillas personalizables por facultad
- [ ] Exportación a HTML responsive
- [ ] Integración con S3/MinIO para almacenamiento de certificados

### Under Consideration
- [ ] GraphQL API además de REST
- [ ] Versionado de certificados
- [ ] Auditoría de generaciones
- [ ] Dashboard de administración
- [ ] SDK para clientes (Python, JavaScript)

---

## Tipos de Cambios

- `Added` - Nuevas funcionalidades
- `Changed` - Cambios en funcionalidades existentes
- `Deprecated` - Funcionalidades que serán removidas
- `Removed` - Funcionalidades removidas
- `Fixed` - Corrección de bugs
- `Security` - Correcciones de seguridad
- `Performance` - Mejoras de rendimiento
- `Tests` - Cambios en tests

---

## Links

- [Repository](https://github.com/Juanpa1911/ms-documetacion)
- [Issues](https://github.com/Juanpa1911/ms-documetacion/issues)
- [Pull Requests](https://github.com/Juanpa1911/ms-documetacion/pulls)
- [Documentation](./docs/)
- [Performance Tests](./performance/)

---

## Versionado

Este proyecto usa [Semantic Versioning](https://semver.org/):
- **MAJOR** version: Cambios incompatibles en la API
- **MINOR** version: Nuevas funcionalidades compatibles
- **PATCH** version: Correcciones de bugs compatibles

Ejemplo: `v1.0.1`
- `1` = Major (API version)
- `0` = Minor (features)
- `1` = Patch (bugfixes)
