import unittest
from flask import Flask
from app.handlers.error_handlers import register_error_handlers
from app.exceptions import (
    AlumnoNotFoundException,
    ServiceUnavailableException,
    DocumentGenerationException
)


class TestErrorHandlers(unittest.TestCase):
    """Tests para los error handlers registrados"""
    
    def setUp(self):
        """Se ejecuta antes de cada test - crea app y client"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        register_error_handlers(self.app)
        
        # Rutas de prueba que lanzan excepciones
        @self.app.route('/test/alumno/<int:id>')
        def test_alumno_not_found(id):
            raise AlumnoNotFoundException(alumno_id=id)
        
        @self.app.route('/test/service')
        def test_service_unavailable():
            raise ServiceUnavailableException(service_name="alumno-service")
        
        @self.app.route('/test/document')
        def test_document_error():
            raise DocumentGenerationException(document_type="pdf", reason="Template missing")
        
        @self.app.route('/test/generic')
        def test_generic_error():
            raise Exception("Error genérico")
        
        @self.app.route('/test/value-error')
        def test_value_error():
            raise ValueError("Invalid value")
        
        self.client = self.app.test_client()
    
    def test_alumno_not_found_handler(self):
        """Test: Handler para AlumnoNotFoundException retorna 404 JSON"""
        response = self.client.get('/test/alumno/123')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, 'application/json')
        
        data = response.get_json()
        self.assertEqual(data['error'], 'AlumnoNotFound')
        self.assertIn('alumno_id', data)
        self.assertEqual(data['alumno_id'], 123)
    
    def test_service_unavailable_handler(self):
        """Test: Handler para ServiceUnavailableException retorna 503 JSON"""
        response = self.client.get('/test/service')
        
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.content_type, 'application/json')
        
        data = response.get_json()
        self.assertEqual(data['error'], 'ServiceUnavailable')
        self.assertEqual(data['service_name'], 'alumno-service')
    
    def test_document_generation_handler(self):
        """Test: Handler para DocumentGenerationException retorna 500 JSON"""
        response = self.client.get('/test/document')
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content_type, 'application/json')
        
        data = response.get_json()
        self.assertEqual(data['error'], 'DocumentGenerationError')
        self.assertEqual(data['document_type'], 'pdf')
    
    def test_generic_exception_handler(self):
        """Test: Handler genérico para excepciones no controladas"""
        response = self.client.get('/test/generic')
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content_type, 'application/json')
        
        data = response.get_json()
        self.assertIn('error', data)
        self.assertIn('message', data)
    
    def test_value_error_handler(self):
        """Test: Handler para ValueError retorna 400 JSON"""
        response = self.client.get('/test/value-error')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, 'application/json')
        
        data = response.get_json()
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()

