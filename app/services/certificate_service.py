import datetime
import requests
import logging
from io import BytesIO
from flask import current_app
from app.mapping import AlumnoMapping
from app.models import Alumno
from app.services.documentos_office_service import obtener_tipo_documento
from app.services.redis_service import RedisService

logger = logging.getLogger(__name__)

class CertificateService:
    @staticmethod
    def generar_certificado_alumno_regular(id: int, tipo: str) -> BytesIO:
        alumno = CertificateService._buscar_alumno_por_id(id)
        if not alumno:
            return None
        
        context = CertificateService._obtener_contexto_alumno(alumno)
        documento = obtener_tipo_documento(tipo)
        if not documento:
            return None
            
        if tipo in ('odt', 'docx'):
            plantilla = 'certificado_plantilla'
        else:
            plantilla = 'certificado_pdf'

        return documento.generar(
            carpeta='certificado',
            plantilla=plantilla,
            context=context
        )
    
    @staticmethod
    def _obtener_contexto_alumno(alumno: Alumno) -> dict:
        return {
            "alumno": alumno,
            "especialidad": alumno.especialidad,
            "facultad": alumno.especialidad.facultad,
            "fecha": CertificateService._obtener_fechaactual()
        }
    
    @staticmethod
    def _obtener_fechaactual():
        fecha_actual = datetime.datetime.now()
        fecha_str = fecha_actual.strftime('%d de %B de %Y')
        return fecha_str
    
    @staticmethod
    def _buscar_alumno_por_id(id: int) -> Alumno:
        # Intentar obtener del caché primero
        cache_key = f"alumno:{id}"
        cached_data = RedisService.get(cache_key)
        
        if cached_data:
            logger.info(f"Alumno {id} obtenido desde caché")
            alumno_mapping = AlumnoMapping()
            return alumno_mapping.load(cached_data)
        
        # Si no está en caché, consultar al microservicio
        logger.info(f"Alumno {id} no está en caché, consultando microservicio")
        URL_ALUMNOS = current_app.config.get('ALUMNO_SERVICE_URL')
        alumno_mapping = AlumnoMapping()
        
        r = requests.get(f'{URL_ALUMNOS}/alumnos/{id}')
        if r.status_code == 200:
            data = r.json()
            result = alumno_mapping.load(data)
            
            # Guardar en caché para futuras consultas
            ttl = current_app.config.get('CACHE_ALUMNO_TTL', 300)
            RedisService.set(cache_key, data, ttl)
            logger.info(f"Alumno {id} almacenado en caché por {ttl}s")
            
            return result
        else:
            raise Exception(f'Error al obtener el alumno con id {id}: {r.status_code}')
    
