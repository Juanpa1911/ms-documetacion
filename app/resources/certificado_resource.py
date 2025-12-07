from flask import Blueprint, send_file, jsonify
from app.services import AlumnoService
from app.exceptions import DocumentGenerationException
from app.validators import validar_id_alumno
import logging

logger = logging.getLogger(__name__)
certificado_bp = Blueprint('certificado', __name__)

# Instancia única del servicio (inicialización lazy)
_alumno_service = None

def get_alumno_service():
    """Obtiene la instancia del servicio (lazy initialization)."""
    global _alumno_service
    if _alumno_service is None:
        _alumno_service = AlumnoService()
    return _alumno_service

# Configuración de formatos soportados
FORMATOS_SOPORTADOS = {
    'pdf': {
        'mimetype': 'application/pdf',
        'as_attachment': False,
        'download_name': None
    },
    'odt': {
        'mimetype': 'application/vnd.oasis.opendocument.text',
        'as_attachment': True,
        'download_name': 'certificado_alumno_{id}.odt'
    },
    'docx': {
        'mimetype': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'as_attachment': True,
        'download_name': 'certificado_alumno_{id}.docx'
    }
}


def _generar_certificado(alumno_id: int, formato: str):
    """Función genérica para generar certificados en cualquier formato."""
    if not validar_id_alumno(alumno_id):
        logger.warning(f"ID de alumno inválido: {alumno_id}")
        raise DocumentGenerationException(
            formato,
            f"El ID del alumno debe ser un número positivo. Recibido: {alumno_id}"
        )
    
    logger.info(f"Generando certificado {formato.upper()} para alumno ID: {alumno_id}")
    documento = get_alumno_service().generar_certificado_alumno_regular(alumno_id, formato)
    
    config = FORMATOS_SOPORTADOS[formato]
    download_name = config['download_name'].format(id=alumno_id) if config['download_name'] else None
    
    return send_file(
        documento,
        mimetype=config['mimetype'],
        as_attachment=config['as_attachment'],
        download_name=download_name
    )


@certificado_bp.route('/certificado/<int:id>/pdf', methods=['GET'])
def certificado_en_pdf(id: int):
    """Genera certificado de alumno regular en formato PDF"""
    try:
        return _generar_certificado(id, 'pdf')
    except DocumentGenerationException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado generando PDF para alumno {id}: {str(e)}")
        raise


@certificado_bp.route('/certificado/<int:id>/odt', methods=['GET'])
def certificado_en_odt(id: int):
    """Genera certificado de alumno regular en formato ODT"""
    try:
        return _generar_certificado(id, 'odt')
    except DocumentGenerationException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado generando ODT para alumno {id}: {str(e)}")
        raise


@certificado_bp.route('/certificado/<int:id>/docx', methods=['GET'])
def reporte_en_docx(id: int):
    """Genera certificado de alumno regular en formato DOCX"""
    try:
        return _generar_certificado(id, 'docx')
    except DocumentGenerationException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado generando DOCX para alumno {id}: {str(e)}")
        raise