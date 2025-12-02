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
        """Test que RedisClient se inicializa correctamente"""
        mock_redis.return_value.ping.return_value = True
        client = RedisClient()
        self.assertIsNotNone(client.client)
    
    @patch('app.repositories.redis_client.redis.Redis')
    def test_get_returns_none_when_key_not_exists(self, mock_redis):
        """Test que get retorna None cuando la key no existe"""
        mock_redis.return_value.ping.return_value = True
        mock_redis.return_value.get.return_value = None
        
        client = RedisClient()
        result = client.get('nonexistent_key')
        
        self.assertIsNone(result)


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
