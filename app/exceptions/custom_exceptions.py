class BaseAppException(Exception):
    def __init__(self, message: str, status_code: int = 500, error_code: str = "InternalServerError"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
    
    def to_dict(self) -> dict:
        return {
            "error": self.error_code,
            "message": self.message,
            "status": self.status_code
        }


class AlumnoNotFoundException(BaseAppException):
    def __init__(self, alumno_id: int):
        message = f"Alumno con ID {alumno_id} no encontrado"
        super().__init__(message, status_code=404, error_code="AlumnoNotFound")
        self.alumno_id = alumno_id
    
    def to_dict(self) -> dict:
        """Incluye alumno_id en la respuesta"""
        result = super().to_dict()
        result["alumno_id"] = self.alumno_id
        return result


class EspecialidadNotFoundException(BaseAppException):
    def __init__(self, especialidad_id: int):
        message = f"Especialidad con ID {especialidad_id} no encontrada"
        super().__init__(message, status_code=404, error_code="EspecialidadNotFound")
        self.especialidad_id = especialidad_id
    
    def to_dict(self) -> dict:
        """Incluye especialidad_id en la respuesta"""
        result = super().to_dict()
        result["especialidad_id"] = self.especialidad_id
        return result


class ServiceUnavailableException(BaseAppException):
    def __init__(self, service_name: str, reason: str = None):
        message = f"Servicio '{service_name}' no disponible"
        if reason:
            message += f": {reason}"
        
        super().__init__(message, status_code=503, error_code="ServiceUnavailable")
        self.service_name = service_name
        self.reason = reason
    
    def to_dict(self) -> dict:
        """Incluye service_name en la respuesta"""
        result = super().to_dict()
        result["service_name"] = self.service_name
        if self.reason:
            result["reason"] = self.reason
        return result


class CacheException(BaseAppException):
    def __init__(self, operation: str, key: str, reason: str = None):
        message = f"Error en caché - operación '{operation}' en clave '{key}'"
        if reason:
            message += f": {reason}"
        
        super().__init__(message, status_code=500, error_code="CacheError")
        self.operation = operation
        self.key = key
        self.reason = reason
    
    def to_dict(self) -> dict:
        """Incluye detalles de la operación de caché"""
        result = super().to_dict()
        result["operation"] = self.operation
        result["key"] = self.key
        if self.reason:
            result["reason"] = self.reason
        return result


class DocumentGenerationException(BaseAppException):
    def __init__(self, document_type: str, reason: str = "Error desconocido"):
        message = f"Error generando documento tipo '{document_type}': {reason}"
        super().__init__(message, status_code=500, error_code="DocumentGenerationError")
        self.document_type = document_type
        self.reason = reason
    
    def to_dict(self) -> dict:
        """Incluye tipo de documento en la respuesta"""
        result = super().to_dict()
        result["document_type"] = self.document_type
        return result
