import unittest
from app import create_app
from app.services.certificate_service import CertificateService
from app.models import Alumno, Especialidad, TipoDocumento


class ValidacionContextoTest(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()
    
    def test_validar_contexto_completo(self):

        context = {
            'alumno': 'datos_alumno',
            'especialidad': 'datos_especialidad',
            'facultad': 'datos_facultad',
            'universidad': 'datos_universidad',
            'fecha': '1 de diciembre de 2025'
        }
        
        resultado = CertificateService._validar_contexto(context)
        self.assertTrue(resultado)
    
    def test_validar_contexto_sin_alumno(self):
        context = {
            'especialidad': 'datos_especialidad',
            'facultad': 'datos_facultad',
            'universidad': 'datos_universidad',
            'fecha': '1 de diciembre de 2025'
        }
        
        resultado = CertificateService._validar_contexto(context)
        self.assertFalse(resultado)
    
    def test_validar_contexto_sin_fecha(self):

        context = {
            'alumno': 'datos_alumno',
            'especialidad': 'datos_especialidad',
            'facultad': 'datos_facultad',
            'universidad': 'datos_universidad'
            # 'fecha': falta intencionalmente
        }
        
        resultado = CertificateService._validar_contexto(context)     
        self.assertFalse(resultado)


class ValidacionDatosAlumnoTest(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()
    
    def test_validar_alumno_completo(self):

        # Arrange - Crear alumno con todos los datos
        tipo_doc = TipoDocumento()
        tipo_doc.nombre = "DNI"
        
        especialidad = Especialidad()
        especialidad.nombre = "Ingeniería en Sistemas"
        
        alumno = Alumno()
        alumno.nombre = "MARIA"
        alumno.apellido = "GARCIA"
        alumno.nrodocumento = "12345678"
        alumno.legajo = "50001"
        alumno.tipo_documento = tipo_doc
        alumno.especialidad = especialidad
        
        # Act
        resultado = CertificateService._validar_datos_alumno(alumno)
        
        # Assert
        self.assertTrue(resultado)
    
    def test_validar_alumno_sin_nombre_debe_retornar_false(self):

        tipo_doc = TipoDocumento()
        tipo_doc.nombre = "DNI"
        
        especialidad = Especialidad()
        especialidad.nombre = "ISI"
        
        alumno = Alumno()
        alumno.nombre = None 
        alumno.apellido = "GARCIA"
        alumno.nrodocumento = "12345678"
        alumno.legajo = "50001"
        alumno.tipo_documento = tipo_doc
        alumno.especialidad = especialidad
        
        resultado = CertificateService._validar_datos_alumno(alumno)
        
        self.assertFalse(resultado)
    
    def test_validar_alumno_sin_especialidad_debe_retornar_false(self):

        tipo_doc = TipoDocumento()
        tipo_doc.nombre = "DNI"
        
        alumno = Alumno()
        alumno.nombre = "MARIA"
        alumno.apellido = "GARCIA"
        alumno.nrodocumento = "12345678"
        alumno.legajo = "50001"
        alumno.tipo_documento = tipo_doc
        alumno.especialidad = None 
        
        resultado = CertificateService._validar_datos_alumno(alumno)
        
        self.assertFalse(resultado)
    
    def test_validar_alumno_none_debe_retornar_false(self):

        resultado = CertificateService._validar_datos_alumno(None)
        self.assertFalse(resultado)


if __name__ == '__main__':
    unittest.main()
