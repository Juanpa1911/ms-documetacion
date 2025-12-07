# API Documentation - Microservicio de Documentación

## Información General

**Base URL**: `http://documentos.universidad.localhost` (desarrollo)  
**Versión**: v1  
**Formato**: JSON (errores), Binary (documentos)

---

## Índice
- [Endpoints](#endpoints)
- [Modelos de Datos](#modelos-de-datos)
- [Códigos de Estado](#códigos-de-estado)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Manejo de Errores](#manejo-de-errores)

---

## Endpoints

### Health Check

Verifica el estado del servicio.

#### `GET /api/v1/health`

**Respuesta exitosa** (200 OK):
```json
{
  "status": "ok",
  "service": "documentos-service"
}
```

**Ejemplo curl**:
```bash
curl http://documentos.universidad.localhost/api/v1/health
```

---

### Certificado en PDF

Genera certificado de alumno regular en formato PDF.

#### `GET /api/v1/certificado/<id>/pdf`

**Parámetros**:
- `id` (path, integer, required): ID del alumno (debe ser > 0)

**Headers de respuesta**:
```
Content-Type: application/pdf
Content-Length: <tamaño en bytes>
```

**Respuesta exitosa** (200 OK):
- Body: Binario (PDF)

**Ejemplo curl**:
```bash
curl -o certificado.pdf \
  http://documentos.universidad.localhost/api/v1/certificado/123/pdf
```

**Ejemplo con wget**:
```bash
wget -O certificado_alumno_123.pdf \
  http://documentos.universidad.localhost/api/v1/certificado/123/pdf
```

---

### Certificado en DOCX

Genera certificado de alumno regular en formato Microsoft Word (DOCX).

#### `GET /api/v1/certificado/<id>/docx`

**Parámetros**:
- `id` (path, integer, required): ID del alumno (debe ser > 0)

**Headers de respuesta**:
```
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Content-Disposition: attachment; filename="certificado_alumno_<id>.docx"
```

**Respuesta exitosa** (200 OK):
- Body: Binario (DOCX)

**Ejemplo curl**:
```bash
curl -o certificado.docx \
  http://documentos.universidad.localhost/api/v1/certificado/123/docx
```

**Ejemplo Python**:
```python
import requests

response = requests.get(
    'http://documentos.universidad.localhost/api/v1/certificado/123/docx'
)

if response.status_code == 200:
    with open('certificado.docx', 'wb') as f:
        f.write(response.content)
```

---

### Certificado en ODT

Genera certificado de alumno regular en formato OpenDocument Text (ODT).

#### `GET /api/v1/certificado/<id>/odt`

**Parámetros**:
- `id` (path, integer, required): ID del alumno (debe ser > 0)

**Headers de respuesta**:
```
Content-Type: application/vnd.oasis.opendocument.text
Content-Disposition: attachment; filename="certificado_alumno_<id>.odt"
```

**Respuesta exitosa** (200 OK):
- Body: Binario (ODT)

**Ejemplo curl**:
```bash
curl -o certificado.odt \
  http://documentos.universidad.localhost/api/v1/certificado/123/odt
```

---

## Modelos de Datos

### Alumno (Interno)

Los endpoints no reciben ni retornan JSON de alumnos, pero internamente usan:

```json
{
  "id": 123,
  "nombre": "Juan",
  "apellido": "Pérez",
  "nrodocumento": "12345678",
  "tipo_documento": {
    "id": 1,
    "nombre": "Documento Nacional de Identidad",
    "sigla": "DNI"
  },
  "especialidad": {
    "id": 1,
    "nombre": "Ingeniería en Sistemas",
    "letra": "K",
    "facultad": "Facultad de Ingeniería - Universidad Nacional de Tucumán"
  }
}
```

---

## Códigos de Estado

### Exitosos

| Código | Significado | Cuándo ocurre |
|--------|-------------|---------------|
| `200 OK` | Solicitud exitosa | Documento generado correctamente |

### Errores del Cliente

| Código | Significado | Cuándo ocurre |
|--------|-------------|---------------|
| `404 Not Found` | Recurso no encontrado | Endpoint inexistente o ID de alumno no encontrado |
| `405 Method Not Allowed` | Método HTTP no permitido | Usar POST en endpoint GET |
| `429 Too Many Requests` | Rate limit excedido | >100 peticiones/segundo |

### Errores del Servidor

| Código | Significado | Cuándo ocurre |
|--------|-------------|---------------|
| `500 Internal Server Error` | Error en el servidor | ID inválido (0 o negativo), error generando documento |
| `503 Service Unavailable` | Servicio no disponible | Circuit breaker abierto, servicio externo caído |

---

## Ejemplos de Uso

### Escenario 1: Generar certificado PDF para un alumno

**Request**:
```bash
curl -v http://documentos.universidad.localhost/api/v1/certificado/456/pdf \
  -o certificado_456.pdf
```

**Response exitosa**:
```
< HTTP/1.1 200 OK
< Content-Type: application/pdf
< Content-Length: 45678
< 
* Binary data (PDF)
```

**Response con error (alumno no encontrado)**:
```json
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": "NotFound",
  "message": "Alumno con ID 456 no encontrado",
  "status": 404
}
```

---

### Escenario 2: Generar múltiples formatos para el mismo alumno

**Bash Script**:
```bash
#!/bin/bash
ALUMNO_ID=123
BASE_URL="http://documentos.universidad.localhost/api/v1/certificado"

# Generar PDF
curl -o "certificado_${ALUMNO_ID}.pdf" "${BASE_URL}/${ALUMNO_ID}/pdf"

# Generar DOCX
curl -o "certificado_${ALUMNO_ID}.docx" "${BASE_URL}/${ALUMNO_ID}/docx"

# Generar ODT
curl -o "certificado_${ALUMNO_ID}.odt" "${BASE_URL}/${ALUMNO_ID}/odt"

echo "Certificados generados para alumno ${ALUMNO_ID}"
```

---

### Escenario 3: Integración con Python

```python
import requests
from pathlib import Path

class DocumentosClient:
    def __init__(self, base_url="http://documentos.universidad.localhost"):
        self.base_url = base_url
    
    def generar_certificado(self, alumno_id: int, formato: str = 'pdf'):
        """
        Genera certificado en el formato especificado.
        
        Args:
            alumno_id: ID del alumno
            formato: 'pdf', 'docx' o 'odt'
        
        Returns:
            bytes: Contenido del documento
        
        Raises:
            requests.HTTPError: Si hay error HTTP
        """
        url = f"{self.base_url}/api/v1/certificado/{alumno_id}/{formato}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    
    def guardar_certificado(self, alumno_id: int, formato: str = 'pdf', 
                           directorio: str = '.'):
        """Genera y guarda certificado en disco."""
        content = self.generar_certificado(alumno_id, formato)
        filename = Path(directorio) / f"certificado_{alumno_id}.{formato}"
        
        with open(filename, 'wb') as f:
            f.write(content)
        
        return filename

# Uso
client = DocumentosClient()

try:
    # Generar PDF
    pdf_path = client.guardar_certificado(123, 'pdf', '/tmp')
    print(f"PDF guardado en: {pdf_path}")
    
    # Generar DOCX
    docx_bytes = client.generar_certificado(123, 'docx')
    print(f"DOCX generado: {len(docx_bytes)} bytes")
    
except requests.HTTPError as e:
    print(f"Error HTTP: {e.response.status_code}")
    print(f"Mensaje: {e.response.json()}")
```

---

### Escenario 4: Generación masiva (batch)

```python
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def generar_certificado_batch(alumno_ids: list, formato='pdf', max_workers=5):
    """
    Genera certificados para múltiples alumnos en paralelo.
    
    Args:
        alumno_ids: Lista de IDs de alumnos
        formato: Formato del documento
        max_workers: Máximo de workers concurrentes
    
    Returns:
        dict: {alumno_id: bytes | Exception}
    """
    base_url = "http://documentos.universidad.localhost/api/v1/certificado"
    resultados = {}
    
    def generar_uno(alumno_id):
        try:
            url = f"{base_url}/{alumno_id}/{formato}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return alumno_id, response.content
        except Exception as e:
            return alumno_id, e
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(generar_uno, aid): aid 
                  for aid in alumno_ids}
        
        for future in as_completed(futures):
            alumno_id, resultado = future.result()
            resultados[alumno_id] = resultado
    
    return resultados

# Uso
alumnos = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
resultados = generar_certificado_batch(alumnos, formato='pdf')

# Procesar resultados
exitosos = sum(1 for r in resultados.values() if isinstance(r, bytes))
errores = sum(1 for r in resultados.values() if isinstance(r, Exception))

print(f"Exitosos: {exitosos}, Errores: {errores}")
```

**Nota**: Respetar el rate limit de 100 req/s (ajustar `max_workers` según necesidad).

---

## Manejo de Errores

### Formato de Error Estándar

Todos los errores retornan JSON con esta estructura:

```json
{
  "error": "TipoDeError",
  "message": "Descripción legible del error",
  "status": 500
}
```

### Errores Comunes

#### 1. ID Inválido (ID ≤ 0)

**Request**:
```bash
curl http://documentos.universidad.localhost/api/v1/certificado/0/pdf
```

**Response** (500):
```json
{
  "error": "DocumentGenerationError",
  "message": "El ID del alumno debe ser un número positivo. Recibido: 0",
  "status": 500
}
```

---

#### 2. Alumno No Encontrado

**Request**:
```bash
curl http://documentos.universidad.localhost/api/v1/certificado/99999/pdf
```

**Response** (404):
```json
{
  "error": "NotFound",
  "message": "Alumno con ID 99999 no encontrado en el sistema",
  "status": 404
}
```

---

#### 3. Rate Limit Excedido

**Request**: >100 peticiones/segundo

**Response** (429):
```json
{
  "error": "TooManyRequests",
  "message": "Rate limit exceeded. Try again later.",
  "status": 429
}
```

**Headers adicionales**:
```
Retry-After: 1
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
```

---

#### 4. Servicio Externo No Disponible

**Response** (503):
```json
{
  "error": "ServiceUnavailable",
  "message": "Circuit breaker abierto. Servicio temporalmente no disponible.",
  "status": 503
}
```

---

#### 5. Error de Validación (Datos Incompletos)

**Response** (500):
```json
{
  "error": "ValidationError",
  "message": "Datos del alumno incompletos: falta especialidad",
  "status": 500
}
```

---

## Consideraciones de Performance

### Cache
- Los datos de alumnos se cachean por **5 minutos**
- Primera petición: ~500ms (incluye llamada a ms-alumnos)
- Peticiones subsecuentes (cache hit): ~50-100ms

### Timeouts
- Request timeout: **30 segundos**
- Generación PDF: ~200-500ms
- Generación DOCX: ~100-200ms
- Generación ODT: ~100-200ms

### Límites
- **Rate Limit**: 100 peticiones/segundo
- **Burst**: 50 peticiones adicionales permitidas
- **Max File Size**: No hay límite (documentos típicamente <500KB)

### Recomendaciones
- Usar cache del lado del cliente si se regenera mismo documento
- Para batch, usar `max_workers` ≤ 10 para respetar rate limit
- Implementar retry con exponential backoff en cliente

---

## Versionado

**Versión actual**: v1  
**Path**: `/api/v1/*`

**Política de versionado**:
- Breaking changes → nueva versión (v2, v3, etc.)
- Backward-compatible changes → misma versión
- Deprecación: mínimo 6 meses de aviso

---

## Soporte

**Issues**: [GitHub Issues](https://github.com/Juanpa1911/ms-documetacion/issues)  
**Documentación adicional**:
- [Architecture](./ARCHITECTURE.md)
- [Deployment](./DEPLOYMENT.md)
- [Patterns](../PATRONES_MICROSERVICIOS.md)
