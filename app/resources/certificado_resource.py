from flask import Blueprint, send_file, jsonify
from app.services import AlumnoService
from app.exceptions import DocumentGenerationException
import logging

logger = logging.getLogger(__name__)
certificado_bp = Blueprint('certificado', __name__)


def _validar_id_alumno(alumno_id: int) -> None:
    """Valida que el ID del alumno sea válido (mayor a 0)"""
    if alumno_id <= 0:
        logger.warning(f"ID de alumno inválido: {alumno_id}")
        raise DocumentGenerationException(
            f"El ID del alumno debe ser un número positivo. Recibido: {alumno_id}"
        )


@certificado_bp.route('/certificado/<int:id>/pdf', methods=['GET'])
def certificado_en_pdf(id: int):
    """Genera certificado de alumno regular en formato PDF"""
    try:
        _validar_id_alumno(id)
        logger.info(f"Generando certificado PDF para alumno ID: {id}")
        pdf_io = AlumnoService.generar_certificado_alumno_regular(id, 'pdf')
        return send_file(pdf_io, mimetype='application/pdf', as_attachment=False)
    except DocumentGenerationException:
        raise  # Re-lanzar para que lo maneje el error handler
    except Exception as e:
        logger.error(f"Error inesperado generando PDF para alumno {id}: {str(e)}")
        raise

@certificado_bp.route('/certificado/<int:id>/odt', methods=['GET'])
def certificado_en_odt(id: int):
    """Genera certificado de alumno regular en formato ODT"""
    try:
        _validar_id_alumno(id)
        logger.info(f"Generando certificado ODT para alumno ID: {id}")
        odt_io = AlumnoService.generar_certificado_alumno_regular(id, 'odt')
        
        return send_file(
            odt_io,
            mimetype='application/vnd.oasis.opendocument.text',
            as_attachment=True,
            download_name=f"certificado_alumno_{id}.odt"
        )
    except DocumentGenerationException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado generando ODT para alumno {id}: {str(e)}")
        raise

@certificado_bp.route('/certificado/<int:id>/docx', methods=['GET'])
def reporte_en_docx(id: int):
    """Genera certificado de alumno regular en formato DOCX"""
    try:
        _validar_id_alumno(id)
        logger.info(f"Generando certificado DOCX para alumno ID: {id}")
        docx_io = AlumnoService.generar_certificado_alumno_regular(id, 'docx')
        
        return send_file(
            docx_io,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=f"certificado_alumno_{id}.docx"
        )
    except DocumentGenerationException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado generando DOCX para alumno {id}: {str(e)}")
        raise