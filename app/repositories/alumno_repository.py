import requests
import logging
from typing import Optional
from flask import current_app

from app.repositories.redis_client import RedisClient
from app.mapping import AlumnoMapping
from app.models import Alumno

logger = logging.getLogger(__name__)

class AlumnoRepository:
    """Repositorio para gestionar la obtención de alumnos con cache Redis"""
    
    def __init__(self):
        self.redis_client = RedisClient()
        self.alumno_mapping = AlumnoMapping()
    
    def _get_cache_key(self, alumno_id: int) -> str:
        """Genera la clave de cache para un alumno"""
        return f"alumno:{alumno_id}"
    
    def _fetch_from_service(self, alumno_id: int) -> dict:
        """Obtiene el alumno desde el microservicio externo"""
        url = f"{current_app.config['ALUMNO_SERVICE_URL']}/alumnos/{alumno_id}"
        timeout = current_app.config['REQUEST_TIMEOUT']
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    
    def get_alumno_by_id(self, alumno_id: int) -> Optional[Alumno]:
        """Obtiene un alumno por ID usando cache Redis"""
        cache_key = self._get_cache_key(alumno_id)
        
        # Intentar obtener del cache
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            try:
                return self.alumno_mapping.load(cached_data)
            except Exception as e:
                logger.error(f"Error al deserializar alumno desde cache: {e}")
                self.redis_client.delete(cache_key)
        
        # Consultar servicio
        try:
            alumno_data = self._fetch_from_service(alumno_id)
            
            # Guardar en cache
            ttl = current_app.config['CACHE_ALUMNO_TTL']
            self.redis_client.set(cache_key, alumno_data, ttl)
            
            return self.alumno_mapping.load(alumno_data)
            
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            logger.error(f"Error al obtener alumno {alumno_id}: {e}")
            raise

