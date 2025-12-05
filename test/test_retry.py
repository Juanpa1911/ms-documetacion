"""
Tests para el decorator retry y su integración con repositorios.
Verifica reintentos exitosos, fallidos, backoff exponencial y logging.
"""
import unittest
from unittest.mock import Mock, patch, call
import time
import requests
from io import StringIO

from app.utils import retry


class TestRetryDecorator(unittest.TestCase):
    """Tests unitarios para el decorator retry"""
    
    def test_retry_exitoso_primer_intento(self):
        """Test: Función exitosa en el primer intento no debe reintentar"""
        mock_func = Mock(return_value="success")
        decorated = retry(max_attempts=3)(mock_func)
        
        result = decorated()
        
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 1)
    
    def test_retry_exitoso_segundo_intento(self):
        """Test: Función que falla una vez y luego tiene éxito"""
        mock_func = Mock(side_effect=[Exception("Fallo 1"), "success"])
        decorated = retry(max_attempts=3, delay=0.1)(mock_func)
        
        result = decorated()
        
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 2)
    
    def test_retry_falla_todos_los_intentos(self):
        """Test: Función que falla en todos los intentos debe lanzar excepción"""
        mock_func = Mock(side_effect=requests.ConnectionError("Connection failed"))
        decorated = retry(
            max_attempts=3,
            delay=0.1,
            exceptions=(requests.RequestException,)
        )(mock_func)
        
        with self.assertRaises(requests.ConnectionError):
            decorated()
        
        self.assertEqual(mock_func.call_count, 3)
    
    def test_retry_backoff_exponencial(self):
        """Test: Verificar que el delay aumenta exponencialmente"""
        mock_func = Mock(side_effect=[
            Exception("Fallo 1"),
            Exception("Fallo 2"),
            "success"
        ])
        
        start_time = time.time()
        decorated = retry(max_attempts=3, delay=0.1, backoff=2.0)(mock_func)
        result = decorated()
        elapsed_time = time.time() - start_time
        
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 3)
        # Tiempo total: 0.1s + 0.2s = 0.3s (con margen de error)
        self.assertGreaterEqual(elapsed_time, 0.3)
        self.assertLess(elapsed_time, 0.5)
    
    def test_retry_solo_captura_excepciones_especificadas(self):
        """Test: Solo reintentar con las excepciones especificadas"""
        mock_func = Mock(side_effect=ValueError("Wrong exception"))
        decorated = retry(
            max_attempts=3,
            delay=0.1,
            exceptions=(requests.RequestException,)
        )(mock_func)
        
        with self.assertRaises(ValueError):
            decorated()
        
        # Solo debe intentar una vez porque ValueError no está en exceptions
        self.assertEqual(mock_func.call_count, 1)
    
    @patch('app.utils.retry_decorator.logger')
    def test_retry_logging_warning_en_fallo(self, mock_logger):
        """Test: Verificar que se loguea warning en cada reintento"""
        mock_func = Mock(side_effect=[
            requests.Timeout("Timeout 1"),
            "success"
        ])
        mock_func.__name__ = "test_function"
        
        decorated = retry(
            max_attempts=3,
            delay=0.1,
            exceptions=(requests.RequestException,)
        )(mock_func)
        
        result = decorated()
        
        self.assertEqual(result, "success")
        # Debe haber logueado 1 warning (primer fallo) y 1 info (éxito en segundo intento)
        self.assertEqual(mock_logger.warning.call_count, 1)
        self.assertEqual(mock_logger.info.call_count, 1)
    
    @patch('app.utils.retry_decorator.logger')
    def test_retry_logging_error_en_fallo_final(self, mock_logger):
        """Test: Verificar que se loguea error cuando se agotan los intentos"""
        mock_func = Mock(side_effect=requests.ConnectionError("Failed"))
        mock_func.__name__ = "test_function"
        
        decorated = retry(
            max_attempts=2,
            delay=0.1,
            exceptions=(requests.RequestException,)
        )(mock_func)
        
        with self.assertRaises(requests.ConnectionError):
            decorated()
        
        # Debe haber logueado 1 warning (primer fallo) y 1 error (fallo final)
        self.assertEqual(mock_logger.warning.call_count, 1)
        self.assertEqual(mock_logger.error.call_count, 1)
        
        # Verificar mensaje de error
        error_call = mock_logger.error.call_args[0][0]
        self.assertIn("test_function", error_call)
        self.assertIn("2 intentos", error_call)


class TestRetryIntegracionRepositorios(unittest.TestCase):
    """Tests de integración del retry con repositorios"""
    
    def setUp(self):
        """Configurar Flask app context para los tests"""
        from app import create_app
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Limpiar Flask app context"""
        self.app_context.pop()
    
    @patch('app.repositories.alumno_repository.requests.get')
    def test_alumno_repository_retry_en_timeout(self, mock_get):
        """Test: AlumnoRepository reintenta en caso de timeout"""
        from app.repositories.alumno_repository import AlumnoRepository
        
        # Simular 2 timeouts y luego éxito
        mock_get.side_effect = [
            requests.Timeout("Timeout 1"),
            requests.Timeout("Timeout 2"),
            Mock(status_code=200, json=lambda: {
                'id': 1,
                'nombre': 'Juan',
                'apellido': 'Perez',
                'documento': '12345678',
                'legajo': 'L001',
                'tipoDocumento': {'id': 1, 'descripcion': 'DNI'},
                'especialidad': {
                    'id': 1,
                    'nombre': 'Informática',
                    'facultad': {'id': 1, 'nombre': 'FI', 'universidad': {'id': 1, 'nombre': 'UNT'}}
                }
            })
        ]
        
        repo = AlumnoRepository()
        
        # Mock de RedisClient
        with patch.object(repo.redis_client, 'get', return_value=None):
            with patch.object(repo.redis_client, 'set', return_value=True):
                alumno = repo.get_alumno_by_id(1)
        
        # Verificar que se llamó 3 veces (2 fallos + 1 éxito)
        self.assertEqual(mock_get.call_count, 3)
        self.assertIsNotNone(alumno)
        self.assertEqual(alumno.nombre, 'Juan')
    
    @patch('app.repositories.especialidad_repository.requests.get')
    def test_especialidad_repository_retry_falla_todos_intentos(self, mock_get):
        """Test: EspecialidadRepository lanza excepción después de agotar reintentos"""
        from app.repositories.especialidad_repository import EspecialidadRepository
        
        # Simular falla constante
        mock_get.side_effect = requests.ConnectionError("Service unavailable")
        
        repo = EspecialidadRepository()
        
        # Mock de RedisClient
        with patch.object(repo.redis_client, 'get', return_value=None):
            with self.assertRaises(requests.ConnectionError):
                repo.get_especialidad_by_id(1)
        
        # Verificar que se intentó 3 veces
        self.assertEqual(mock_get.call_count, 3)
    
    @patch('app.repositories.alumno_repository.requests.get')
    @patch('app.utils.retry_decorator.logger')
    def test_retry_logging_en_repositorio_real(self, mock_logger, mock_get):
        """Test: Verificar logging en escenario real con retry"""
        from app.repositories.alumno_repository import AlumnoRepository
        
        # Simular 1 fallo y luego éxito
        mock_get.side_effect = [
            requests.Timeout("Timeout"),
            Mock(status_code=200, json=lambda: {
                'id': 1,
                'nombre': 'Test',
                'apellido': 'User',
                'documento': '11111111',
                'legajo': 'L999',
                'tipoDocumento': {'id': 1, 'descripcion': 'DNI'},
                'especialidad': {
                    'id': 1,
                    'nombre': 'Test',
                    'facultad': {'id': 1, 'nombre': 'FT', 'universidad': {'id': 1, 'nombre': 'UT'}}
                }
            })
        ]
        
        repo = AlumnoRepository()
        
        with patch.object(repo.redis_client, 'get', return_value=None):
            with patch.object(repo.redis_client, 'set', return_value=True):
                alumno = repo.get_alumno_by_id(1)
        
        self.assertIsNotNone(alumno)
        # Verificar que se logueó el warning del primer fallo
        mock_logger.warning.assert_called()
        warning_msg = mock_logger.warning.call_args[0][0]
        self.assertIn("_fetch_from_service", warning_msg)
        self.assertIn("intento 1/3", warning_msg)


if __name__ == '__main__':
    unittest.main()
