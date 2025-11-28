import redis
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import timedelta
import os

logger = logging.getLogger(__name__)


class RedisService:
    """
    Servicio para gestionar operaciones con Redis:
    - Caché de datos
    - Almacenamiento de transacciones SAGA
    - Pub/Sub para comunicación entre microservicios
    - Coordinación distribuida
    """
    
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_db = int(os.getenv('REDIS_DB', 0))
        self.redis_password = os.getenv('REDIS_PASSWORD', None)
        
        self._client = None
        self._pubsub = None
        
    @property
    def client(self) -> redis.Redis:
        """Obtiene o crea el cliente Redis"""
        if self._client is None:
            self._client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            try:
                self._client.ping()
                logger.info(f"✓ Conexión establecida con Redis en {self.redis_host}:{self.redis_port}")
            except redis.ConnectionError as e:
                logger.error(f"✗ Error conectando a Redis: {e}")
                raise
        return self._client
    
    # ==================== OPERACIONES DE CACHÉ ====================
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error obteniendo clave {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Guarda un valor en el caché
        
        Args:
            key: Clave
            value: Valor a guardar
            ttl: Tiempo de vida en segundos (None = sin expiración)
        """
        try:
            serialized = json.dumps(value)
            if ttl:
                return self.client.setex(key, ttl, serialized)
            else:
                return self.client.set(key, serialized)
        except Exception as e:
            logger.error(f"Error guardando clave {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Elimina una clave del caché"""
        try:
            return self.client.delete(key) > 0
        except Exception as e:
            logger.error(f"Error eliminando clave {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Verifica si una clave existe"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error verificando existencia de {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """Obtiene el tiempo de vida restante de una clave en segundos"""
        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"Error obteniendo TTL de {key}: {e}")
            return -1
    
    # ==================== OPERACIONES PARA SAGA ====================
    
    def save_saga_transaction(self, transaction_id: str, transaction_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """
        Guarda el estado de una transacción SAGA
        
        Args:
            transaction_id: ID único de la transacción
            transaction_data: Datos de la transacción
            ttl: Tiempo de vida en segundos (default: 1 hora)
        """
        key = f"saga:transaction:{transaction_id}"
        return self.set(key, transaction_data, ttl)
    
    def get_saga_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado de una transacción SAGA"""
        key = f"saga:transaction:{transaction_id}"
        return self.get(key)
    
    def update_saga_transaction(self, transaction_id: str, transaction_data: Dict[str, Any]) -> bool:
        """Actualiza el estado de una transacción SAGA manteniendo el TTL original"""
        key = f"saga:transaction:{transaction_id}"
        ttl = self.get_ttl(key)
        if ttl > 0:
            return self.set(key, transaction_data, ttl)
        return self.set(key, transaction_data)
    
    def delete_saga_transaction(self, transaction_id: str) -> bool:
        """Elimina una transacción SAGA"""
        key = f"saga:transaction:{transaction_id}"
        return self.delete(key)
    
    def list_saga_transactions(self, pattern: str = "*") -> List[str]:
        """Lista IDs de transacciones SAGA que coincidan con el patrón"""
        try:
            keys = self.client.keys(f"saga:transaction:{pattern}")
            return [key.replace("saga:transaction:", "") for key in keys]
        except Exception as e:
            logger.error(f"Error listando transacciones SAGA: {e}")
            return []
    
    # ==================== PUB/SUB PARA EVENTOS ====================
    
    def publish_event(self, channel: str, message: Dict[str, Any]) -> int:
        """
        Publica un evento en un canal
        
        Args:
            channel: Nombre del canal
            message: Mensaje a publicar
            
        Returns:
            Número de suscriptores que recibieron el mensaje
        """
        try:
            serialized = json.dumps(message)
            recipients = self.client.publish(channel, serialized)
            logger.info(f"Evento publicado en canal '{channel}': {recipients} suscriptores")
            return recipients
        except Exception as e:
            logger.error(f"Error publicando evento en {channel}: {e}")
            return 0
    
    def subscribe_to_channel(self, channel: str):
        """Suscribe a un canal para recibir eventos"""
        try:
            if self._pubsub is None:
                self._pubsub = self.client.pubsub()
            self._pubsub.subscribe(channel)
            logger.info(f"Suscrito al canal '{channel}'")
            return self._pubsub
        except Exception as e:
            logger.error(f"Error suscribiendo al canal {channel}: {e}")
            return None
    
    def unsubscribe_from_channel(self, channel: str):
        """Cancela la suscripción a un canal"""
        try:
            if self._pubsub:
                self._pubsub.unsubscribe(channel)
                logger.info(f"Desuscrito del canal '{channel}'")
        except Exception as e:
            logger.error(f"Error desuscribiendo del canal {channel}: {e}")
    
    # ==================== BLOQUEOS DISTRIBUIDOS ====================
    
    def acquire_lock(self, lock_name: str, timeout: int = 10, blocking_timeout: int = 5) -> bool:
        """
        Adquiere un bloqueo distribuido
        
        Args:
            lock_name: Nombre del bloqueo
            timeout: Tiempo máximo que durará el bloqueo (segundos)
            blocking_timeout: Tiempo máximo de espera para adquirir el bloqueo (segundos)
        """
        try:
            lock = self.client.lock(
                f"lock:{lock_name}",
                timeout=timeout,
                blocking_timeout=blocking_timeout
            )
            acquired = lock.acquire(blocking=True)
            if acquired:
                logger.info(f"Bloqueo '{lock_name}' adquirido")
            return acquired
        except Exception as e:
            logger.error(f"Error adquiriendo bloqueo {lock_name}: {e}")
            return False
    
    def release_lock(self, lock_name: str) -> bool:
        """Libera un bloqueo distribuido"""
        try:
            lock = self.client.lock(f"lock:{lock_name}")
            lock.release()
            logger.info(f"Bloqueo '{lock_name}' liberado")
            return True
        except Exception as e:
            logger.error(f"Error liberando bloqueo {lock_name}: {e}")
            return False
    
    # ==================== UTILIDADES ====================
    
    def ping(self) -> bool:
        """Verifica la conexión con Redis"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Error en ping a Redis: {e}")
            return False
    
    def flush_db(self) -> bool:
        """Limpia toda la base de datos (¡USAR CON PRECAUCIÓN!)"""
        try:
            self.client.flushdb()
            logger.warning("Base de datos Redis limpiada")
            return True
        except Exception as e:
            logger.error(f"Error limpiando base de datos: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Obtiene información del servidor Redis"""
        try:
            return self.client.info()
        except Exception as e:
            logger.error(f"Error obteniendo info de Redis: {e}")
            return {}
    
    def close(self):
        """Cierra las conexiones con Redis"""
        try:
            if self._pubsub:
                self._pubsub.close()
            if self._client:
                self._client.close()
            logger.info("Conexiones con Redis cerradas")
        except Exception as e:
            logger.error(f"Error cerrando conexiones: {e}")


# Instancia global del servicio
redis_service = RedisService()
