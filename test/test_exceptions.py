import unittest
from app.exceptions.custom_exceptions import (
    BaseAppException,
    AlumnoNotFoundException,
    EspecialidadNotFoundException,
    ServiceUnavailableException,
    CacheException,
    DocumentGenerationException
)


class TestBaseAppException(unittest.TestCase):
    def test_base_exception_creation(self):
        """Test: Crear excepción base con mensaje"""
        exc = BaseAppException("Test error")
        self.assertEqual(str(exc), "Test error")
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.error_code, "InternalServerError")
    
    def test_base_exception_custom_status(self):
        exc = BaseAppException("Test", status_code=400)
        self.assertEqual(exc.status_code, 400)
    
    def test_base_exception_to_dict(self):
        exc = BaseAppException("Test error", status_code=400)
        result = exc.to_dict()
        
        self.assertEqual(result["error"], "InternalServerError")
        self.assertEqual(result["message"], "Test error")
        self.assertEqual(result["status"], 400)


class TestAlumnoNotFoundException(unittest.TestCase):
    def test_alumno_not_found_creation(self):
        exc = AlumnoNotFoundException(alumno_id=123)
        
        self.assertEqual(exc.status_code, 404)
        self.assertEqual(exc.error_code, "AlumnoNotFound")
        self.assertIn("123", str(exc))
    
    def test_alumno_not_found_to_dict(self):
        exc = AlumnoNotFoundException(alumno_id=456)
        result = exc.to_dict()
        
        self.assertEqual(result["error"], "AlumnoNotFound")
        self.assertEqual(result["status"], 404)
        self.assertIn("alumno_id", result)


class TestEspecialidadNotFoundException(unittest.TestCase):
    def test_especialidad_not_found_creation(self):
        """Test: Crear excepción de especialidad no encontrada"""
        exc = EspecialidadNotFoundException(especialidad_id=789)
        
        self.assertEqual(exc.status_code, 404)
        self.assertEqual(exc.error_code, "EspecialidadNotFound")
        self.assertIn("789", str(exc))


class TestServiceUnavailableException(unittest.TestCase):
    def test_service_unavailable_creation(self):
        """Test: Crear excepción de servicio no disponible"""
        exc = ServiceUnavailableException(service_name="alumno-service")
        
        self.assertEqual(exc.status_code, 503)
        self.assertEqual(exc.error_code, "ServiceUnavailable")
        self.assertIn("alumno-service", str(exc))
    
    def test_service_unavailable_with_reason(self):
        exc = ServiceUnavailableException(
            service_name="alumno-service",
            reason="Connection timeout"
        )
        
        result = exc.to_dict()
        self.assertIn("Connection timeout", result["message"])


class TestCacheException(unittest.TestCase):
    
    def test_cache_exception_creation(self):
        exc = CacheException(operation="set", key="alumno:123")
        
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.error_code, "CacheError")
        self.assertIn("set", str(exc))
        self.assertIn("alumno:123", str(exc))


class TestDocumentGenerationException(unittest.TestCase):
    
    def test_document_generation_creation(self):
        exc = DocumentGenerationException(
            document_type="pdf",
            reason="Template not found"
        )
        
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.error_code, "DocumentGenerationError")
        self.assertIn("pdf", str(exc))
        self.assertIn("Template not found", str(exc))
    
    def test_document_generation_to_dict(self):
        exc = DocumentGenerationException(
            document_type="docx",
            reason="Missing data"
        )
        
        result = exc.to_dict()
        self.assertIn("document_type", result)
        self.assertEqual(result["document_type"], "docx")


if __name__ == '__main__':
    unittest.main()

            
            
