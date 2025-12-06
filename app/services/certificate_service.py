import datetime
import os
import logging
from io import BytesIO
from app.validators import validar_datos_alumno, validar_contexto, validar_id_alumno
from app.models import Alumno
from app.services.documentos_office_service import obtener_tipo_documento
from app.exceptions import AlumnoNotFoundException, EspecialidadNotFoundException, DocumentGenerationException, ServiceUnavailableException
from app.repositories.alumno_repository import AlumnoRepository
from app.repositories.especialidad_repository import EspecialidadRepository

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

class CertificateService:
    @staticmethod
    def generar_certificado_alumno_regular(id: int, tipo: str) -> BytesIO:


        logger.info(f'Iniciando generación de certificado para alumno {id} en formato {tipo}')
        
        try:

            logger.debug(f'Buscando alumno con ID {id}')
            alumno = CertificateService._buscar_alumno_por_id(id)
            logger.debug(f'Alumno encontrado: {alumno.nombre} {alumno.apellido}')
            
            # Enriquecer especialidad si solo tiene ID (llamar a MS académica)
            logger.debug('Verificando y enriqueciendo datos de especialidad')
            alumno = CertificateService._enriquecer_especialidad(alumno)
            
            logger.debug('Validando datos del alumno')
            if not validar_datos_alumno(alumno):
                logger.error(f'Datos incompletos para alumno {id}')
                raise DocumentGenerationException(
                    tipo,
                    f'El alumno {id} tiene datos incompletos. '
                    'Verifique que tenga nombre, apellido, documento, legajo, '
                    'tipo de documento y especialidad.'
                )

            logger.debug('Construyendo contexto con datos del alumno y relaciones')
            context = CertificateService._obtener_contexto_alumno(alumno)

            logger.debug('Validando contexto completo')
            if not validar_contexto(context):
                logger.error('Contexto incompleto para generar documento')
                raise DocumentGenerationException(
                    tipo,
                    'El contexto para generar el documento está incompleto. '
                    'Faltan datos de alumno, especialidad, facultad, universidad o fecha.'
                )
            
            logger.debug(f'Obteniendo generador para tipo: {tipo}')
            documento = obtener_tipo_documento(tipo)
            if not documento:
                logger.error(f'Tipo de documento no soportado: {tipo}')
                raise DocumentGenerationException(tipo, f'Tipo de documento no soportado: {tipo}')
            
            if tipo in ('odt', 'docx'):
                plantilla = 'certificado_plantilla'
            else:
                plantilla = 'certificado_pdf'
            
            logger.debug(f'Usando plantilla: {plantilla}')
            
            logger.info(f'Generando documento {tipo} con plantilla {plantilla}')
            resultado = documento.generar(
                carpeta='certificado',
                plantilla=plantilla,
                context=context
            )
            
            if not resultado:
                logger.error('El generador retornó None')
                raise DocumentGenerationException(tipo, 'Error al generar el documento')
            
            logger.info(f'Certificado generado exitosamente para alumno {id}')
            return resultado

            
        except (AlumnoNotFoundException, DocumentGenerationException):
            # Re-lanzar excepciones personalizadas sin modificar
            logger.error(f'Error controlado al generar certificado: {str(e)}')
            raise
        except Exception as e:
            # Convertir excepciones inesperadas en DocumentGenerationException
            logger.exception(f'Error inesperado al generar certificado para alumno {id}: {str(e)}')
            raise DocumentGenerationException(tipo, f'Error inesperado al generar certificado: {str(e)}')    

         
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
        """
        Busca alumno por ID usando repositorio con cache Redis.
        
        Implementa patrón Repository para:
        1. Buscar en cache Redis primero (cache hit = respuesta instantánea)
        2. Si no está en cache, llamar al microservicio de alumnos
        3. Guardar resultado en cache con TTL
        4. Retry automático en caso de fallo (implementado en el repositorio)
        
        Args:
            id: ID del alumno a buscar
            
        Returns:
            Alumno: Objeto con datos completos del alumno
            
        Raises:
            AlumnoNotFoundException: Si el alumno no existe (404)
            ServiceUnavailableException: Si el MS de alumnos no responde
        """
        # Usar mock data mientras no existe el microservicio de alumnos
        USE_MOCK = os.getenv('USE_MOCK_DATA', 'true').lower() == 'true'
        
        if USE_MOCK:
            logger.debug(f'Usando datos mock para alumno {id}')
            alumno_mock = CertificateService._get_mock_alumno(id)
            if alumno_mock is None:
                raise AlumnoNotFoundException(f'Alumno con ID {id} no encontrado')
            return alumno_mock
        
        # Usar repositorio con cache Redis + retry automático
        logger.debug(f'Buscando alumno {id} en repositorio (cache + HTTP)')
        repo = AlumnoRepository()
        
        try:
            alumno = repo.get_alumno_by_id(id)
            
            if alumno is None:
                logger.warning(f'Alumno {id} no encontrado en el microservicio')
                raise AlumnoNotFoundException(id)
            
            logger.debug(f'Alumno {id} obtenido exitosamente')
            return alumno
            
        except AlumnoNotFoundException:
            raise
        except Exception as e:
            logger.error(f'Error al buscar alumno {id}: {str(e)}')
            raise ServiceUnavailableException('alumnos', str(e))
    
    @staticmethod
    def _enriquecer_especialidad(alumno: Alumno) -> Alumno:
        """
        Enriquece el objeto alumno con datos completos de especialidad.
        
        Si el alumno solo tiene especialidad.id (sin nombre, facultad, etc.),
        llama al EspecialidadRepository para obtener datos completos desde
        el microservicio de gestión académica.
        
        Flujo:
        1. Si USE_MOCK=true → Retorna sin cambios (mock ya tiene datos completos)
        2. Si especialidad tiene 'nombre' → Ya está completa, retorna sin cambios
        3. Si especialidad solo tiene 'id' → Llama a MS académica para enriquecer
        
        Args:
            alumno: Objeto alumno que puede tener especialidad parcial o completa
            
        Returns:
            Alumno con especialidad completa enriquecida
            
        Raises:
            EspecialidadNotFoundException: Si la especialidad no existe
            ServiceUnavailableException: Si el MS académica no responde
            DocumentGenerationException: Si no hay datos de especialidad
        """
        USE_MOCK = os.getenv('USE_MOCK_DATA', 'true').lower() == 'true'
        
        if USE_MOCK:
            logger.debug('Usando mock: especialidad ya incluida completa')
            return alumno
        
        # Verificar si especialidad existe
        if not hasattr(alumno, 'especialidad') or alumno.especialidad is None:
            logger.error(f'Alumno {alumno.id} no tiene datos de especialidad')
            raise DocumentGenerationException(
                'certificado',
                f'El alumno {alumno.id} no tiene información de especialidad'
            )
        
        # Verificar si la especialidad ya tiene datos completos
        if hasattr(alumno.especialidad, 'nombre') and alumno.especialidad.nombre:
            logger.debug('Especialidad completa ya presente en el alumno')
            return alumno
        
        # Si solo tiene ID, obtener especialidad completa del MS académica
        if hasattr(alumno.especialidad, 'id') and alumno.especialidad.id:
            especialidad_id = alumno.especialidad.id
            logger.info(f'Enriqueciendo especialidad {especialidad_id} desde MS académica')
            
            repo = EspecialidadRepository()
            
            try:
                especialidad_completa = repo.get_especialidad_by_id(especialidad_id)
                
                # Reemplazar especialidad parcial con datos completos
                alumno.especialidad = especialidad_completa
                logger.info(f'Especialidad {especialidad_id} enriquecida: {especialidad_completa.nombre}')
                return alumno
                
            except EspecialidadNotFoundException:
                logger.error(f'Especialidad {especialidad_id} no encontrada en MS académica')
                raise
            except ServiceUnavailableException:
                logger.error(f'MS académica no disponible al buscar especialidad {especialidad_id}')
                raise
            except Exception as e:
                logger.error(f'Error inesperado al obtener especialidad {especialidad_id}: {str(e)}')
                raise ServiceUnavailableException('academica', str(e))
        
        # Si llegamos aquí, especialidad no tiene ID ni nombre
        logger.error(f'Alumno {alumno.id} tiene especialidad inválida (sin ID ni nombre)')
        raise DocumentGenerationException(
            'certificado',
            f'El alumno {alumno.id} tiene especialidad inválida'
        )
    
    @staticmethod
    def _get_mock_alumno(id: int) -> Alumno:
        """Retorna datos mock de un alumno para testing"""
        from app.models import Especialidad, TipoDocumento, Facultad, Universidad
        
        # Base de datos mock de alumnos para pruebas de rendimiento
        alumnos_mock = {
            1: {"nombre": "MARIANO PABLO CRISTOBAL", "apellido": "SOSA", "doc": "42532964", "legajo": "12652", "especialidad": "ISI"},
            2: {"nombre": "JUAN CARLOS", "apellido": "PÉREZ", "doc": "38456789", "legajo": "12345", "especialidad": "ISI"},
            3: {"nombre": "MARÍA FERNANDA", "apellido": "GONZÁLEZ", "doc": "40123456", "legajo": "12678", "especialidad": "IEM"},
            5: {"nombre": "ROBERTO LUIS", "apellido": "MARTÍNEZ", "doc": "35987654", "legajo": "11890", "especialidad": "ISI"},
            8: {"nombre": "ANA SOFÍA", "apellido": "RODRÍGUEZ", "doc": "41234567", "legajo": "13001", "especialidad": "IQ"},
            13: {"nombre": "DIEGO ALBERTO", "apellido": "FERNÁNDEZ", "doc": "39876543", "legajo": "12789", "especialidad": "IC"},
            21: {"nombre": "LAURA BEATRIZ", "apellido": "LÓPEZ", "doc": "43210987", "legajo": "13456", "especialidad": "ISI"},
            34: {"nombre": "CARLOS EDUARDO", "apellido": "RAMÍREZ", "doc": "37654321", "legajo": "11567", "especialidad": "IEM"},
        }
        
        # Si el ID no está en mock, retornar None (404)
        if id not in alumnos_mock:
            return None
        
        datos = alumnos_mock[id]
        
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
        
        # Especialidades según código
        especialidades_map = {
            "ISI": {"id": 1, "nombre": "Ingeniería en Sistemas de Información"},
            "IEM": {"id": 2, "nombre": "Ingeniería Electromecánica"},
            "IQ": {"id": 3, "nombre": "Ingeniería Química"},
            "IC": {"id": 4, "nombre": "Ingeniería Civil"}
        }
        
        esp_code = datos["especialidad"]
        esp_data = especialidades_map.get(esp_code, especialidades_map["ISI"])
        
        especialidad = Especialidad()
        especialidad.id = esp_data["id"]
        especialidad.nombre = esp_data["nombre"]
        especialidad.letra = esp_code
        especialidad.observacion = "Especialidad de grado"
        especialidad.facultad = facultad
        
        # Mock de TipoDocumento
        tipo_documento = TipoDocumento()
        tipo_documento.id = 1
        tipo_documento.nombre = "DNI"
        
        # Mock de Alumno
        alumno = Alumno()
        alumno.id = id
        alumno.nombre = datos["nombre"]
        alumno.apellido = datos["apellido"]
        alumno.nrodocumento = datos["doc"]
        alumno.legajo = datos["legajo"]
        alumno.tipo_documento = tipo_documento
        alumno.especialidad = especialidad
        
        return alumno
    