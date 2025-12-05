import requests
import logging
from typing import Optional
from flask import current_app

from app.repositories.redis_client import RedisClient
from app.mapping import EspecialidadMapping
from app.models import Especialidad
from app.utils import retry

logger = logging.getLogger(__name__)

class EspecialidadRepository:
    """Repositorio para gestionar la obtención de especialidades con cache Redis"""
    
    def __init__(self):
        self.redis_client = RedisClient()
        self.especialidad_mapping = EspecialidadMapping()
    
    def _get_cache_key(self, especialidad_id: int) -> str:
        """Genera la clave de cache para una especialidad"""
        return f"especialidad:{especialidad_id}"
    
    @retry(max_attempts=3, delay=0.5, backoff=2.0, exceptions=(requests.RequestException,))
    def _fetch_from_service(self, especialidad_id: int) -> dict:
        """Obtiene la especialidad desde el microservicio externo con retry automático"""
        url = f"{current_app.config['ESPECIALIDAD_SERVICE_URL']}/especialidades/{especialidad_id}"
        timeout = current_app.config['REQUEST_TIMEOUT']
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    
    def get_especialidad_by_id(self, especialidad_id: int) -> Optional[Especialidad]:
        """Obtiene una especialidad por ID usando cache Redis"""
        cache_key = self._get_cache_key(especialidad_id)
        
        # Intentar obtener del cache
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            try:
                return self.especialidad_mapping.load(cached_data)
            except Exception as e:
                logger.error(f"Error al deserializar especialidad desde cache: {e}")
                self.redis_client.delete(cache_key)
        
        # Consultar servicio
        try:
            especialidad_data = self._fetch_from_service(especialidad_id)
            
            # Guardar en cache
            ttl = current_app.config['CACHE_ESPECIALIDAD_TTL']
            self.redis_client.set(cache_key, especialidad_data, ttl)
            
            return self.especialidad_mapping.load(especialidad_data)
            
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            logger.error(f"Error al obtener especialidad {especialidad_id}: {e}")
            raise

