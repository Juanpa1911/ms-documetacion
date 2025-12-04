class AlumnoNotFoundException(Exception):
    """Excepción lanzada cuando no se encuentra un alumno."""
    pass

class EspecialidadNotFoundException(Exception):
    """Excepción lanzada cuando no se encuentra una especialidad."""
    pass

class ServiceUnavailableException(Exception):
    """Excepción lanzada cuando un servicio no está disponible."""
    pass

class CacheException(Exception):
    """Excepción lanzada cuando hay un error relacionado con la caché."""
    pass

class DocumentGenerationException(Exception):
    """Excepción lanzada cuando hay un error en la generación de documentos."""
    pass
