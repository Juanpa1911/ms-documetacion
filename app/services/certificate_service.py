import datetime
import os
import requests
from io import BytesIO
from app.mapping import AlumnoMapping
from app.models import Alumno
from app.services.documentos_office_service import obtener_tipo_documento
from app.exceptions import AlumnoNotFoundException, DocumentGenerationException

class CertificateService:
    @staticmethod
    def generar_certificado_alumno_regular(id: int, tipo: str) -> BytesIO:
        try:
            alumno = CertificateService._buscar_alumno_por_id(id)
            
            context = CertificateService._obtener_contexto_alumno(alumno)
            documento = obtener_tipo_documento(tipo)
            if not documento:
                raise DocumentGenerationException(f'Tipo de documento no soportado: {tipo}')
                
            if tipo in ('odt', 'docx'):
                plantilla = 'certificado_plantilla'
            else:
                plantilla = 'certificado_pdf'

            resultado = documento.generar(
                carpeta='certificado',
                plantilla=plantilla,
                context=context
            )
            
            if not resultado:
                raise DocumentGenerationException('Error al generar el documento')
            
            return resultado
        except (AlumnoNotFoundException, DocumentGenerationException):
            # Re-lanzar excepciones personalizadas
            raise
        except Exception as e:
            # Convertir excepciones inesperadas en DocumentGenerationException
            raise DocumentGenerationException(f'Error inesperado al generar certificado: {str(e)}')
    
    @staticmethod
    def _obtener_contexto_alumno(alumno: Alumno) -> dict:
        especialidad = alumno.especialidad
        facultad = especialidad.facultad
        universidad = facultad.universidad
        return {
            "alumno": alumno,
            "especialidad": especialidad,
            "facultad": facultad,
            "universidad": universidad,
            "fecha": CertificateService._obtener_fechaactual()
        }
    
    @staticmethod
    def _obtener_fechaactual():
        import locale
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'es_AR.UTF-8')
            except:
                pass  # Usar locale por defecto
        
        fecha_actual = datetime.datetime.now()
        fecha_str = fecha_actual.strftime('%d de %B de %Y')
        return fecha_str
    
    @staticmethod
    def _buscar_alumno_por_id(id: int) -> Alumno:
        from app.exceptions import ServiceUnavailableException
        
        # Usar mock data mientras no existe el microservicio de alumnos
        USE_MOCK = os.getenv('USE_MOCK_DATA', 'true').lower() == 'true'
        
        if USE_MOCK:
            return CertificateService._get_mock_alumno(id)
        
        # Código real para cuando el microservicio esté disponible
        URL_ALUMNOS = os.getenv('ALUMNOS_HOST', 'http://localhost:5000')
        alumno_mapping = AlumnoMapping()
        try:
            r = requests.get(f'{URL_ALUMNOS}/api/v1/alumnos/{id}', timeout=5)
            if r.status_code == 404:
                raise AlumnoNotFoundException(id)
            elif r.status_code != 200:
                raise ServiceUnavailableException('alumnos', f'Status code: {r.status_code}')
            
            result = alumno_mapping.load(r.json())
            return result
        except requests.exceptions.Timeout:
            raise ServiceUnavailableException('alumnos', 'Timeout al conectar')
        except requests.exceptions.ConnectionError:
            raise ServiceUnavailableException('alumnos', 'Error de conexión')
        except requests.exceptions.RequestException as e:
            raise ServiceUnavailableException('alumnos', str(e))
    
    @staticmethod
    def _get_mock_alumno(id: int) -> Alumno:
        """Retorna datos mock de un alumno para testing"""
        from app.models import Especialidad, TipoDocumento, Facultad, Universidad
        
        # Mock de Universidad
        universidad = Universidad()
        universidad.id = 1
        universidad.nombre = "Universidad Tecnológica Nacional"
        
        # Mock de Facultad
        facultad = Facultad()
        facultad.id = 1
        facultad.nombre = "Facultad Regional San Rafael"
        facultad.ciudad = "San Rafael"
        facultad.provincia = "Mendoza"
        facultad.universidad = universidad
        
        # Mock de Especialidad
        especialidad = Especialidad()
        especialidad.id = 1
        especialidad.nombre = "Ingeniería en Sistemas de Información"
        especialidad.letra = "ISI"
        especialidad.observacion = "Especialidad de grado"
        especialidad.facultad = facultad
        
        # Mock de TipoDocumento
        tipo_documento = TipoDocumento()
        tipo_documento.id = 1
        tipo_documento.nombre = "DNI"
        
        # Mock de Alumno
        alumno = Alumno()
        alumno.id = id
        alumno.nombre = "MARIANO PABLO CRISTOBAL"
        alumno.apellido = "SOSA"
        alumno.nrodocumento = "42532964"
        alumno.legajo = "12652"
        alumno.tipo_documento = tipo_documento
        alumno.especialidad = especialidad
        
        return alumno
    