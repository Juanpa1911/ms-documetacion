import unittest
from app import create_app
from app.validators import validar_contexto





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
        
        resultado = validar_contexto(context)
        self.assertTrue(resultado)
    
    def test_validar_contexto_sin_alumno(self):
        context = {
            'especialidad': 'datos_especialidad',
            'facultad': 'datos_facultad',
            'universidad': 'datos_universidad',
            'fecha': '1 de diciembre de 2025'
        }
        
        resultado = validar_contexto(context)
        self.assertFalse(resultado)
    
    def test_validar_contexto_sin_fecha(self):

        context = {
            'alumno': 'datos_alumno',
            'especialidad': 'datos_especialidad',
            'facultad': 'datos_facultad',
            'universidad': 'datos_universidad'
            # 'fecha': falta intencionalmente
        }
        
        resultado = validar_contexto(context)     
        self.assertFalse(resultado)