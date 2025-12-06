import time
from datetime import datetime
from flask import jsonify, Blueprint
from flask.wrappers import Response

home = Blueprint('home', __name__)
start_time = time.time()


@home.route('/', methods=['GET'])
def index() -> Response:
    return jsonify('OK'), 200


@home.route('/health', methods=['GET'])
def health() -> Response:
    """
    Endpoint de healthcheck para monitoreo y Traefik
    """
    return jsonify({
        'status': 'ok',
        'service': 'documentos-service'
    }), 200


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
