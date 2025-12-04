import logging
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from app.exceptions import BaseAppException

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:
    
    @app.errorhandler(BaseAppException)
    def handle_app_exception(error: BaseAppException):
        logger.error(f"{error.error_code}: {error.message}")
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        response = {
            "error": error.name,
            "message": error.description,
            "status": error.code
        }
        logger.warning(f"HTTP {error.code}: {error.description}")
        return jsonify(response), error.code
    
    @app.errorhandler(ValueError)
    def handle_value_error(error: ValueError):
        response = {
            "error": "ValueError",
            "message": str(error),
            "status": 400
        }
        logger.error(f"ValueError: {str(error)}")
        return jsonify(response), 400
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        response = {
            "error": "InternalServerError",
            "message": "Ha ocurrido un error interno del servidor",
            "status": 500
        }
        
        # Log detallado del error (sin exponer al cliente)
        logger.error(f"Unhandled exception: {type(error).__name__}: {str(error)}", 
                    exc_info=True)
        
        return jsonify(response), 500
