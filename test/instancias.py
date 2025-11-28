from datetime import datetime
from datetime import date
from app.models import (
    Alumno)

from app.services import (
    AlumnoService)

from app.services.tipo_doc_service import TipoDocumentoService
def nuevoAlumno(apellido="Pérez", nombre="Juan", nro_documento="30123456", tipo_documento=None, fecha_nacimiento="1990-01-15", sexo="M", nro_legajo=12345, fecha_ingreso=date.today()):
    alumno = Alumno()
    alumno.apellido = apellido
    alumno.nombre = nombre
    alumno.nro_documento = nro_documento
    alumno.tipo_documento = nuevoTipoDocumento()
    alumno.fecha_nacimiento = fecha_nacimiento
    alumno.sexo = sexo
    alumno.nro_legajo = nro_legajo
    alumno.fecha_ingreso = fecha_ingreso
    return alumno