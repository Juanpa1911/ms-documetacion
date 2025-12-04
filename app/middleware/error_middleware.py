import logging
from flask import Flask, jsonify

logger = logging.getLogger(__name__)


def register_error_middleware(app: Flask) -> None:
    
    @app.teardown_appcontext
    def teardown_context(exception=None):
        if exception:
            logger.error(f"Request teardown with exception: {type(exception).__name__}")
