# Testing de Performance con k6

## 🎯 Descripción

Scripts de k6 para evaluar el rendimiento del microservicio de documentación bajo diferentes escenarios de carga.

## 🖥️ Entorno de Testing

**Sistema Operativo:**
- Linux (Kubuntu 24.04) con Docker nativo (sin virtualización)

**Hardware:**
- **CPU**: Intel Core i5-12450HX (12 núcleos, 55W TDP)
- **RAM**: 16GB DDR5 @ 4800 MT/s
- **Storage**: NVMe 1TB

**Configuración Docker:**
- 2 réplicas × 4 workers Granian
- Redis 7 + Traefik v3.5

**Nota**: Resultados válidos para producción Linux. En Windows (WSL2/Hyper-V) esperar +20-30% overhead.

## 📋 Scripts Disponibles

### 1. Smoke Test (`smoke-test.js`)
**Objetivo**: Verificar funcionamiento básico con carga mínima

**Configuración**:
- VUs: 1
- Duración: 30 segundos
- Tests: Health check, PDF, DOCX

**Cuándo usarlo**: Antes de cualquier otra prueba, para validar que el sistema funciona.

```bash
k6 run performance/scripts/smoke-test.js
```

---

### 2. Load Test (`load-test.js`)
**Objetivo**: Evaluar comportamiento bajo carga normal esperada

**Configuración**:
- VUs: 10 → 30 → 50 (escalonado)
- Duración: 9 minutos
- Tests: Generación de PDF, DOCX, ODT con IDs aleatorios

**Cuándo usarlo**: Para medir rendimiento bajo condiciones normales de producción.

```bash
k6 run performance/scripts/load-test.js
```

---

### 3. Spike Test (`spike-test.js`)
**Objetivo**: Evaluar respuesta ante picos súbitos de tráfico

**Configuración**:
- VUs: 10 → 100 (spike) → 0
- Duración: 70 segundos
- Valida: Rate limit, Circuit breaker

**Cuándo usarlo**: Para verificar que los patrones de resiliencia funcionan.

```bash
k6 run performance/scripts/spike-test.js
```

---

## 🚀 Ejecución

### Requisitos Previos

1. **Instalar k6**:
```bash
# Ubuntu/Debian
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# macOS
brew install k6

# Windows
choco install k6
```

2. **Levantar el servicio**:
```bash
docker-compose up -d
```

3. **Verificar que funciona**:
```bash
curl https://documentos.universidad.localhost/api/v1/health
```

---

### Ejecutar Tests

```bash
# Orden recomendado:

# 1. Smoke Test (verificar que funciona)
k6 run performance/scripts/smoke-test.js

# 2. Load Test (carga normal)
k6 run performance/scripts/load-test.js

# 3. Spike Test (picos de tráfico)
k6 run performance/scripts/spike-test.js
```

### Opciones Adicionales

```bash
# Con más detalle
k6 run --verbose performance/scripts/load-test.js

# Guardar resultados en CSV
k6 run --out csv=performance/results/load-test.csv performance/scripts/load-test.js

# Con URL personalizada
k6 run -e BASE_URL=http://localhost performance/scripts/smoke-test.js
```

---

## 📊 Interpretación de Resultados

### Métricas Clave

| Métrica | Descripción | Valores Esperados |
|---------|-------------|-------------------|
| `http_req_duration (p95)` | 95% de requests completan en este tiempo | < 2000ms |
| `http_req_duration (p99)` | 99% de requests completan en este tiempo | < 3000ms |
| `http_req_failed` | Porcentaje de requests fallidos | < 5% |
| `successful_requests` | Cantidad de 200 OK | > 90% |
| `rate_limit_429` | Activaciones de rate limit | Esperado en spike test |
| `circuit_breaker_503` | Activaciones de circuit breaker | Esperado en spike test |

### Códigos de Estado Esperados

- **200 OK**: Generación exitosa
- **429 Too Many Requests**: Rate limit activado (>100 req/s)
- **503 Service Unavailable**: Circuit breaker abierto (durante sobrecarga)
- **404 Not Found**: Alumno no existe (esperado con IDs altos)
- **500 Internal Server Error**: Error en generación (investigar)

---

## 🔧 Troubleshooting

### Error: "HTTPS certificate error"

Si usas **Windows 11** o tienes problemas con certificados, descomenta en los scripts:

```javascript
export const options = {
    insecureSkipTLSVerify: true, // ← Descomentar esta línea
    stages: [...]
}
```

### Error: "Connection refused"

Verifica que el servicio esté corriendo:
```bash
docker-compose ps
curl https://documentos.universidad.localhost/api/v1/health
```

### Error: "Rate limit activado inmediatamente"

Es normal en spike test. El rate limit está configurado a 100 req/s con burst de 50.

---

## 📁 Estructura de Resultados

Los resultados se guardan automáticamente en:

```
performance/
└── results/
    ├── smoke-test-summary.json
    ├── load-test-summary.json
    └── spike-test-summary.json
```

---

## 📈 Análisis Recomendado

Después de ejecutar los tests, documenta en `docs/PERFORMANCE_ANALYSIS.md`:

1. **Smoke Test**: ¿Pasa todos los checks? ¿Cuál es la latencia base?
2. **Load Test**: ¿Cuál es el p95/p99? ¿Qué formato es más lento?
3. **Spike Test**: ¿Cuándo se activa rate limit? ¿El circuit breaker responde?

### Preguntas Clave

- ¿A partir de cuántos VUs empieza a degradarse el rendimiento?
- ¿El cache reduce la latencia significativamente?
- ¿El sistema se recupera después de un spike?
- ¿Los patrones de resiliencia funcionan como esperado?

---

## 🎯 Objetivos de Performance

| Escenario | Objetivo |
|-----------|----------|
| Smoke Test | 100% de requests exitosos |
| Load Test (50 VUs) | p95 < 2s, error rate < 5% |
| Spike Test | Rate limit activo, sin crashes |

---

## 🔗 Referencias

- [Documentación k6](https://k6.io/docs/)
- [Métricas de k6](https://k6.io/docs/using-k6/metrics/)
- [Análisis de Performance](../docs/PERFORMANCE_ANALYSIS.md)
