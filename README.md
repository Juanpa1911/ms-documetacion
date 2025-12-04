# Microservicio de Documentación - SysAcad

Microservicio para la generación de documentos PDF (certificados, fichas de alumnos, etc.) basado en Flask, WeasyPrint y Granian WSGI server.

## 📋 Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Instalación y Configuración](#instalación-y-configuración)
- [Desarrollo Local](#desarrollo-local)
- [Despliegue con Docker Compose](#despliegue-con-docker-compose)
- [Configuración de Red (Importante)](#configuración-de-red-importante)
- [Testing](#testing)
- [Tecnologías](#tecnologías)

---

## 📦 Requisitos Previos

### Para Desarrollo Local
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) - Gestor de paquetes Python

### Para Despliegue con Docker
- Docker 20.10+
- Docker Compose V2+
- Red Docker externa configurada (ver [Configuración de Red](#configuración-de-red-importante))

---

## 🚀 Instalación y Configuración

### 1. Instalar uv (Gestor de Paquetes)

**Windows (PowerShell como Administrador):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Reiniciar la terminal después de la instalación.

**Documentación:** [https://docs.astral.sh/uv/getting-started/first-steps/](https://docs.astral.sh/uv/getting-started/first-steps/)

### 2. Clonar el Repositorio

```bash
git clone https://github.com/Juanpa1911/ms-documetacion.git
cd ms-documetacion
```

### 3. Configurar Variables de Entorno

```bash
cp .env.example .env
```

**Editar `.env` con tus valores:**
```env
# Contexto de Flask
FLASK_CONTEXT=production

# Puerto de la aplicación (dentro del contenedor)
APP_PORT=5000

# Redis (ajustar según tu configuración)
REDIS_HOST=redis-documentacion
REDIS_PORT=6379
REDIS_PASSWORD=tu_password_redis

# Microservicios externos
ALUMNOS_HOST=http://ms-alumnos:5000
ACADEMICA_HOST=http://ms-academica:5000

# Cache TTL (segundos)
CACHE_ALUMNO_TTL=300
CACHE_ESPECIALIDAD_TTL=600

# Logging
LOG_LEVEL=INFO

# Granian WSGI Server
GRANIAN_WORKERS=4
GRANIAN_THREADS=4

# SQLAlchemy (opcional, comentado por defecto)
# SQLALCHEMY_TRACK_MODIFICATIONS=False
# SQLALCHEMY_ECHO=False
```

---

## 💻 Desarrollo Local

### 1. Crear Entorno Virtual

```bash
uv venv
```

### 2. Activar Entorno Virtual

**Windows:**
```powershell
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 3. Instalar Dependencias

```bash
uv sync
```

### 4. Ejecutar la Aplicación

**Con Granian (Recomendado para desarrollo):**
```bash
granian --interface wsgi wsgi:app --host 0.0.0.0 --port 5000 --workers 2 --reload
```

**Con Flask (solo para debug):**
```bash
flask run --host=0.0.0.0 --port=5000
```

### 5. Acceder a la Aplicación

- Healthcheck: `http://localhost:5000/api/v1/health`
- Raíz: `http://localhost:5000/api/v1/`

---

## 🐳 Despliegue con Docker Compose

### Modo Producción (con Traefik y servicios externos)

```bash
docker compose up --build -d
```

**Características:**
- Conecta a Redis y PostgreSQL externos
- Integración con Traefik para reverse proxy
- Load balancing (2 réplicas)
- Circuit Breaker y Retry patterns configurados
- Red externa `carlosred` (ver configuración abajo)

---

## 🌐 Configuración de Red (Importante)

### ⚠️ CAMBIOS OBLIGATORIOS PARA CADA DESARROLLADOR

El proyecto usa una red Docker externa llamada `carlosred` por defecto. **Debes cambiarla al nombre de tu red local.**

### 1. Crear tu Red Docker Externa

```bash
# Reemplazar 'TU_NOMBRE_RED' con el nombre que prefieras
docker network create TU_NOMBRE_RED
```

**Ejemplo:**
```bash
docker network create maria-red
```

### 2. Actualizar `docker-compose.yml`

Abrir `/docker-compose.yml` y cambiar todas las referencias de `carlosred` a `TU_NOMBRE_RED`:

```yaml
services:
  documentos-service:
      # ... otras configuraciones ...
      networks:
        TU_NOMBRE_RED:  # ← CAMBIAR AQUÍ (línea 10)
          aliases:
            - documentos.universidad.localhost
      labels:
        # ... otras labels ...
        - "traefik.docker.network=TU_NOMBRE_RED"  # ← CAMBIAR AQUÍ (línea 31)

networks:
    TU_NOMBRE_RED:  # ← CAMBIAR AQUÍ (línea 32)
      external: true
```

**Ubicaciones exactas a modificar en `docker-compose.yml`:**
- **Línea 10:** `networks:` → `TU_NOMBRE_RED:`
- **Línea 31:** Label `traefik.docker.network=TU_NOMBRE_RED`
- **Línea 32:** Sección `networks:` → `TU_NOMBRE_RED:`

```yaml
networks:
  dev-network:  # Puedes dejar esto como está para desarrollo local
    driver: bridge
```

### 4. Verificar Red Existente

```bash
docker network ls
```

Asegúrate de que tu red aparezca en la lista antes de hacer `docker compose up`.

### 5. Configuración de Traefik (Si usas Traefik externo)

Si tienes Traefik corriendo en un `docker-compose.yml` separado, asegúrate de que esté en la misma red.

**Ejemplo de configuración completa de Traefik (`traefik/docker-compose.yml`):**

```yaml
services:
  reverse-proxy:
    image: traefik:v3.5
    container_name: traefik-documentacion
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    ports:
      - 80:80
      - 443:443
      - 6379:6379    # Puerto para Redis
      - 5432:5432    # Puerto para PostgreSQL
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./config/traefik.yml:/etc/traefik/traefik.yml:ro
      - ./config/config.yml:/etc/traefik/config.yml:ro
      - ./certs:/etc/certs:ro
    networks:
      - TU_NOMBRE_RED  # ← CAMBIAR al nombre de tu red
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.traefik=true"

networks:
  TU_NOMBRE_RED:  # ← CAMBIAR al nombre de tu red
    external: true
```

**Ejemplo de configuración de Redis externo (`redis/docker-compose.yml`):**

```yaml
services:
  redis:
    image: redis:7-bookworm
    container_name: redis-documentacion
    restart: always
    volumes:
      - ./data:/data
      - ./data/redis.conf:/data/redis.conf
    command: redis-server /data/redis.conf --loglevel notice --requirepass ${REDIS_PASSWORD}
    networks:
      - TU_NOMBRE_RED  # ← CAMBIAR al nombre de tu red
    labels:
      - "traefik.enable=true"
      - "traefik.tcp.routers.redis.rule=HostSNI(`*`)"
      - "traefik.tcp.routers.redis.entryPoints=redis"
      - "traefik.tcp.routers.redis.service=redis"
      - "traefik.tcp.services.redis.loadbalancer.server.port=6379"

networks:
    TU_NOMBRE_RED:  # ← CAMBIAR al nombre de tu red
      external: true
```

**Pasos para levantar la infraestructura completa:**

```bash
# 1. Crear la red (solo una vez)
docker network create TU_NOMBRE_RED

# 2. Levantar Traefik
cd traefik
docker compose up -d

# 3. Levantar Redis
cd ../redis
docker compose up -d

# 4. Levantar PostgreSQL (si tienes uno separado)
cd ../postgresql
docker compose up -d

# 5. Levantar el microservicio de documentos
cd ../ms-documetacion
docker compose up --build -d
```

### 6. Configurar `/etc/hosts` (Linux/macOS) o `C:\Windows\System32\drivers\etc\hosts` (Windows)

Agregar la entrada para resolución local:

```
127.0.0.1    documentos.universidad.localhost
```

---

## 🧪 Testing

### Healthcheck

**Opción 1: Directo al contenedor (sin Traefik)**
```bash
docker exec ms-documetacion-documentos-service-1 curl http://localhost:5000/api/v1/health
```

**Opción 2: A través de Traefik (requiere certificado SSL)**
```bash
# Ignorando certificado autofirmado
curl -Lk https://documentos.universidad.localhost/api/v1/health
```

**Respuesta esperada:**
```json
{
  "service": "documentos-service",
  "status": "ok"
}
```

### Generación de Certificado PDF (Ejemplo)

```bash
curl -X POST https://documentos.universidad.localhost/api/v1/certificados \
  -H "Content-Type: application/json" \
  -d '{
    "alumno_id": 123,
    "tipo_certificado": "regular"
  }' \
  --output certificado.pdf -Lk
```

### Ver Logs

```bash
# Todos los logs
docker compose logs -f

# Solo servicio de documentos
docker compose logs -f documentos-service

# Últimas 50 líneas
docker compose logs --tail=50 documentos-service
```

### Verificar Estado de Contenedores

```bash
# Ver contenedores corriendo
docker ps

# Ver solo contenedores de documentos
docker ps | grep documentos

# Ver estado de servicios de compose
docker compose ps
```

---

## 🛠️ Tecnologías

### Core
- **Python 3.13.7** - Lenguaje base
- **Flask 3.1.2** - Framework web
- **Granian** - Servidor WSGI de alto rendimiento (Rust)

### Generación de Documentos
- **WeasyPrint 65.1** - Generación de PDF desde HTML/CSS
- **docxtpl 0.20.0** - Plantillas DOCX
- **python-odt-template 0.5.1** - Plantillas ODT

### Cache y Persistencia
- **Redis 4.5.5** - Cache distribuido
- **SQLAlchemy** (opcional) - ORM

### Infraestructura
- **Docker** - Contenedorización
- **Traefik v3.5** - Reverse proxy y load balancer
- **PostgreSQL 14.17** (externo) - Base de datos

### Patterns Implementados
- **Circuit Breaker** - Prevención de cascadas de fallos
  - Latencia > 100ms en percentil 50
  - Response code ratio > 25% en rango 500-600
  - Network error ratio > 50%
- **Retry Pattern** - 4 intentos con 100ms intervalo inicial
- **Load Balancing** - 2 réplicas del servicio
- **Cache-Aside** - TTL configurable por entidad (300s alumnos, 600s especialidades)

---

## 📝 Comandos Útiles

### Gestión de Dependencias con uv

```bash
# Agregar nueva dependencia
uv add nombre-paquete==version

# Actualizar lockfile
uv lock

# Sincronizar entorno
uv sync

# Ver dependencias instaladas
uv pip list

# Eliminar paquete
uv remove nombre-paquete
```

### Docker - Gestión de Contenedores

```bash
# Construir imagen manualmente
docker build -t gestion-documentos:v1.0.0 .

# Ver contenedores corriendo
docker ps

# Ver logs en tiempo real
docker compose logs -f

# Reiniciar servicios
docker compose restart

# Detener servicios
docker compose down

# Detener y eliminar volúmenes
docker compose down -v

# Limpiar todo (contenedores, volúmenes, imágenes)
docker compose down -v --rmi all

# Reconstruir forzando sin cache
docker compose build --no-cache

# Ver estadísticas de uso de recursos
docker stats
```

### Docker - Limpieza

```bash
# Eliminar imágenes huérfanas
docker image prune

# Eliminar imágenes no usadas
docker image prune -a

# Limpiar todo el sistema Docker (cuidado!)
docker system prune -a --volumes

# Eliminar contenedores detenidos
docker container prune
```

---

## 🐛 Troubleshooting

### Error: "network carlosred not found"
**Causa:** La red Docker externa no existe.

**Solución:**
```bash
# Crear la red (reemplazar con tu nombre)
docker network create TU_NOMBRE_RED

# Actualizar docker-compose.yml con el nombre correcto
```

### Error: "pull access denied for gestion-documentos"
**Causa:** Docker intenta descargar la imagen desde Docker Hub en lugar de construirla localmente.

**Solución:**
Verifica que `docker-compose.yml` tenga la sección `build:`:
```yaml
services:
  documentos-service:
      build:
        context: .
        dockerfile: Dockerfile
      image: gestion-documentos:v1.0.0
```

### Error: "granian: executable file not found"
**Causa:** Granian no está instalado en el entorno virtual del contenedor.

**Solución:**
```bash
# Asegúrate de que pyproject.toml tenga granian
uv add granian>=1.0.0

# Actualizar lockfile
uv lock

# Reconstruir imagen
docker compose up --build -d
```

### Contenedores se apagan solos
**Causa:** Error en el código de inicio (wsgi.py, app/__init__.py).

**Solución:**
```bash
# Ver logs para identificar el error
docker compose logs documentos-service

# Errores comunes:
# - Variables de entorno faltantes en .env
# - Sintaxis incorrecta en wsgi.py
# - Blueprints no registrados correctamente
```

### Error: "AttributeError: 'function' object has no attribute 'push'"
**Causa:** Uso incorrecto de `app.app_context` en `wsgi.py`.

**Solución:**
Verificar que `wsgi.py` use:
```python
with app.app_context():
    pass
```
En lugar de:
```python
app.app_context.push()  # ❌ Incorrecto
```

### Error de memoria durante build (error 137)
**Causa:** Docker se queda sin memoria durante la instalación de dependencias.

**Solución:**
```bash
# Opción 1: Limpiar caché de Docker
docker system prune -a

# Opción 2: Aumentar memoria de Docker Desktop
# Settings → Resources → Memory → 4GB o más

# Opción 3: Build con límite de memoria
docker build --memory=4g --memory-swap=4g -t gestion-documentos:v1.0.0 .
```

### Error: "SSL certificate problem: self-signed certificate"
**Causa:** Traefik usa certificados autofirmados en desarrollo.

**Solución:**
```bash
# Opción 1: Ignorar certificado en curl
curl -Lk https://documentos.universidad.localhost/api/v1/health

# Opción 2: Instalar mkcert (Linux)
sudo apt install mkcert
mkcert -install
mkcert documentos.universidad.localhost

# Opción 3: Probar directamente el contenedor
docker exec ms-documetacion-documentos-service-1 curl http://localhost:5000/api/v1/health
```

### Endpoint devuelve 404
**Causa:** La ruta no incluye el prefijo correcto.

**Solución:**
Todos los endpoints tienen prefijo `/api/v1/`:
```bash
# ❌ Incorrecto
curl http://localhost:5000/health

# ✅ Correcto
curl http://localhost:5000/api/v1/health
```

---

## 🏗️ Estructura del Proyecto

```
ms-documetacion/
├── app/
│   ├── __init__.py              # Factory de Flask app
│   ├── config/
│   │   ├── config.py            # Configuraciones por entorno
│   ├── mapping/
│   │   ├── alumno_mapping.py    # Mapeo de DTOs de alumnos
│   │   ├── especialidad_mapping.py
│   │   └── tipodocumento_mapping.py
│   ├── models/
│   │   ├── alumno.py            # Modelos de datos
│   │   ├── especialidad.py
│   │   └── tipodocumento.py
│   ├── repositories/
│   │   ├── alumno_repository.py # Repositorios con cache Redis
│   │   ├── especialidad_repository.py
│   │   └── redis_client.py
│   ├── resources/
│   │   ├── certificado_resource.py  # Endpoints de certificados
│   │   └── home.py              # Healthcheck y raíz
│   ├── services/
│   │   ├── alumno_service.py    # Lógica de negocio
│   │   ├── certificate_service.py
│   │   └── documentos_office_service.py
│   ├── static/
│   │   └── img/                 # Imágenes para templates
│   ├── template/
│   │   ├── certificado/
│   │   │   └── certificado_pdf.html
│   │   └── ficha_alumno/
│   │       └── ficha_alumno.html
│   └── validators/
├── test/
│   ├── test_app.py
│   └── test_repositories.py
├── .env.example                 # Template de variables de entorno
├── .gitignore
├── docker-compose.yml           # Producción con Traefik
├── docker-compose.dev.yml       # Desarrollo local
├── Dockerfile                   # Multi-stage build optimizado
├── pyproject.toml               # Dependencias Python (uv)
├── uv.lock                      # Lockfile de dependencias
├── wsgi.py                      # Entrypoint para Granian
└── README.md                    # Este archivo
```

---

## 👥 Contribución

### Workflow de Git

1. **Crear branch desde `main`:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/nueva-funcionalidad
   ```

2. **Hacer commits descriptivos:**
   ```bash
   git add .
   git commit -m "feat: agregar generación de ficha de alumno"
   ```

3. **Push y crear Pull Request:**
   ```bash
   git push origin feature/nueva-funcionalidad
   ```

4. **Esperar code review y merge**

### Convenciones de Commits

- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bugs
- `docs:` - Documentación
- `refactor:` - Refactorización sin cambio de funcionalidad
- `test:` - Agregar o modificar tests
- `chore:` - Cambios en build, CI/CD, dependencias

---

## 📄 Licencia

Este proyecto es parte del sistema SysAcad de la Universidad.

---

## 📞 Contacto y Soporte

- **Repositorio:** [https://github.com/Juanpa1911/ms-documetacion](https://github.com/Juanpa1911/ms-documetacion)
- **Issues:** [https://github.com/Juanpa1911/ms-documetacion/issues](https://github.com/Juanpa1911/ms-documetacion/issues)
- **Documentación uv:** [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
- **Documentación Granian:** [https://github.com/emmett-framework/granian](https://github.com/emmett-framework/granian)
- **Documentación WeasyPrint:** [https://doc.courtbouillon.org/weasyprint/](https://doc.courtbouillon.org/weasyprint/)

---

**Última actualización:** Diciembre 2025
