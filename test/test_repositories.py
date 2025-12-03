import unittest
from unittest.mock import Mock, patch
from app import create_app
from app.repositories import RedisClient, AlumnoRepository


class RedisClientUnitTest(unittest.TestCase):
    """Tests unitarios con mocks (NO requieren Redis)"""
    
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()
    
    @patch('app.repositories.redis_client.redis.Redis')
    def test_inicializa_correctamente(self, mock_redis):
        """Verifica que RedisClient se conecta"""
        mock_redis.return_value.ping.return_value = True
        client = RedisClient()
        self.assertIsNotNone(client.client)
    
    @patch('app.repositories.redis_client.redis.Redis')
    def test_get_sin_clave(self, mock_redis):
        """Verifica que get retorna None si la clave no existe"""
        mock_redis.return_value.ping.return_value = True
        mock_redis.return_value.get.return_value = None
        
        client = RedisClient()
        self.assertIsNone(client.get('inexistente'))


class RedisClientIntegrationTest(unittest.TestCase):
    """Tests de integración (REQUIEREN Redis corriendo en localhost:6379)"""
    
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = RedisClient()
        
        if not self.client.client:
            self.skipTest("Redis no disponible - Inicia: docker run -d -p 6379:6379 redis:7-alpine")
    
    def tearDown(self):
        if self.client.client:
            for key in self.client.client.keys('test:*'):
                self.client.client.delete(key)
        self.app_context.pop()
    
    def test_set_y_get(self):
        """Verifica guardar y recuperar datos en Redis real"""
        data = {'nombre': 'Juan', 'edad': 25}
        
        self.assertTrue(self.client.set('test:1', data, 60))
        self.assertEqual(self.client.get('test:1'), data)
    
    def test_ttl_expira(self):
        """Verifica que las keys expiran correctamente"""
        import time
        
        self.client.set('test:expire', 'valor', 1)
        self.assertIsNotNone(self.client.get('test:expire'))
        
        time.sleep(2)
        self.assertIsNone(self.client.get('test:expire'))


class AlumnoRepositoryTest(unittest.TestCase):
    """Tests para AlumnoRepository"""
    
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()
    
    def test_cache_key_formato(self):
        """Verifica que genera cache key con formato correcto"""
        repo = AlumnoRepository()
        self.assertEqual(repo._get_cache_key(123), 'alumno:123')


if __name__ == '__main__':
    unittest.main()
