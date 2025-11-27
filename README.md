# Microservicio de Documentación

Microservicio para generar certificados académicos en PDF, ODT y DOCX con caché Redis y despliegue en Docker con Traefik.

## Stack Tecnológico

- **Python 3.12+** con Flask
- **Redis** para caché de datos
- **Docker** y Docker Compose
- **Traefik** como reverse proxy
- **uv** como gestor de paquetes

## Arquitectura

Este microservicio consume datos de:

- **ms-alumnos**: Obtiene información de los estudiantes
- **ms-especialidades**: Obtiene información de las carreras

Utiliza **Redis** para cachear las respuestas y reducir la carga en los microservicios dependientes.

## ¿Por qué Redis?

Redis es una base de datos en memoria que sirve como **caché de alta velocidad**:

### Beneficios:

- **Velocidad**: Almacena datos en RAM (mucho más rápido que consultar otros microservicios)
- **Reducción de latencia**: Evita llamadas HTTP repetidas a ms-alumnos y ms-especialidades
- **Escalabilidad**: Disminuye la carga en los microservicios dependientes
- **Resiliencia**: Si Redis falla, el servicio sigue funcionando (sin caché)

### Funcionamiento del Caché:

1. **Primera petición** → Consulta ms-alumnos → Guarda en Redis → Retorna datos
2. **Peticiones siguientes** → Lee desde Redis ⚡ (mucho más rápido)
3. **Después del TTL** → El caché expira → Vuelve a consultar el microservicio

## Requisitos

- Python 3.12+
- uv (gestor de paquetes)
- Docker y Docker Compose (para Redis)

## Instalación de uv

1. Abrir **consola de PowerShell como administrador**
2. Instalar `uv`:

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. Reiniciar la PC

## Instalación del Proyecto

```powershell
# Clonar el repositorio
git clone <url-repo>
cd ms-documetacion

# Instalar dependencias
uv sync
```

## Configuración

El archivo `.env` contiene la configuración:

```env
FLASK_CONTEXT=development

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=tu_password_segura

# Cache TTL (segundos)
CACHE_ALUMNO_TTL=300        # 5 minutos
CACHE_ESPECIALIDAD_TTL=600  # 10 minutos

# Microservicios
ALUMNO_SERVICE_URL=http://localhost:5001/api/v1
ESPECIALIDAD_SERVICE_URL=http://localhost:5002/api/v1

# Logging
LOG_LEVEL=INFO
```

### Configuración de Redis (`./data/redis.conf`)

Crea el archivo con esta configuración:

```conf
# Límite de memoria
maxmemory 100mb
maxmemory-policy volatile-lfu

# Seguridad
requirepass tu_password_segura

# Persistencia
save 900 1
save 300 10
save 60 10000
```

**Políticas de memoria:**

- `volatile-lfu`: Elimina las claves menos frecuentemente usadas (con TTL)
- Ideal para caché donde quieres mantener los datos más populares

## Ejecución

### Opción 1: Desarrollo local (sin Docker)

**Terminal 1 - Iniciar servicios mock:**

```powershell
.venv\Scripts\python.exe test\test_mock_services.py
```

**Terminal 2 - Iniciar microservicio:**

```powershell
.venv\Scripts\python.exe app.py
```

**Nota:** Sin Redis, el servicio funciona normalmente pero sin caché.

### Opción 2: Con Redis local

**Terminal 1 - Iniciar Redis con Docker:**

```powershell
docker run -d -p 6379:6379 --name redis --rm redis:8.2-alpine redis-server --requirepass tu_password_segura --maxmemory 100mb --maxmemory-policy volatile-lfu
```

**Terminal 2 - Iniciar servicios mock:**

```powershell
.venv\Scripts\python.exe test\test_mock_services.py
```

**Terminal 3 - Iniciar microservicio:**

```powershell
.venv\Scripts\python.exe app.py
```

### Opción 3: Producción con Granian

```powershell
granian --port 5000 --host 0.0.0.0 --http auto --workers 4 --blocking-threads 4 --backlog 2048 --interface wsgi wsgi:app
```

El servicio estará disponible en: **http://localhost:5000**

## Endpoints

### Health Check

```
GET /api/v1/health
```

Respuesta:

```json
{
  "service": "ms-documentacion",
  "status": "healthy",
  "redis": "connected"
}
```

### Información del servicio

```
GET /api/v1/
```

### Generar certificado

```
GET /api/v1/certificado/{id}/pdf   # PDF
GET /api/v1/certificado/{id}/odt   # OpenDocument
GET /api/v1/certificado/{id}/docx  # Word
```

## Docker y Traefik

- **docker-compose.yml** con Redis configurado
- **Labels de Traefik** para enrutamiento automático
- **Red compartida `mired`** para comunicación entre servicios

Para levantar todo con Docker Compose:

```powershell
docker-compose up -d
```

## Probar manualmente

```powershell
# Verificar salud del servicio y Redis
Invoke-WebRequest http://localhost:5000/api/v1/health | ConvertFrom-Json

# Generar certificado ODT
Invoke-WebRequest http://localhost:5000/api/v1/certificado/1/odt -OutFile certificado.odt

# Generar certificado DOCX
Invoke-WebRequest http://localhost:5000/api/v1/certificado/1/docx -OutFile certificado.docx
```

## Notas

- **PDF en Windows**: Requiere GTK+ instalado. En Linux funciona sin problemas.
- **ODT y DOCX**: Funcionan en todos los sistemas operativos.
- Los servicios mock incluyen 2 alumnos de ejemplo (IDs: 1 y 2).
- **Redis es opcional** - el servicio funciona sin caché si Redis no está disponible.
- El caché mejora significativamente el rendimiento en producción.

## Documentación

- **uv**: https://docs.astral.sh/uv/
- **Granian**: https://github.com/emmett-framework/granian
- **Redis**: https://redis.io/docs/
- **Traefik**: https://doc.traefik.io/traefik/
- **Flask**: https://flask.palletsprojects.com/
