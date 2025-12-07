import time
import os
from datetime import datetime
from flask import jsonify, Blueprint, current_app
from flask.wrappers import Response
import requests
import logging

home = Blueprint('home', __name__)
start_time = time.time()
logger = logging.getLogger(__name__)


def _check_redis() -> dict:
    """Verifica conectividad con Redis"""
    try:
        from app.repositories.redis_client import RedisClient
        redis_client = RedisClient()
        if redis_client.client:
            redis_client.client.ping()
            return {'status': 'healthy', 'message': 'Connected'}
        return {'status': 'unhealthy', 'message': 'Client not initialized'}
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return {'status': 'unhealthy', 'message': str(e)}


def _check_service(url: str, service_name: str) -> dict:
    """Verifica disponibilidad de un microservicio externo"""
    try:
        response = requests.get(
            f"{url.rstrip('/')}/health",
            timeout=3
        )
        if response.status_code == 200:
            return {'status': 'healthy', 'url': url}
        return {'status': 'degraded', 'url': url, 'code': response.status_code}
    except requests.RequestException as e:
        logger.warning(f"{service_name} health check failed: {str(e)}")
        return {'status': 'unhealthy', 'url': url, 'message': str(e)}


@home.route('/', methods=['GET'])
def index() -> Response:
    return jsonify('OK'), 200


@home.route('/health', methods=['GET'])
def health() -> Response:
    """
    Endpoint de healthcheck profundo para monitoreo y orquestadores.
    Verifica Redis y microservicios externos críticos.
    
    Returns:
        200: Todos los servicios saludables
        503: Alguna dependencia crítica no disponible
    """
    use_mock_data = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
    
    # Si usa datos mock, retorna health check simple
    if use_mock_data:
        return jsonify({
            'status': 'ok',
            'service': 'documentos-service',
            'mode': 'mock',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
    
    # Health check profundo para producción
    checks = {
        'status': 'healthy',
        'service': 'documentos-service',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'dependencies': {
            'redis': _check_redis(),
            'alumno_service': _check_service(
                current_app.config['ALUMNO_SERVICE_URL'],
                'Alumno Service'
            ),
            'especialidad_service': _check_service(
                current_app.config['ESPECIALIDAD_SERVICE_URL'],
                'Especialidad Service'
            )
        }
    }
    
    # Verificar si alguna dependencia crítica está caída
    redis_unhealthy = checks['dependencies']['redis']['status'] == 'unhealthy'
    alumno_unhealthy = checks['dependencies']['alumno_service']['status'] == 'unhealthy'
    especialidad_unhealthy = checks['dependencies']['especialidad_service']['status'] == 'unhealthy'
    
    if redis_unhealthy or alumno_unhealthy or especialidad_unhealthy:
        checks['status'] = 'degraded'
        logger.warning(f"Service degraded: {checks['dependencies']}")
        return jsonify(checks), 503
    
    return jsonify(checks), 200


@home.route('/docs', methods=['GET'])
def info_service() -> Response:
    """
    Endpoint de información general del servicio
    """
    data = {
        "status": "UP",
        "service": "certificados-api",
        "version": "1.0.0",
        "uptime_seconds": int(time.time() - start_time),
        "timestamp": datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    }
    return jsonify(data), 200
