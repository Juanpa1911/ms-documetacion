import redis
import json
import logging
from typing import Optional, Any
from flask import current_app

logger = logging.getLogger(__name__)

class RedisService:
    """Servicio para gestionar caché con Redis"""
    
    _client: Optional[redis.Redis] = None
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """Obtiene o crea el cliente de Redis"""
        if cls._client is None:
            try:
                cls._client = redis.Redis(
                    host=current_app.config.get('REDIS_HOST', 'localhost'),
                    port=current_app.config.get('REDIS_PORT', 6379),
                    db=current_app.config.get('REDIS_DB', 0),
                    password=current_app.config.get('REDIS_PASSWORD') or None,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                # Test connection
                cls._client.ping()
                logger.info(f"Redis conectado exitosamente")
            except redis.ConnectionError as e:
                logger.warning(f"No se pudo conectar a Redis: {e}. Funcionando sin caché.")
                cls._client = None
        return cls._client
    
    @classmethod
    def get(cls, key: str) -> Optional[dict]:
        """Obtiene un valor del caché"""
        try:
            client = cls.get_client()
            if client is None:
                return None
            
            value = client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Error al obtener de Redis: {e}")
            return None
    
    @classmethod
    def set(cls, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Guarda un valor en el caché
        
        Args:
            key: Clave del caché
            value: Valor a almacenar (se serializa a JSON)
            ttl: Tiempo de vida en segundos (default: 5 minutos)
        """
        try:
            client = cls.get_client()
            if client is None:
                return False
            
            client.setex(key, ttl, json.dumps(value))
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error al guardar en Redis: {e}")
            return False
    
    @classmethod
    def delete(cls, key: str) -> bool:
        """Elimina una clave del caché"""
        try:
            client = cls.get_client()
            if client is None:
                return False
            
            client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Error al eliminar de Redis: {e}")
            return False
    
    @classmethod
    def clear_pattern(cls, pattern: str) -> int:
        """
        Elimina todas las claves que coincidan con un patrón
        
        Args:
            pattern: Patrón de búsqueda (ej: "alumno:*")
        """
        try:
            client = cls.get_client()
            if client is None:
                return 0
            
            keys = client.keys(pattern)
            if keys:
                deleted = client.delete(*keys)
                logger.info(f"Cache CLEAR: {pattern} ({deleted} claves)")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error al limpiar patrón en Redis: {e}")
            return 0
    
    @classmethod
    def health_check(cls) -> bool:
        """Verifica si Redis está disponible"""
        try:
            client = cls.get_client()
            if client is None:
                return False
            client.ping()
            return True
        except:
            return False
