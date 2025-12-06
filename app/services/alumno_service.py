from typing import Optional
from app.services.certificate_service import CertificateService

class AlumnoService:
    """
    Servicio de aplicación para operaciones de alumnos.
    
    Actúa como fachada para operaciones relacionadas con alumnos,
    delegando a servicios específicos.
    """
    
    def __init__(self, certificate_service: Optional[CertificateService] = None):
        """
        Constructor con inyección de dependencias.
        
        Args:
            certificate_service: Servicio de certificados (opcional)
        """
        self.certificate_service = certificate_service or CertificateService()

    def generar_certificado_alumno_regular(self, id: int, tipo: str):
        """
        Genera un certificado de alumno regular en el formato especificado.
        
        Args:
            id: ID del alumno
            tipo: Formato del certificado (pdf, docx, odt)
            
        Returns:
            BytesIO con el documento generado
        """
        return self.certificate_service.generar_certificado_alumno_regular(id, tipo)
