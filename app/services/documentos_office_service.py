from abc import ABC, abstractmethod
from io import BytesIO
import os
import logging
import tempfile
from flask import current_app, render_template
from python_odt_template import ODTTemplate
from python_odt_template.jinja import get_odt_renderer
from docxtpl import DocxTemplate
import jinja2 

# Configurar logger para este módulo
logger = logging.getLogger(__name__)


class Document(ABC):
    """
    Clase abstracta base para generación de documentos.
    
    Define la interfaz común que deben implementar todos los generadores
    de documentos (PDF, DOCX, ODT).
    """
    
    @staticmethod
    @abstractmethod
    def generar(carpeta: str, plantilla: str, context: dict) -> BytesIO:
        """
        Genera un documento usando la plantilla y contexto especificados.
        
        Args:
            carpeta: Subcarpeta dentro de templates/ donde buscar la plantilla
            plantilla: Nombre base de la plantilla (sin extensión)
            context: Diccionario con datos para renderizar la plantilla
            
        Returns:
            BytesIO con el contenido binario del documento generado
            
        Raises:
            FileNotFoundError: Si la plantilla no existe
            Exception: Si falla la generación del documento
        """
        pass


class PDFDocument(Document):
    """
    Generador de documentos PDF usando WeasyPrint.
    
    Renderiza plantillas HTML con Jinja2 y las convierte a PDF usando WeasyPrint.
    Soporta CSS, imágenes y tipografías personalizadas.
    """
    
    @staticmethod
    # pyrefly: ignore  # bad-override
    def generar(carpeta: str, plantilla: str, context: dict) -> BytesIO:
        """
        Genera un PDF a partir de una plantilla HTML.
        
        Proceso:
        1. Construye base_url con protocolo file:/// para recursos locales
        2. Renderiza HTML con Jinja2 usando el contexto
        3. Convierte HTML a PDF con WeasyPrint
        4. Retorna BytesIO con el PDF generado
        
        Args:
            carpeta: Subcarpeta en templates/ (ej: 'certificado')
            plantilla: Nombre de plantilla sin extensión (ej: 'certificado_pdf')
            context: Datos para renderizar (alumno, especialidad, etc.)
            
        Returns:
            BytesIO con el PDF generado
        """
        logger.debug(f'Generando PDF desde {carpeta}/{plantilla}.html')
        
        # Construir base_url file:/// para que WeasyPrint pueda abrir archivos locales
        base_path = current_app.root_path.replace('\\', '/')
        base_url = f"file:///{base_path}"
        logger.debug(f'Base URL configurada: {base_url}')

        render_context = dict(context or {})
        render_context.update({"url_base": base_url})

        logger.debug('Renderizando plantilla HTML con Jinja2')
        html_string = render_template(f"{carpeta}/{plantilla}.html", **render_context)
        
        logger.debug('Convirtiendo HTML a PDF con WeasyPrint')
        # Lazy import: solo importar WeasyPrint cuando realmente se necesita
        # Esto evita problemas en tests y cuando las librerías GTK no están disponibles
        try:
            from weasyprint import HTML
        except (OSError, ImportError) as e:
            logger.error(f"Error al importar WeasyPrint: {e}")
            raise ImportError(
                "WeasyPrint no está disponible. Asegúrese de que GTK esté instalado correctamente. "
                "En Windows, puede instalar GTK desde https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer"
            ) from e
        
        bytes_data = HTML(string=html_string, base_url=base_url).write_pdf()
        pdf_io = BytesIO(bytes_data)
        
        logger.info(f'PDF generado exitosamente: {len(bytes_data)} bytes')
        return pdf_io


class ODTDocument(Document):
    """
    Generador de documentos ODT (OpenDocument Text) usando python-odt-template.
    
    Compatible con LibreOffice, OpenOffice y Microsoft Word (con soporte ODT).
    Soporta campos dinámicos, imágenes y formateo avanzado.
    """
    
    @staticmethod
    # pyrefly: ignore  # bad-override
    def generar(carpeta: str, plantilla: str, context: dict) -> BytesIO:
        """
        Genera un ODT a partir de una plantilla .odt con marcadores Jinja2.
        
        Proceso:
        1. Localiza plantilla en templates/carpeta/plantilla.odt
        2. Configura media_path para resolución de imágenes en static/
        3. Renderiza plantilla con contexto usando python-odt-template
        4. Empaqueta resultado en archivo temporal
        5. Lee contenido y retorna BytesIO
        
        Args:
            carpeta: Subcarpeta en templates/ (ej: 'certificado')
            plantilla: Nombre sin extensión (ej: 'certificado_plantilla')
            context: Datos para renderizar
            
        Returns:
            BytesIO con el documento ODT generado
            
        Note:
            Usa archivos temporales durante generación (se eliminan automáticamente)
        """
        logger.debug(f'Generando ODT desde {carpeta}/{plantilla}.odt')
        
        templates_root = os.path.join(current_app.root_path, current_app.template_folder)
        path_template = os.path.join(templates_root, carpeta, f"{plantilla}.odt")
        logger.debug(f'Ruta plantilla: {path_template}')

        # media path para que el renderer encuentre imágenes dentro de static
        media_path = current_app.static_folder
        logger.debug(f'Media path para imágenes: {media_path}')
        odt_renderer = get_odt_renderer(media_path=media_path)

        odt_io = BytesIO()
        with tempfile.NamedTemporaryFile(suffix='.odt', delete=False) as temp_file:
            temp_path = temp_file.name
        
        logger.debug('Renderizando plantilla ODT')
        with ODTTemplate(path_template) as template:
            odt_renderer.render(template, context=context)
            template.pack(temp_path)
            with open(temp_path, 'rb') as f:
                content = f.read()
                odt_io.write(content)
                logger.info(f'ODT generado exitosamente: {len(content)} bytes')

        os.unlink(temp_path)
        odt_io.seek(0)
        return odt_io


class DOCXDocument(Document):
    """
    Generador de documentos DOCX (Microsoft Word) usando docxtpl.
    
    Compatible con Microsoft Word, LibreOffice y Google Docs.
    Soporta tablas, imágenes, estilos y formateo complejo.
    """
    
    @staticmethod
    # pyrefly: ignore  # bad-override
    def generar(carpeta: str, plantilla: str, context: dict) -> BytesIO:
        """
        Genera un DOCX a partir de una plantilla .docx con marcadores Jinja2.
        
        Proceso:
        1. Localiza plantilla en templates/carpeta/plantilla.docx
        2. Crea entorno Jinja2 para renderizado
        3. Agrega url_base al contexto para recursos locales
        4. Renderiza usando docxtpl
        5. Guarda en archivo temporal y retorna BytesIO
        
        Args:
            carpeta: Subcarpeta en templates/ (ej: 'certificado')
            plantilla: Nombre sin extensión (ej: 'certificado_plantilla')
            context: Datos para renderizar
            
        Returns:
            BytesIO con el documento DOCX generado
            
        Note:
            La plantilla debe ser un .docx válido con marcadores Jinja2
            como {{ alumno.nombre }} o {% for item in lista %}
        """
        logger.debug(f'Generando DOCX desde {carpeta}/{plantilla}.docx')
        
        templates_root = os.path.join(current_app.root_path, current_app.template_folder)
        path_template = os.path.join(templates_root, carpeta, f"{plantilla}.docx")
        logger.debug(f'Ruta plantilla: {path_template}')

        doc = DocxTemplate(path_template)

        docx_io = BytesIO()
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_path = temp_file.name

        jinja_env = jinja2.Environment()
        render_context = dict(context or {})
        base_path = current_app.root_path.replace('\\', '/')
        render_context.update({"url_base": "file:///" + base_path})
        
        logger.debug('Renderizando plantilla DOCX con Jinja2')
        doc.render(render_context, jinja_env)
        doc.save(temp_path)
        
        with open(temp_path, 'rb') as f:
            content = f.read()
            docx_io.write(content)
            logger.info(f'DOCX generado exitosamente: {len(content)} bytes')

        os.unlink(temp_path)
        docx_io.seek(0)
        return docx_io


def obtener_tipo_documento(tipo: str) -> Document:
    """
    Factory function que retorna el generador de documentos apropiado.
    
    Args:
        tipo: Tipo de documento deseado ('pdf', 'odt', 'docx')
        
    Returns:
        Clase generadora correspondiente (PDFDocument, ODTDocument, DOCXDocument)
        None si el tipo no es soportado
        
    Examples:
        >>> generador = obtener_tipo_documento('pdf')
        >>> generador.generar('certificado', 'certificado_pdf', context)
    """
    logger.debug(f'Solicitando generador para tipo: {tipo}')
    
    tipos = {
        'pdf': PDFDocument,
        'odt': ODTDocument,
        'docx': DOCXDocument,
    }
    
    generador = tipos.get(tipo)
    if not generador:
        logger.warning(f'Tipo de documento no soportado: {tipo}. Tipos válidos: {list(tipos.keys())}')
    
    return generador
