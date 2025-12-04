import pytest
from app.exceptions.custom_exceptions import (
    BaseAppException,
    AlumnoNotFoundException,
    EspecialidadNotFoundException,
    ServiceUnavailableException,
    CacheException,
    DocumentGenerationException
)


class TestBaseAppException:
    def test_base_exception_creation(self):
        """Test: Crear excepción base con mensaje"""
        exc = BaseAppException("Test error")
        assert str(exc) == "Test error"
        assert exc.status_code == 500
        assert exc.error_code == "InternalServerError"
    
    def test_base_exception_custom_status(self):
        exc = BaseAppException("Test", status_code=400)
        assert exc.status_code == 400
    
    def test_base_exception_to_dict(self):
        exc = BaseAppException("Test error", status_code=400)
        result = exc.to_dict()
        
        assert result["error"] == "InternalServerError"
        assert result["message"] == "Test error"
        assert result["status"] == 400


class TestAlumnoNotFoundException:
    def test_alumno_not_found_creation(self):
        exc = AlumnoNotFoundException(alumno_id=123)
        
        assert exc.status_code == 404
        assert exc.error_code == "AlumnoNotFound"
        assert "123" in str(exc)
    
    def test_alumno_not_found_to_dict(self):
        exc = AlumnoNotFoundException(alumno_id=456)
        result = exc.to_dict()
        
        assert result["error"] == "AlumnoNotFound"
        assert result["status"] == 404
        assert "alumno_id" in result


class TestEspecialidadNotFoundException:
    def test_especialidad_not_found_creation(self):
        """Test: Crear excepción de especialidad no encontrada"""
        exc = EspecialidadNotFoundException(especialidad_id=789)
        
        assert exc.status_code == 404
        assert exc.error_code == "EspecialidadNotFound"
        assert "789" in str(exc)


class TestServiceUnavailableException:
    def test_service_unavailable_creation(self):
        """Test: Crear excepción de servicio no disponible"""
        exc = ServiceUnavailableException(service_name="alumno-service")
        
        assert exc.status_code == 503
        assert exc.error_code == "ServiceUnavailable"
        assert "alumno-service" in str(exc)
    
    def test_service_unavailable_with_reason(self):
        exc = ServiceUnavailableException(
            service_name="alumno-service",
            reason="Connection timeout"
        )
        
        result = exc.to_dict()
        assert "Connection timeout" in result["message"]


class TestCacheException:
    
    def test_cache_exception_creation(self):
        exc = CacheException(operation="set", key="alumno:123")
        
        assert exc.status_code == 500
        assert exc.error_code == "CacheError"
        assert "set" in str(exc)
        assert "alumno:123" in str(exc)


class TestDocumentGenerationException:
    
    def test_document_generation_creation(self):
        exc = DocumentGenerationException(
            document_type="pdf",
            reason="Template not found"
        )
        
        assert exc.status_code == 500
        assert exc.error_code == "DocumentGenerationError"
        assert "pdf" in str(exc)
        assert "Template not found" in str(exc)
    
    def test_document_generation_to_dict(self):
        exc = DocumentGenerationException(
            document_type="docx",
            reason="Missing data"
        )
        
        result = exc.to_dict()
        assert "document_type" in result
        assert result["document_type"] == "docx"

            
            
