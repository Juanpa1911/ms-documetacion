import redis
import json
import logging
from typing import Optional, Any
from flask import current_app

logger = logging.getLogger(__name__)

class RedisClient:
    """Cliente para gestionar conexiones con Redis"""
    
    def __init__(self):
        """Inicializa la conexión a Redis"""
        try:
            self.client = redis.Redis(
                host=current_app.config['REDIS_HOST'],
                port=current_app.config['REDIS_PORT'],
                db=current_app.config['REDIS_DB'],
                password=current_app.config.get('REDIS_PASSWORD'),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.client.ping()
            logger.info("Conexión a Redis establecida")
        except redis.ConnectionError as e:
            logger.warning(f"Redis no disponible: {e}")
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor de Redis deserializado desde JSON"""
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except (json.JSONDecodeError, redis.RedisError) as e:
            logger.error(f"Error al obtener {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int) -> bool:
        """Almacena un valor en Redis serializado a JSON"""
        if not self.client:
            return False
        
        try:
            self.client.setex(key, ttl, json.dumps(value))
            return True
        except (TypeError, json.JSONDecodeError, redis.RedisError) as e:
            logger.error(f"Error al almacenar {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Elimina una clave de Redis"""
        if not self.client:
            return False
        
        try:
            return bool(self.client.delete(key))
        except redis.RedisError as e:
            logger.error(f"Error al eliminar {key}: {e}")
            return False
