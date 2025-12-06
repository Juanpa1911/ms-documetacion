import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter } from 'k6/metrics';

const successCounter = new Counter('successful_requests');
const errorCounter = new Counter('error_requests');

export const options = {
    insecureSkipTLSVerify: true, // Certificado autofirmado
    vus: 1, // Solo 1 usuario virtual
    duration: '30s', // 30 segundos
    thresholds: {
        'http_req_duration': ['p(95)<1000'], // 95% < 1s
        'http_req_failed': ['rate<0.01'], // Menos de 1% de errores
    },
};

export default function () {
    const BASE_URL = 'https://documentos.universidad.localhost';

    // Test 1: Health check
    console.log('🔍 Testing health endpoint...');
    const healthRes = http.get(`${BASE_URL}/api/v1/health`);
    
    const healthCheck = check(healthRes, {
        'health status is 200': (r) => r.status === 200,
        'health returns correct JSON': (r) => {
            try {
                const body = JSON.parse(r.body);
                return body.status === 'ok' && body.service === 'documentos-service';
            } catch {
                return false;
            }
        },
    });

    if (healthCheck) {
        console.log('✅ Health check passed');
        successCounter.add(1);
    } else {
        console.log('❌ Health check failed');
        errorCounter.add(1);
    }

    sleep(2);

    // Test 2: Generar PDF
    console.log('📄 Testing PDF generation...');
    const pdfRes = http.get(`${BASE_URL}/api/v1/certificado/1/pdf`);
    
    const pdfCheck = check(pdfRes, {
        'pdf status is 200': (r) => r.status === 200,
        'pdf content type is correct': (r) => r.headers['Content-Type'] === 'application/pdf',
        'pdf has content': (r) => r.body.length > 1000,
    });

    if (pdfCheck) {
        console.log(`✅ PDF generated (${pdfRes.body.length} bytes)`);
        successCounter.add(1);
    } else {
        console.log(`❌ PDF generation failed (status: ${pdfRes.status})`);
        errorCounter.add(1);
    }

    sleep(2);

    // Test 3: Generar DOCX
    console.log('📝 Testing DOCX generation...');
    const docxRes = http.get(`${BASE_URL}/api/v1/certificado/1/docx`);
    
    const docxCheck = check(docxRes, {
        'docx status is 200': (r) => r.status === 200,
        'docx content type is correct': (r) => r.headers['Content-Type'].includes('wordprocessingml'),
        'docx has content': (r) => r.body.length > 1000,
    });

    if (docxCheck) {
        console.log(`✅ DOCX generated (${docxRes.body.length} bytes)`);
        successCounter.add(1);
    } else {
        console.log(`❌ DOCX generation failed (status: ${docxRes.status})`);
        errorCounter.add(1);
    }

    sleep(2);
}

export function handleSummary(data) {
    const successful = data.metrics.successful_requests?.values.count || 0;
    const errors = data.metrics.error_requests?.values.count || 0;
    const total = data.metrics.http_reqs.values.count;

    console.log('\n🧪 ============ SMOKE TEST SUMMARY ============');
    console.log(`Total Requests:   ${total}`);
    console.log(`Successful:       ${successful} (${((successful/total)*100).toFixed(2)}%)`);
    console.log(`Errors:           ${errors} (${((errors/total)*100).toFixed(2)}%)`);
    console.log(`Avg Duration:     ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms`);
    
    if (successful === total) {
        console.log('\n✅ SMOKE TEST PASSED - Sistema funcionando correctamente');
    } else {
        console.log('\n❌ SMOKE TEST FAILED - Revisar errores');
    }
    console.log('=============================================\n');

    return {
        'performance/results/smoke-test-summary.json': JSON.stringify(data, null, 2),
        'stdout': '',
    };
}
