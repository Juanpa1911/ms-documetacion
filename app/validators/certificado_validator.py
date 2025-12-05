from flask import jsonify, request
from functools import wraps

from marshmallow import ValidationError

def validate_routes_with(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data, errors = schema().load(request.json)
            except ValidationError as err:
                return jsonify(err.messages), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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