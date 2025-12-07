import unittest
from flask import current_app
from app import create_app
import os
import json


class AppTestCase(unittest.TestCase):
    """Tests básicos de la aplicación Flask"""

    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        os.environ['USE_MOCK_DATA'] = 'true'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_app_exists(self):
        """Test: La aplicación Flask existe"""
        self.assertIsNotNone(current_app)

    def test_app_is_testing(self):
        """Test: La aplicación está en modo testing"""
        self.assertTrue(current_app.config.get('TESTING', False))


class EndpointsTestCase(unittest.TestCase):
    """Tests de endpoints de la aplicación"""

    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_index_endpoint(self):
        """Test: Endpoint raíz / retorna 200"""
        response = self.client.get('/api/v1/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, 'OK')

    def test_health_endpoint(self):
        """Test: Endpoint /health retorna status ok"""
        response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['service'], 'documentos-service')

    def test_health_endpoint_structure(self):
        """Test: /health tiene la estructura correcta"""
        response = self.client.get('/api/v1/health')
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('service', data)
        self.assertIsInstance(data['status'], str)
        self.assertIsInstance(data['service'], str)

    def test_404_not_found(self):
        """Test: Endpoint inexistente retorna 404 con JSON"""
        response = self.client.get('/api/v1/ruta-inexistente')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'NotFound')
        self.assertEqual(data['status'], 404)

    def test_certificado_endpoint_invalid_id_type(self):
        """Test: ID no numérico retorna 404"""
        response = self.client.get('/api/v1/certificado/abc/pdf')
        self.assertEqual(response.status_code, 404)

    def test_certificado_endpoint_zero_id(self):
        """Test: ID cero retorna error de validación"""
        response = self.client.get('/api/v1/certificado/0/pdf')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)


class BlueprintsTestCase(unittest.TestCase):
    """Tests de registro de blueprints"""

    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_blueprints_registered(self):
        """Test: Blueprints están registrados"""
        # Flask registra blueprints internos también
        blueprint_names = [bp.name for bp in current_app.blueprints.values()]
        self.assertIn('home', blueprint_names)
        self.assertIn('certificado', blueprint_names)

    def test_blueprint_url_prefix(self):
        """Test: Blueprints tienen prefijo /api/v1"""
        rules = [rule.rule for rule in current_app.url_map.iter_rules()]
        # Verificar que las rutas tienen el prefijo correcto
        api_routes = [r for r in rules if r.startswith('/api/v1')]
        self.assertGreater(len(api_routes), 0)


class ConfigurationTestCase(unittest.TestCase):
    """Tests de configuración de la aplicación"""

    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_testing_config(self):
        """Test: Configuración de testing está activa"""
        self.assertTrue(current_app.config['TESTING'])

    def test_required_config_keys(self):
        """Test: Configuración tiene las claves necesarias"""
        required_keys = [
            'REDIS_HOST',
            'REDIS_PORT',
            'REDIS_DB',
            'CACHE_ALUMNO_TTL',
            'CACHE_ESPECIALIDAD_TTL',
            'REQUEST_TIMEOUT'
        ]
        for key in required_keys:
            self.assertIn(key, current_app.config)

    def test_config_values_types(self):
        """Test: Los valores de configuración tienen el tipo correcto"""
        self.assertIsInstance(current_app.config['REDIS_PORT'], int)
        self.assertIsInstance(current_app.config['REDIS_DB'], int)
        self.assertIsInstance(current_app.config['CACHE_ALUMNO_TTL'], int)
        self.assertIsInstance(current_app.config['CACHE_ESPECIALIDAD_TTL'], int)
        self.assertIsInstance(current_app.config['REQUEST_TIMEOUT'], int)


class ErrorHandlingTestCase(unittest.TestCase):
    """Tests de manejo de errores HTTP"""

    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_404_returns_json(self):
        """Test: Error 404 retorna JSON en lugar de HTML"""
        response = self.client.get('/ruta-que-no-existe')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, 'application/json')

    def test_404_has_proper_structure(self):
        """Test: Error 404 tiene estructura correcta"""
        response = self.client.get('/ruta-inexistente')
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('message', data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 404)

    def test_method_not_allowed(self):
        """Test: Método HTTP no permitido retorna 405"""
        # /health solo acepta GET
        response = self.client.post('/api/v1/health')
        self.assertEqual(response.status_code, 405)


if __name__ == '__main__':
    unittest.main()
