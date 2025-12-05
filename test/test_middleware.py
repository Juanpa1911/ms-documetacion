import unittest
import logging
from flask import Flask
from app.middleware.logging_middleware import register_logging_middleware
from unittest.mock import patch


class TestLoggingMiddleware(unittest.TestCase):
    """Tests para el middleware de logging"""
    
    def setUp(self):
        """Se ejecuta antes de cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        register_logging_middleware(self.app)
        
        @self.app.route('/test')
        def test_route():
            return {"message": "test"}, 200
        
        @self.app.route('/test/error')
        def test_error_route():
            return {"error": "Internal Server Error"}, 500
        
        self.client = self.app.test_client()
    
    @patch('app.middleware.logging_middleware.logger')
    def test_middleware_logs_request(self, mock_logger):
        """Test: Middleware logea las requests entrantes"""
        response = self.client.get('/test')
        
        # Verificar que se llamó al logger
        self.assertTrue(mock_logger.info.called)
        
        # Verificar que alguna llamada contiene 'GET' y '/test'
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        has_get = any('GET' in str(call) for call in log_calls)
        has_path = any('/test' in str(call) for call in log_calls)
        
        self.assertTrue(has_get)
        self.assertTrue(has_path)
    
    @patch('app.middleware.logging_middleware.logger')
    def test_middleware_logs_response_time(self, mock_logger):
        """Test: Middleware logea el tiempo de respuesta"""
        response = self.client.get('/test')
        
        # Verificar que se logeó algo con 'ms'
        log_calls = [str(call) for call in mock_logger.log.call_args_list + mock_logger.info.call_args_list]
        has_ms = any('ms' in str(call) for call in log_calls)
        
        self.assertTrue(has_ms)
    
    @patch('app.middleware.logging_middleware.logger')
    def test_middleware_logs_status_code(self, mock_logger):
        """Test: Middleware logea el código de estado"""
        response = self.client.get('/test')
        
        # Verificar que se logeó el status 200
        log_calls = [str(call) for call in mock_logger.log.call_args_list + mock_logger.info.call_args_list]
        has_200 = any('200' in str(call) for call in log_calls)
        
        self.assertTrue(has_200)


class TestMiddlewareIntegration(unittest.TestCase):
    """Tests de integración del middleware"""
    
    def setUp(self):
        """Se ejecuta antes de cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        register_logging_middleware(self.app)
        
        @self.app.route('/test')
        def test_route():
            return {"message": "test"}, 200
        
        @self.app.route('/test/error')
        def test_error_route():
            return {"error": "Internal Server Error"}, 500
        
        self.client = self.app.test_client()
    
    def test_middleware_no_alters_response(self):
        """Test: Middleware no altera la respuesta"""
        response = self.client.get('/test')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'test')
    
    @patch('app.middleware.logging_middleware.logger')
    def test_middleware_multiple_requests(self, mock_logger):
        """Test: Middleware funciona con múltiples requests"""
        self.client.get('/test')
        self.client.get('/test')
        self.client.get('/test')
        
        # Verificar que se llamó al logger varias veces
        self.assertGreaterEqual(mock_logger.info.call_count, 3)


class TestErrorMiddlewareLogging(unittest.TestCase):
    """Tests para verificar logging en caso de errores"""
    
    def setUp(self):
        """Se ejecuta antes de cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        register_logging_middleware(self.app)
        
        @self.app.route('/test/error')
        def test_error_route():
            return {"error": "Internal Server Error"}, 500
        
        self.client = self.app.test_client()
    
    @patch('app.middleware.logging_middleware.logger')
    def test_error_logging(self, mock_logger):
        """Test: Middleware logea responses con status 5xx como ERROR"""
        response = self.client.get('/test/error')
        
        # Verificar que se llamó al logger.log con nivel ERROR
        self.assertTrue(mock_logger.log.called)
        
        # Verificar que alguna llamada tiene nivel ERROR y contiene '500'
        log_calls = mock_logger.log.call_args_list
        has_error = any(call[0][0] == logging.ERROR for call in log_calls)
        has_500 = any('500' in str(call) for call in log_calls)
        
        self.assertTrue(has_error)
        self.assertTrue(has_500)


if __name__ == '__main__':
    unittest.main()
