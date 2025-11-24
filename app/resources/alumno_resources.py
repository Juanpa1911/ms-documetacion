from flask import jsonify, Blueprint, request
from app.services import AlumnoService
from app.mapping.alumno_mapping import AlumnoMapping

alumno_bp = Blueprint('alumno', __name__)
alumno_mapping = AlumnoMapping()

@alumno_bp.route('/alumno', methods=['GET'])
def buscar_todos():
    alumnos = AlumnoService.buscar_todos()
    return alumno_mapping.dump(alumnos, many=True), 200

@alumno_bp.route('/alumno/<hashid:id>', methods=['GET'])
def buscar_alumno_id(id):
    alumno = AlumnoService.buscar_alumno_id(id)
    if alumno:
        return alumno_mapping.dump(alumno), 200
    return jsonify({"message": "Alumno no encontrado"}), 404

@alumno_bp.route('/alumno/legajo/<int:nro_legajo>', methods=['GET'])
def buscar_alumno_legajo(nro_legajo):
    alumno = AlumnoService.buscar_alumno_legajo(nro_legajo)
    if alumno:
        return alumno_mapping.dump(alumno), 200
    return jsonify({"message": "Alumno no encontrado"}), 404

@alumno_bp.route('/alumno/documento/<string:nro_documento>', methods=['GET'])
def buscar_alumno_doc(nro_documento):
    alumno = AlumnoService.buscar_alumno_doc(nro_documento)
    if alumno:
        return alumno_mapping.dump(alumno), 200
    return jsonify({"message": "Alumno no encontrado"}), 404

@alumno_bp.route('/alumno', methods=['POST'])
def crear_alumno():
    data = request.get_json()
    alumno = alumno_mapping.load(data)
    AlumnoService.crear_alumno(alumno)
    return alumno_mapping.dump(alumno), 201

@alumno_bp.route('/alumno/<hashid:id>', methods=['PUT'])
def actualizar_alumno(id):
    data = request.get_json()
    alumno = alumno_mapping.load(data)
    AlumnoService.actualizar_alumno(alumno)
    if alumno:
        return alumno_mapping.dump(alumno), 200
    return jsonify({"message": "Alumno no encontrado"}), 404

@alumno_bp.route('/alumno/<hashid:id>', methods=['DELETE'])
def eliminar_alumno(id):
    alumno = AlumnoService.borrar_alumno_id(id)
    if alumno:
        return jsonify({"message": "Alumno eliminado"}), 200
    return jsonify({"message": "Alumno no encontrado"}), 404   


