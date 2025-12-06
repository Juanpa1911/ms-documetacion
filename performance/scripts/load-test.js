import http from 'k6/http';
import { Trend, Counter, Rate } from 'k6/metrics';
import { check, sleep } from 'k6';

const statusTrend = new Trend('status_codes');
const successCounter = new Counter('successful_requests');
const errorCounter = new Counter('error_requests');
const pdfDuration = new Trend('pdf_generation_duration');
const docxDuration = new Trend('docx_generation_duration');
const odtDuration = new Trend('odt_generation_duration');
const errorRate = new Rate('error_rate');

export const options = {
    insecureSkipTLSVerify: true, // Certificado autofirmado
    stages: [
        { duration: "1m", target: 10 },   // Ramp-up a 10 usuarios
        { duration: "3m", target: 30 },   // Incrementar a 30 usuarios
        { duration: "2m", target: 50 },   // Pico a 50 usuarios
        { duration: "2m", target: 30 },   // Bajar a 30
        { duration: "1m", target: 0 },    // Ramp-down
    ],
    thresholds: {
        'http_req_duration': ['p(95)<2000', 'p(99)<3000'], // 95% < 2s, 99% < 3s
        'error_rate': ['rate<0.1'], // Menos de 10% de errores
        'successful_requests': ['count>100'], // Al menos 100 requests exitosos
    },
};

export default function () {
    const BASE_URL = 'https://documentos.universidad.localhost';
    
    // Datos de prueba
    const alumnoIds = [1, 2, 3, 5, 8, 13, 21, 34];
    const formatos = ['pdf', 'docx', 'odt'];
    
    const alumnoId = alumnoIds[Math.floor(Math.random() * alumnoIds.length)];
    const formato = formatos[Math.floor(Math.random() * formatos.length)];
    
    const url = `${BASE_URL}/api/v1/certificado/${alumnoId}/${formato}`;
    
    const startTime = new Date();
    const res = http.get(url, {
        tags: { formato: formato },
    });
    const duration = new Date() - startTime;
    
    statusTrend.add(res.status);

    const isSuccess = check(res, {
        'status is 200': (r) => r.status === 200,
        'content type is correct': (r) => {
            const contentType = r.headers['Content-Type'] || '';
            if (formato === 'pdf') return contentType === 'application/pdf';
            if (formato === 'docx') return contentType.includes('wordprocessingml');
            if (formato === 'odt') return contentType.includes('opendocument');
            return false;
        },
        'response has content': (r) => r.body && r.body.length > 1000, // Al menos 1KB
    });

    if (isSuccess) {
        successCounter.add(1);
        
        // Registrar duración por tipo de formato
        if (formato === 'pdf') pdfDuration.add(duration);
        if (formato === 'docx') docxDuration.add(duration);
        if (formato === 'odt') odtDuration.add(duration);
    } else {
        errorCounter.add(1);
        errorRate.add(1);
    }

    // Simular tiempo de espera entre requests (1-3 segundos)
    sleep(Math.random() * 2 + 1);
}

export function handleSummary(data) {
    const metrics = data.metrics;
    
    console.log('\n📊 ============ LOAD TEST SUMMARY ============');
    console.log(`Total Requests:     ${metrics.http_reqs.values.count}`);
    console.log(`Successful (200):   ${metrics.successful_requests?.values.count || 0}`);
    console.log(`Errors:             ${metrics.error_requests?.values.count || 0}`);
    console.log(`Error Rate:         ${(metrics.error_rate?.values.rate * 100 || 0).toFixed(2)}%`);
    console.log('\n--- Latency ---');
    console.log(`p50:  ${(metrics.http_req_duration?.values['p(50)'] || 0).toFixed(2)}ms`);
    console.log(`p95:  ${(metrics.http_req_duration?.values['p(95)'] || 0).toFixed(2)}ms`);
    console.log(`p99:  ${(metrics.http_req_duration?.values['p(99)'] || 0).toFixed(2)}ms`);
    
    if (metrics.pdf_generation_duration) {
        console.log('\n--- Por Formato ---');
        console.log(`PDF avg:  ${metrics.pdf_generation_duration.values.avg.toFixed(2)}ms`);
        console.log(`DOCX avg: ${metrics.docx_generation_duration?.values.avg.toFixed(2) || 'N/A'}ms`);
        console.log(`ODT avg:  ${metrics.odt_generation_duration?.values.avg.toFixed(2) || 'N/A'}ms`);
    }
    
    console.log('============================================\n');

    return {
        'performance/results/load-test-summary.json': JSON.stringify(data, null, 2),
        'stdout': '',
    };
}
