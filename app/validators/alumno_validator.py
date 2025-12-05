import logging
from app.models import Alumno
from app.exceptions import DocumentGenerationException


logger = logging.getLogger(__name__)


def validar_id_alumno(alumno_id: int) -> None:
    """Valida que el ID del alumno sea válido (mayor a 0)"""
    if alumno_id <= 0:
        return False
    return True


def validar_datos_alumno(alumno: Alumno) -> bool:
    """
    Valida que el objeto Alumno tenga todos los campos requeridos.
    
    Args:
        alumno: Objeto Alumno a validar
        
    Returns:
        bool: True si el alumno tiene todos los campos requeridos, False en caso contrario
    """
    # Primero verificar que el alumno no sea None
    if not alumno:
        logger.warning("Se intentó validar un alumno None")
        return False
    
    # Lista de campos que DEBEN tener valor (no None)
    campos_requeridos = [
        alumno.nombre,
        alumno.apellido,
        alumno.nrodocumento,
        alumno.legajo,
        alumno.tipo_documento,
        alumno.especialidad
    ]
    
    # all() retorna True solo si TODOS los valores son "truthy" (no None, no vacío)
    # Si alguno es None, retorna False
    es_valido = all(campo is not None for campo in campos_requeridos)
    
       
    if not es_valido:
        campos_faltantes = []
        if not alumno.nombre:
            campos_faltantes.append('nombre')
        if not alumno.apellido:
            campos_faltantes.append('apellido')
        if not alumno.nrodocumento:
            campos_faltantes.append('nrodocumento')
        if not alumno.legajo:
            campos_faltantes.append('legajo')
        if not alumno.tipo_documento:
            campos_faltantes.append('tipo_documento')
        if not alumno.especialidad:
            campos_faltantes.append('especialidad')
        
        logger.warning(f"Alumno {alumno.id} tiene campos faltantes: {campos_faltantes}")
       
    return es_valido