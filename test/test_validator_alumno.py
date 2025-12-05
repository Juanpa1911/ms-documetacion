import unittest
from app import create_app
from app.validators import validar_datos_alumno, validar_id_alumno
from app.models import Alumno, Especialidad, TipoDocumento

class ValidacionIdAlumno(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()

    def test_validar_id(self):
        id = 1
        self.assertTrue(validar_id_alumno(id))

    def test_validar_id_erroneo(self):
        id = -2
        self.assertFalse(validar_id_alumno(id))



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
        resultado = validar_datos_alumno(alumno)
        
        # Assert
        self.assertTrue(resultado)
    
    def test_validar_alumno_sin_nombre(self):

        tipo_doc = TipoDocumento()
        tipo_doc.nombre = "DNI"
        
        especialidad = Especialidad()
        especialidad.nombre = "ISI"
        
        alumno = Alumno()
        alumno.id = 1
        alumno.nombre = None 
        alumno.apellido = "GARCIA"
        alumno.nrodocumento = "12345678"
        alumno.legajo = "50001"
        alumno.tipo_documento = tipo_doc
        alumno.especialidad = especialidad
        
        resultado = validar_datos_alumno(alumno)
        
        self.assertFalse(resultado)
    
    def test_validar_alumno_sin_especialidad(self):

        tipo_doc = TipoDocumento()
        tipo_doc.nombre = "DNI"
        
        alumno = Alumno()
        alumno.id = 1
        alumno.nombre = "MARIA"
        alumno.apellido = "GARCIA"
        alumno.nrodocumento = "12345678"
        alumno.legajo = "50001"
        alumno.tipo_documento = tipo_doc
        alumno.especialidad = None 
        
        resultado = validar_datos_alumno(alumno)
        
        self.assertFalse(resultado)
    
    def test_validar_alumno_none(self):

        resultado = validar_datos_alumno(None)
        self.assertFalse(resultado)


if __name__ == '__main__':
    unittest.main()
