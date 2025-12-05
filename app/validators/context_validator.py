import logging

logger = logging.getLogger(__name__)


def validar_contexto(context: dict) -> bool:
    """
    Valida que el contexto para generar documentos tenga todas las claves requeridas.
    
    Args:
        context: Diccionario con los datos necesarios para generar un documento
        
    Returns:
        bool: True si el contexto es válido, False en caso contrario
    """
    # Lista de claves que DEBEN existir en el contexto
    claves_requeridas = ['alumno', 'especialidad', 'facultad', 'universidad', 'fecha']
    
    # all() retorna True solo si TODAS las condiciones son True
    # Verifica que cada clave requerida esté presente en el context
    es_valido = all(clave in context for clave in claves_requeridas)
    
    if not es_valido:
        claves_faltantes = [clave for clave in claves_requeridas if clave not in context]
        logger.warning(f"Contexto incompleto. Faltan las claves: {claves_faltantes}")
    
    return es_valido
