"""
Decorator para implementar patrón retry con backoff exponencial.
Aplica principios KISS, DRY, SOLID y Clean Code.
"""
import time
import logging
from functools import wraps
from typing import Callable, Type, Tuple

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator para reintentar operaciones fallidas con backoff exponencial.
    
    Implementa el patrón Retry para operaciones I/O que pueden fallar temporalmente,
    como llamadas HTTP a microservicios externos o conexiones a servicios.
    
    Args:
        max_attempts: Número máximo de intentos (default: 3)
        delay: Delay inicial en segundos entre reintentos (default: 1.0)
        backoff: Factor de multiplicación del delay (default: 2.0)
                 Ejemplo: delay=1, backoff=2 → delays de 1s, 2s, 4s
        exceptions: Tupla de excepciones a capturar y reintentar (default: Exception)
    
    Returns:
        Callable: Función decorada con lógica de retry
    
    Raises:
        Exception: La última excepción capturada si se agotan los intentos
    
    Example:
        >>> @retry(max_attempts=3, delay=0.5, exceptions=(requests.RequestException,))
        >>> def fetch_data(url):
        >>>     return requests.get(url)
    
    Principios aplicados:
        - KISS: Implementación simple y directa
        - DRY: Código reutilizable para cualquier función
        - SRP (SOLID): Solo se encarga de reintentos, no modifica lógica de negocio
        - OCP (SOLID): Extensible vía parámetros sin modificar el código
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Log solo si hubo reintentos previos
                    if attempt > 1:
                        func_name = getattr(func, '__name__', 'function')
                        logger.info(
                            f"{func_name} exitoso en intento {attempt}/{max_attempts}"
                        )
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    
                    # Si es el último intento, loguear error y lanzar excepción
                    if attempt == max_attempts:
                        func_name = getattr(func, '__name__', 'function')
                        logger.error(
                            f"{func_name} falló después de {max_attempts} intentos: {e}"
                        )
                        raise
                    
                    # Log de warning con información del reintento
                    func_name = getattr(func, '__name__', 'function')
                    logger.warning(
                        f"{func_name} falló (intento {attempt}/{max_attempts}), "
                        f"reintentando en {current_delay:.1f}s: {type(e).__name__}: {e}"
                    )
                    
                    # Esperar antes del siguiente intento
                    time.sleep(current_delay)
                    
                    # Incrementar delay con backoff exponencial
                    current_delay *= backoff
            
            # Fallback (nunca debería llegar aquí)
            raise last_exception
        
        return wrapper
    return decorator
