**Equipo:** 6 integrantes
**Objetivo:** Hacer funcionar el microservicio de generación de
documentos académicos

aplicado el patron cortocircuito aplicado en el docker compose (hecho), aplicar patron retry en el proyecto o en el docker compose, desicion del grupo.
El rate limit tenemos que implementarlo de alguna manera para ver el maximo de peticiones que podemos poner (establecer limite de forma manual para que salte el error)

> [!WARNIng] PIZARRON
>- Analisis y resultado de k6/vegeta
>- Proyecto funcionando (creacion de imagen -Dockerfile)
>- Los patrones de microservicios 
>	- Balanceo de carga
>	- retry
>	- rate limit (alternativo)
>	- cortocircuito
>	- cache de objetos


---
## 📋 ISSUE #1: Implementar Repositorio y Caché con Redis
**Asignado a:** Integrante 1
**Prioridad:** ALTA (Bloqueante para otros issues)
**Estimación:** 8-10 horas
### Descripción
Implementar la capa de repositorio para gestionar la comunicación con los
microservicios externos (alumnos y especialidades) usando Redis como
sistema de caché.
### Tareas específicas:
- [ ] Crear clase `RedisClient` en `app/repositories/redis_client.py`
- Conexión a Redis usando configuración de `config.py`
- Métodos: `get()`, `set()`, `delete()`, `exists()`
- Manejo de serialización JSON
- [ ] Crear `AlumnoRepository` en `app/repositories/alumno_repository.py`
- Método `get_alumno_by_id(id: int)` con cache Redis
- Implementar TTL usando `CACHE_ALUMNO_TTL`
- Manejo de reintentos usando `MAX_RETRY_ATTEMPTS`
- [ ] Crear `EspecialidadRepository` en
`app/repositories/especialidad_repository.py`
- Método `get_especialidad_by_id(id: int)` con cache
- Implementar TTL usando `CACHE_ESPECIALIDAD_TTL`
- [ ] Actualizar `certificate_service.py` para usar los repositorios
- [ ] Crear tests unitarios para los repositorios
### Archivos a modificar/crear:
- `app/repositories/redis_client.py` (CREAR)
- `app/repositories/alumno_repository.py` (CREAR)
- `app/repositories/especialidad_repository.py` (CREAR)
- `app/services/certificate_service.py` (MODIFICAR)
- `test/test_repositories.py` (CREAR)
### Dependencias:
- Ninguna (puede empezar inmediatamente)
---
## 📋 ISSUE #2: Implementar Manejo de Excepciones y Middleware
**Asignado a:** Integrante 2
**Prioridad:** ALTA
**Estimación:** 6-8 horas
### Descripción
Crear un sistema robusto de manejo de errores y middleware para logging,
validación y manejo de excepciones HTTP.
### Tareas específicas:
- [ ] Crear excepciones personalizadas en `app/exceptions/`
- `AlumnoNotFoundException`
- `EspecialidadNotFoundException`
- `ServiceUnavailableException`
- `CacheException`
- `DocumentGenerationException`
- [ ] Crear `error_handler.py` con decorador `@app.errorhandler`
- [ ] Crear middleware en `app/middleware/`
- `logging_middleware.py`: Log de requests/responses
- `error_middleware.py`: Captura de excepciones globales
- `cors_middleware.py`: Configuración CORS si es necesario
- [ ] Implementar respuestas JSON estandarizadas para errores
- [ ] Crear tests para el manejo de errores
### Archivos a crear/modificar:
- `app/exceptions/custom_exceptions.py` (CREAR)
- `app/exceptions/__init__.py` (MODIFICAR)
- `app/middleware/logging_middleware.py` (CREAR)
- `app/middleware/error_middleware.py` (CREAR)
- `app/__init__.py` (MODIFICAR para registrar middleware)
- `test/test_exceptions.py` (CREAR)
### Dependencias:
- Ninguna (puede trabajar en paralelo)
---
## 📋 ISSUE #3: Implementar Validadores y Mejorar Resources
**Asignado a:** Integrante 3
**Prioridad:** MEDIA
**Estimación:** 6-8 horas
### Descripción
Implementar validación de datos de entrada y mejorar los endpoints REST
con manejo de errores apropiado.
### Tareas específicas:
- [ ] Crear validadores en `app/validators/`
- `certificado_validator.py`: Validar parámetros de certificados
- `formato_validator.py`: Validar formatos (pdf, odt, docx)
- [ ] Mejorar `certificado_resource.py`
- Agregar validación de parámetros
- Implementar manejo de errores con try-except
- Agregar documentación de endpoints (docstrings)
- Implementar respuestas HTTP apropiadas (404, 400, 500)
- [ ] Crear endpoint de salud `/health` en `home.py`
- [ ] Crear endpoint `/api/v1/docs` con información del servicio
- [ ] Crear tests de integración para los endpoints
### Archivos a crear/modificar:
- `app/validators/certificado_validator.py` (CREAR)
- `app/validators/formato_validator.py` (CREAR)
- `app/validators/__init__.py` (MODIFICAR)
- `app/resources/certificado_resource.py` (MODIFICAR)
- `app/resources/home.py` (MODIFICAR)
- `test/test_resources.py` (CREAR)
### Dependencias:
- Issue #2 (para usar excepciones personalizadas)
---
## 📋 ISSUE #4: Completar Servicios de Generación de Documentos
**Asignado a:** Integrante 4
**Prioridad:** ALTA
**Estimación:** 8-10 horas
### Descripción
Completar la implementación del servicio de generación de documentos
Office (DOCX/ODT) y mejorar el servicio de certificados.
### Tareas específicas:
- [ ] Completar `documentos_office_service.py`
- Implementar generación de DOCX usando `docxtpl`
- Implementar generación de ODT usando `python-odt-template`
- Implementar generación de PDF usando `weasyprint`
- [ ] Mejorar `certificate_service.py`
- Refactorizar para separar responsabilidades
- Agregar validaciones de contexto
- Mejorar manejo de errores
- [ ] Crear plantillas faltantes en `app/template/certificado/`
- `certificado_plantilla.odt` (plantilla ODT)
- `certificado_plantilla.docx` (plantilla DOCX)
- Mejorar `certificado_pdf.html`
- [ ] Implementar servicio para ficha de alumno
- [ ] Crear tests para generación de documentos
### Archivos a crear/modificar:
- `app/services/documentos_office_service.py` (MODIFICAR)
- `app/services/certificate_service.py` (MODIFICAR)
- `app/template/certificado/certificado_plantilla.odt` (CREAR)
- `app/template/certificado/certificado_plantilla.docx` (CREAR)
- `app/template/certificado/certificado_pdf.html` (MEJORAR)
- `test/test_services.py` (CREAR)
### Dependencias:
- Issue #1 (para usar repositorios)
---
## 📋 ISSUE #5: Configuración de Entorno y Docker
**Asignado a:** Integrante 5
**Prioridad:** ALTA (Bloqueante para deployment)
**Estimación:** 6-8 horas
### Descripción
Configurar correctamente el entorno de desarrollo, variables de entorno,
Docker y docker-compose para deployment.
### Tareas específicas:
- [ ] Crear archivo `.env.example` con todas las variables necesarias
- [ ] Completar `wsgi.py` con configuración de Granian
- [ ] Mejorar `Dockerfile`
- Agregar instalación de dependencias del sistema para WeasyPrint
- Optimizar layers para reducir tamaño
- Agregar healthcheck
- [ ] Corregir y completar `docker-compose.yml`
- Agregar servicio Redis
- Configurar networks correctamente
- Agregar volúmenes para plantillas
- Agregar healthchecks
- [ ] Crear `docker-compose.dev.yml` para desarrollo local
- [ ] Crear script de inicialización `scripts/init.sh`
- [ ] Documentar proceso de instalación en README.md
### Archivos a crear/modificar:
- `.env.example` (CREAR)
- `wsgi.py` (MODIFICAR)
- `Dockerfile` (MEJORAR)
- `docker-compose.yml` (CORREGIR)
- `docker-compose.dev.yml` (CREAR)
- `scripts/init.sh` (CREAR)
- `README.md` (MEJORAR)
### Dependencias:
- Ninguna (puede trabajar en paralelo)
---
## 📋 ISSUE #6: Testing, CI/CD y Documentación
**Asignado a:** Integrante 6
**Prioridad:** MEDIA
**Estimación:** 8-10 horas
### Descripción
Implementar suite completa de tests, configurar CI/CD y crear
documentación técnica del proyecto.
### Tareas específicas:
- [ ] Ampliar `test/test_app.py` con más casos de prueba
- [ ] Crear tests de integración completos
- Test con Redis mock
- Test de generación de documentos
- Test de endpoints completos
- [ ] Configurar pytest con coverage
- [ ] Crear `.github/workflows/ci.yml` para CI/CD
- Ejecutar tests automáticamente
- Verificar cobertura mínima (80%)
- Build de imagen Docker
- [ ] Crear documentación técnica
- `docs/ARCHITECTURE.md`: Arquitectura del sistema
- `docs/API.md`: Documentación de endpoints
- `docs/DEPLOYMENT.md`: Guía de deployment
- [ ] Crear `CONTRIBUTING.md` con guías para contribuir
- [ ] Agregar badges al README (build status, coverage)
### Archivos a crear/modificar:
- `test/test_app.py` (AMPLIAR)
- `test/test_integration.py` (CREAR)
- `pytest.ini` o `pyproject.toml` (CONFIGURAR)
- `.github/workflows/ci.yml` (CREAR)
- `docs/ARCHITECTURE.md` (CREAR)
- `docs/API.md` (CREAR)
- `docs/DEPLOYMENT.md` (CREAR)
- `CONTRIBUTING.md` (CREAR)
- `README.md` (MEJORAR)
### Dependencias:
- Issues #1-5 (necesita que el código esté implementado)
---
## 🔄 Orden de Ejecución Recomendado
### Sprint 1 (Semana 1):
1. **Issue #1** (Integrante 1) - PRIORIDAD CRÍTICA
2. **Issue #2** (Integrante 2) - En paralelo con #1
3. **Issue #5** (Integrante 5) - En paralelo con #1 y #2
### Sprint 2 (Semana 2):
4. **Issue #3** (Integrante 3) - Depende de #2
5. **Issue #4** (Integrante 4) - Depende de #1
### Sprint 3 (Semana 3):
6. **Issue #6** (Integrante 6) - Integración final y testing
---
## 📝 Checklist General del Proyecto
### Antes de empezar:
- [ ] Todos los integrantes tienen acceso al repositorio
- [ ] Crear branch de desarrollo (`develop`)
- [ ] Configurar reglas de protección en `main`
- [ ] Cada integrante crea su branch: `feature/issue-#`
### Durante el desarrollo:
- [ ] Daily standups (15 min)
- [ ] Code review obligatorio antes de merge
- [ ] Tests passing antes de merge
- [ ] Actualizar documentación con cambios
### Para finalizar:
- [ ] Todos los issues cerrados
- [ ] Tests pasando (coverage > 80%)
- [ ] Docker compose funcionando
- [ ] Documentación completa
- [ ] README actualizado
---
## 🚀 Criterios de Aceptación del Proyecto
El microservicio estará **completo y funcional** cuando:
1. ✅ Se puede levantar con `docker-compose up`
2. ✅ Se conecta correctamente a Redis
3. ✅ Genera certificados en PDF, ODT y DOCX
4. ✅ Implementa cache con Redis correctamente
5. ✅ Maneja errores de forma robusta
6. ✅ Los tests pasan con coverage > 80%
7. ✅ La documentación está completa
8. ✅ El endpoint `/health` responde correctamente
---
## 🔗 Referencias Útiles
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [WeasyPrint Docs](https://doc.courtbouillon.org/weasyprint/)
- [docxtpl Documentation](https://docxtpl.readthedocs.io/)
- [Docker Compose](https://docs.docker.com/compose/)
---
**Última actualización:** 1 de diciembre de 2025