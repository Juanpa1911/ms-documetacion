from marshmallow import fields, Schema, post_load, validate
from app.models import Especialidad


class EspecialidadMapping(Schema):
    id = fields.Integer()
    nombre = fields.String(required=True, validate=validate.Length(min=1, max=100))
    letra = fields.String(required=True, validate=validate.Length(equal=1))
    observacion = fields.String(validate=validate.Length(max=255), allow_none=True)
    facultad = fields.String(required=True)

    @post_load
    def nueva_especialidad(self, data, **kwargs):
        esp = Especialidad()
        esp.id = data.get('id')
        esp.nombre = data.get('nombre')
        esp.letra = data.get('letra')
        esp.observacion = data.get('observacion')
        esp.facultad = data.get('facultad')
        return esp