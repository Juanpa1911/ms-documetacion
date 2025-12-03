import unittest
from unittest.mock import Mock, patch
from app import create_app
from app.repositories import RedisClient, AlumnoRepository

class RedisClientTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()
    
    @patch('app.repositories.redis_client.redis.Redis')
    def test_redis_client_initialization(self, mock_redis):
        """Test que RedisClient se inicializa correctamente (con mock)"""
        mock_redis.return_value.ping.return_value = True
        client = RedisClient()
        self.assertIsNotNone(client.client)
    
    @patch('app.repositories.redis_client.redis.Redis')
    def test_get_returns_none_when_key_not_exists(self, mock_redis):
        """Test que get retorna None cuando la key no existe (con mock)"""
        mock_redis.return_value.ping.return_value = True
        mock_redis.return_value.get.return_value = None
        
        client = RedisClient()
        result = client.get('nonexistent_key')
        
        self.assertIsNone(result)


class RedisClientIntegrationTestCase(unittest.TestCase):
    """Tests de integración con Redis real"""
    
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = RedisClient()
        
        # Verifica que Redis esté disponible
        if not self.client.client:
            self.skipTest("Redis no está disponible")
    
    def tearDown(self):
        # Limpia las keys de test
        if self.client.client:
            for key in self.client.client.keys('test:*'):
                self.client.client.delete(key)
        self.app_context.pop()
    
    def test_set_and_get_value(self):
        """Test de set y get en Redis real"""
        test_data = {'nombre': 'Juan', 'edad': 25}
        
        # Set
        result = self.client.set('test:alumno:1', test_data, ttl=60)
        self.assertTrue(result)
        
        # Get
        retrieved = self.client.get('test:alumno:1')
        self.assertEqual(retrieved, test_data)
    
    def test_get_nonexistent_key(self):
        """Test que get retorna None cuando la key no existe en Redis real"""
        result = self.client.get('test:nonexistent:key')
        self.assertIsNone(result)
    
    def test_ttl_expiration(self):
        """Test que las keys expiran correctamente"""
        import time
        
        self.client.set('test:expire', 'value', ttl=1)
        
        # Verifica que existe
        self.assertIsNotNone(self.client.get('test:expire'))
        
        # Espera a que expire
        time.sleep(2)
        
        # Verifica que ya no existe
        self.assertIsNone(self.client.get('test:expire'))


class AlumnoRepositoryTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()
    
    def test_get_cache_key(self):
        """Test que se genera correctamente la cache key"""
        repo = AlumnoRepository()
        key = repo._get_cache_key(123)
        self.assertEqual(key, 'alumno:123')


if __name__ == '__main__':
    unittest.main()
