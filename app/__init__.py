import logging
import os
from flask import Flask
from app.config import config


def create_app() -> Flask:
    app_context = os.getenv('FLASK_CONTEXT')
    # https://flask.palletsprojects.com/en/stable/api/#flask.Flask
    app = Flask(__name__)
    f = config.factory(app_context if app_context else 'development')
    app.config.from_object(f)
    
    from app.handlers import register_error_handlers
    register_error_handlers(app)

    from app.middleware import register_logging_middleware, register_error_middleware
    register_logging_middleware(app)
    register_error_middleware(app)
    
    from app.resources import home, certificado_bp
    app.register_blueprint(home, url_prefix='/api/v1')
    app.register_blueprint(certificado_bp, url_prefix='/api/v1')

    @app.shell_context_processor
    def ctx():
        return {"app": app}

    return app
