from flask.wrappers import Response
from flask import jsonify, Blueprint
from app.services.redis_services import redis_service
import logging

logger = logging.getLogger(__name__)

home = Blueprint('home', __name__)


@home.route('/', methods=['GET'])
def index() -> Response:
    """Endpoint raíz del microservicio"""
    return jsonify({
        "service": "ms-documentacion",
        "version": "1.0.0",
        "status": "running",
        "description": "Microservicio de generación de documentos y certificados académicos"
    }), 200


@home.route('/health', methods=['GET'])
def health() -> Response:
    """
    Health check endpoint para Docker y Traefik.
    Verifica que el servicio y sus dependencias estén funcionando.
    """
    health_status = {
        "service": "ms-documentacion",
        "status": "healthy",
        "checks": {}
    }
    
    # Verificar conexión con Redis
    try:
        redis_ok = redis_service.ping()
        health_status["checks"]["redis"] = "ok" if redis_ok else "error"
    except Exception as e:
        logger.error(f"Health check - Redis error: {e}")
        health_status["checks"]["redis"] = "error"
        health_status["status"] = "unhealthy"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return jsonify(health_status), status_code
