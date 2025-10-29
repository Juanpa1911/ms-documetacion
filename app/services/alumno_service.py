
from app.services.certificate_service import CertificateService

class AlumnoService:

    @staticmethod
    def generar_certificado_alumno_regular(id: int, tipo: str):
        return CertificateService.generar_certificado_alumno_regular(id, tipo)
