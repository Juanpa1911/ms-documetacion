from marshmallow import Schema, fields, post_load, validate
from app.models import Alumno, Especialidad
from .tipodocumento_mapping import TipoDocumentoMapping
from .especialidad_mapping import EspecialidadMapping

class AlumnoMapping(Schema):
    """
    Mapping para deserializar alumno desde JSON.
    
    Soporta dos formatos:
    1. especialidad completa (nested): {"especialidad": {"id": 1, "nombre": "ISI", ...}}
    2. solo especialidad_id: {"especialidad_id": 1}
    """
    id = fields.Integer()
    nombre = fields.String(required=True, validate=validate.Length(min=1, max=50))
    apellido = fields.String(required=True, validate=validate.Length(min=1, max=50))
    nrodocumento = fields.String(required=True, validate=validate.Length(min=1, max=50))
    legajo = fields.String(required=True, validate=validate.Length(min=1, max=50))
    tipo_documento = fields.Nested(TipoDocumentoMapping, required=True)
    
    # Soportar especialidad completa (nested)
    especialidad = fields.Nested(EspecialidadMapping, required=False, allow_none=True)
    
    # Soportar solo especialidad_id (para MS que solo devuelven el ID)
    especialidad_id = fields.Integer(required=False, allow_none=True)

    @post_load
    def nuevo_alumno(self, data, **kwargs):
        alumno = Alumno()
        alumno.id = data.get('id')
        alumno.nombre = data.get('nombre')
        alumno.apellido = data.get('apellido')
        alumno.nrodocumento = data.get('nrodocumento')
        alumno.legajo = data.get('legajo')
        alumno.tipo_documento = data.get('tipo_documento')
        alumno.especialidad = data.get('especialidad')
        # Si solo viene especialidad_id, lo asignamos también
        if 'especialidad_id' in data and not data.get('especialidad'):
            alumno.especialidad_id = data.get('especialidad_id')
        return alumno
