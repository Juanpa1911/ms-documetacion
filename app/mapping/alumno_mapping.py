from marshmallow import Schema, fields, post_load, validate
from app.models import Alumno
from .tipodocumento_mapping import TipoDocumentoMapping
from .especialidad_mapping import EspecialidadMapping

class AlumnoMapping(Schema):
    id = fields.Integer()
    nombre = fields.String(required=True, validate=validate.Length(min=1, max=50))
    apellido = fields.String(required=True, validate=validate.Length(min=1, max=50))
    nrodocumento = fields.String(required=True, validate=validate.Length(min=1, max=50))
    tipo_documento = fields.Nested(TipoDocumentoMapping, required=True)
    especialidad = fields.Nested(EspecialidadMapping, required=True)

    @post_load
    def nuevo_alumno(self, data, **kwargs):
        return Alumno(**data)