import logging
import time
from flask import Flask, request, g

logger = logging.getLogger(__name__)


def register_logging_middleware(app: Flask) -> None:
    
    @app.before_request
    def log_request():
        """Logea información de la request entrante y marca el inicio del tiempo"""
        g.start_time = time.time()
        
        logger.info(
            f"Incoming request: {request.method} {request.path} "
            f"from {request.remote_addr}"
        )
    
    @app.after_request
    def log_response(response):
        # Calcular tiempo de procesamiento
        if hasattr(g, 'start_time'):
            duration = int((time.time() - g.start_time) * 1000)  # En milisegundos
        else:
            duration = 0
        
        # Log con nivel según status code
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO
        
        logger.log(
            log_level,
            f"Response: {response.status_code} - {request.method} {request.path} - {duration}ms"
        )
        
        return response
