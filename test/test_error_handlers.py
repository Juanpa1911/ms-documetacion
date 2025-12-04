import pytest
from flask import Flask
from app.handlers.error_handlers import register_error_handlers
from app.exceptions import (
    AlumnoNotFoundException,
    ServiceUnavailableException,
    DocumentGenerationException
)


@pytest.fixture
def app():
    """Fixture que crea una aplicación Flask para testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    register_error_handlers(app)
    
    # Rutas de prueba que lanzan excepciones
    @app.route('/test/alumno/<int:id>')
    def test_alumno_not_found(id):
        raise AlumnoNotFoundException(alumno_id=id)
    
    @app.route('/test/service')
    def test_service_unavailable():
        raise ServiceUnavailableException(service_name="alumno-service")
    
    @app.route('/test/document')
    def test_document_error():
        raise DocumentGenerationException(document_type="pdf", reason="Template missing")
    
    @app.route('/test/generic')
    def test_generic_error():
        raise Exception("Error genérico")
    
    @app.route('/test/value-error')
    def test_value_error():
        raise ValueError("Invalid value")
    
    return app


@pytest.fixture
def client(app):
    """Fixture que crea un cliente de prueba"""
    return app.test_client()


class TestErrorHandlers:
    """Tests para los error handlers registrados"""
    
    def test_alumno_not_found_handler(self, client):
        """Test: Handler para AlumnoNotFoundException retorna 404 JSON"""
        response = client.get('/test/alumno/123')
        
        assert response.status_code == 404
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        assert data['error'] == 'AlumnoNotFound'
        assert 'alumno_id' in data
        assert data['alumno_id'] == 123
    
    def test_service_unavailable_handler(self, client):
        """Test: Handler para ServiceUnavailableException retorna 503 JSON"""
        response = client.get('/test/service')
        
        assert response.status_code == 503
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        assert data['error'] == 'ServiceUnavailable'
        assert data['service_name'] == 'alumno-service'
    
    def test_document_generation_handler(self, client):
        """Test: Handler para DocumentGenerationException retorna 500 JSON"""
        response = client.get('/test/document')
        
        assert response.status_code == 500
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        assert data['error'] == 'DocumentGenerationError'
        assert data['document_type'] == 'pdf'
    
    def test_generic_exception_handler(self, client):
        """Test: Handler genérico para excepciones no controladas"""
        response = client.get('/test/generic')
        
        assert response.status_code == 500
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        assert 'error' in data
        assert 'message' in data
    
    def test_value_error_handler(self, client):
        """Test: Handler para ValueError retorna 400 JSON"""
        response = client.get('/test/value-error')
        
        assert response.status_code == 400
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        assert 'error' in data

