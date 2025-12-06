from flask import jsonify, request
from functools import wraps
from marshmallow import ValidationError

def validate_with(schema, context=None):
    try:
        # Instancia del schema con
        schema_instance = schema(context=context)

        # Marshmallow 3: si no es válido → lanza ValidationError
        data = schema_instance.load(request.json)
        return data  # data válida

    except ValidationError as err:
        # Retorna error 400 con el detalle de errores
        return jsonify(err.messages), 400