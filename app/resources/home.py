from flask.wrappers import Response
from flask import jsonify, Blueprint

home = Blueprint('home', __name__)


@home.route('/', methods=['GET'])
def index() -> Response:
    return jsonify('OK'), 200


@home.route('/health', methods=['GET'])
def health() -> Response:
    """Endpoint de healthcheck para monitoreo y Traefik"""
    return jsonify({
        'status': 'ok',
        'service': 'documentos-service'
    }), 200
