from flask.wrappers import Response
from flask import jsonify, Blueprint
import logging
from app.services.redis_service import RedisService

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
    """Health check endpoint para Docker y Kubernetes"""
    redis_status = "connected" if RedisService.health_check() else "disconnected"
    
    response = {
        "service": "ms-documentacion",
        "status": "healthy",
        "redis": redis_status
    }
    
    # Si Redis está caído, el servicio sigue funcionando pero sin caché
    status_code = 200
    
    return jsonify(response), status_code
