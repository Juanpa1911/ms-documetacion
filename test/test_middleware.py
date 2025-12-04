import pytest
from flask import Flask
from app.middleware.logging_middleware import register_logging_middleware
import logging


@pytest.fixture
def app():
    """Fixture que crea una aplicación Flask para testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    register_logging_middleware(app)
    
    @app.route('/test')
    def test_route():
        return {"message": "test"}, 200
    
    @app.route('/test/error')
    def test_error_route():
        return {"error": "Internal Server Error"}, 500
    
    return app


@pytest.fixture
def client(app):
    """Fixture que crea un cliente de prueba"""
    return app.test_client()


class TestLoggingMiddleware:
    """Tests para el middleware de logging"""
    
    def test_middleware_logs_request(self, client, caplog):
        with caplog.at_level(logging.INFO):
            response = client.get('/test')
            
            # Verificar que se logeó la request
            assert any('GET' in record.message for record in caplog.records)
            assert any('/test' in record.message for record in caplog.records)
    
    def test_middleware_logs_response_time(self, client, caplog):
        with caplog.at_level(logging.INFO):
            response = client.get('/test')
            
            # Verificar que se logeó el tiempo
            assert any('ms' in record.message for record in caplog.records)
    
    def test_middleware_logs_status_code(self, client, caplog):
        with caplog.at_level(logging.INFO):
            response = client.get('/test')
            
            # Verificar que se logeó el status 200
            assert any('200' in record.message for record in caplog.records)

class TestMiddlewareIntegration:
    """Tests de integración del middleware"""
    
    def test_middleware_no_alters_response(self, client):
        response = client.get('/test')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'test'
    
    def test_middleware_multiple_requests(self, client, caplog):
        with caplog.at_level(logging.INFO):
            client.get('/test')
            client.get('/test')
            client.get('/test')
            
            # Debería haber logeado las 3 requests
            request_logs = [r for r in caplog.records if 'GET' in r.message]
            assert len(request_logs) >= 3

class TestErrorMiddlewareLogging:
    """Tests para verificar logging en caso de errores"""
    
    def test_error_logging(self, client, caplog):
        with caplog.at_level(logging.ERROR):
            response = client.get('/test/error')
            
            # Verificar que se logeó el error
            error_logs = [r for r in caplog.records if r.levelname == 'ERROR']
            assert len(error_logs) > 0
            assert any('500' in r.message for r in error_logs)
