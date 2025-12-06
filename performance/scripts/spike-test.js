import http from 'k6/http';
import { Trend, Counter } from 'k6/metrics';
import { check } from 'k6';

const statusTrend = new Trend('status_codes');
const successCounter = new Counter('successful_requests');
const errorCounter = new Counter('error_requests');
const rateLimitCounter = new Counter('rate_limit_429');
const circuitBreakerCounter = new Counter('circuit_breaker_503');

export const options = {
    insecureSkipTLSVerify: true, // Certificado autofirmado
    stages: [
        { duration: "30s", target: 10 },   // Baseline: 10 usuarios
        { duration: "10s", target: 100 },  // Spike súbito: 100 usuarios
        { duration: "20s", target: 100 },  // Mantener spike
        { duration: "10s", target: 0 },    // Ramp-down
    ],
    thresholds: {
        'http_req_duration': ['p(95)<3000'], // 95% de requests < 3s
        'successful_requests': ['count>50'],  // Al menos 50 requests exitosos
    },
};

export default function () {
    // URL base del microservicio de documentación
    const BASE_URL = 'https://documentos.universidad.localhost';
    
    // IDs de alumnos mockeados en certificate_service.py
    const alumnoIds = [1, 2, 3, 5, 8, 13, 21, 34];
    const formatos = ['pdf', 'docx', 'odt'];
    
    // Seleccionar alumno y formato aleatorio
    const alumnoId = alumnoIds[Math.floor(Math.random() * alumnoIds.length)];
    const formato = formatos[Math.floor(Math.random() * formatos.length)];
    
    const url = `${BASE_URL}/api/v1/certificado/${alumnoId}/${formato}`;
    
    // Hacer request
    const res = http.get(url);
    
    // Registrar código de estado
    statusTrend.add(res.status);

    // Validar respuesta
    const isSuccess = check(res, {
        'status is 200': (r) => r.status === 200,
        'status is valid (200, 429, or 503)': (r) => [200, 429, 503].includes(r.status),
        'no unexpected errors': (r) => r.status !== 500 && r.status !== 502,
        'response has content': (r) => r.body.length > 0,
    });

    // Contadores por tipo de respuesta
    if (res.status === 200) {
        successCounter.add(1);
    } else if (res.status === 429) {
        rateLimitCounter.add(1);
        errorCounter.add(1);
        console.log(`[RATE LIMIT] 429 en alumno=${alumnoId}, formato=${formato}`);
    } else if (res.status === 503) {
        circuitBreakerCounter.add(1);
        errorCounter.add(1);
        console.log(`[CIRCUIT BREAKER] 503 en alumno=${alumnoId}, formato=${formato}`);
    } else {
        errorCounter.add(1);
        console.log(`[ERROR] Status=${res.status}, alumno=${alumnoId}, formato=${formato}`);
    }
}

export function handleSummary(data) {
    const totalRequests = data.metrics.http_reqs?.values?.count || 0;
    const successfulRequests = data.metrics.successful_requests?.values?.count || 0;
    const errorRequests = data.metrics.error_requests?.values?.count || 0;
    const rateLimitHits = data.metrics.rate_limit_429?.values?.count || 0;
    const circuitBreakerTrips = data.metrics.circuit_breaker_503?.values?.count || 0;

    console.log('\n📊 ============ SPIKE TEST SUMMARY ============');
    console.log(`Total Requests:        ${totalRequests}`);
    console.log(`Successful (200):      ${successfulRequests} (${totalRequests > 0 ? ((successfulRequests/totalRequests)*100).toFixed(2) : 0}%)`);
    console.log(`Rate Limit (429):      ${rateLimitHits} (${totalRequests > 0 ? ((rateLimitHits/totalRequests)*100).toFixed(2) : 0}%)`);
    console.log(`Circuit Breaker (503): ${circuitBreakerTrips} (${totalRequests > 0 ? ((circuitBreakerTrips/totalRequests)*100).toFixed(2) : 0}%)`);
    console.log(`Other Errors:          ${errorRequests - rateLimitHits - circuitBreakerTrips}`);
    console.log('============================================\n');

    return {
        'performance/results/spike-test-summary.json': JSON.stringify(data, null, 2),
        'stdout': '', // Evita duplicar output
    };
}
