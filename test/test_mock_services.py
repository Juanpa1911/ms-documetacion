"""
Servicios mock para probar ms-documentacion sin necesitar ms-alumnos y ms-especialidades
"""
from flask import Flask, jsonify
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Mock de ms-alumnos
app_alumnos = Flask(__name__ + '_alumnos')

@app_alumnos.route('/api/v1/alumnos/<int:id>', methods=['GET'])
def get_alumno(id):
    alumnos = {
        1: {
            "id": 1,
            "nombre": "Juan",
            "apellido": "Pérez",
            "nrodocumento": "12345678",
            "tipo_documento": {
                "id": 1,
                "nombre": "DNI"
            },
            "especialidad": {
                "id": 1,
                "nombre": "Ingeniería en Sistemas",
                "letra": "A",
                "observacion": "Carrera de grado",
                "facultad": "Facultad de Ingeniería"
            }
        },
        2: {
            "id": 2,
            "nombre": "María",
            "apellido": "González",
            "nrodocumento": "87654321",
            "tipo_documento": {
                "id": 1,
                "nombre": "DNI"
            },
            "especialidad": {
                "id": 2,
                "nombre": "Licenciatura en Informática",
                "letra": "B",
                "observacion": "Carrera de grado",
                "facultad": "Facultad de Ciencias Exactas"
            }
        }
    }
    
    if id in alumnos:
        logger.info(f"Alumno {id} solicitado: {alumnos[id]['nombre']} {alumnos[id]['apellido']}")
        return jsonify(alumnos[id]), 200
    logger.warning(f"Alumno {id} no encontrado")
    return jsonify({"error": "Alumno no encontrado"}), 404

# Mock de ms-especialidades
app_especialidades = Flask(__name__ + '_especialidades')

@app_especialidades.route('/api/v1/especialidades/<int:id>', methods=['GET'])
def get_especialidad(id):
    especialidades = {
        1: {
            "id": 1,
            "nombre": "Ingeniería en Sistemas",
            "letra": "A",
            "observacion": "Carrera de grado",
            "facultad": "Facultad de Ingeniería"
        },
        2: {
            "id": 2,
            "nombre": "Licenciatura en Informática",
            "letra": "B",
            "observacion": "Carrera de grado",
            "facultad": "Facultad de Ciencias Exactas"
        }
    }
    
    if id in especialidades:
        logger.info(f"Especialidad {id} solicitada: {especialidades[id]['nombre']}")
        return jsonify(especialidades[id]), 200
    logger.warning(f"Especialidad {id} no encontrada")
    return jsonify({"error": "Especialidad no encontrada"}), 404

if __name__ == '__main__':
    print("=" * 60)
    print("SERVICIOS MOCK INICIADOS")
    print("=" * 60)
    print("Mock ms-alumnos: http://localhost:5001/api/v1/alumnos/{id}")
    print("Mock ms-especialidades: http://localhost:5002/api/v1/especialidades/{id}")
    print("=" * 60)
    print("\nAlumnos disponibles:")
    print("  - ID 1: Juan Pérez (Ingeniería en Sistemas)")
    print("  - ID 2: María González (Licenciatura en Informática)")
    print("=" * 60)
    
    # Ejecutar ambos servicios en puertos diferentes
    import threading
    from werkzeug.serving import run_simple
    
    def run_alumnos():
        logger.info("Iniciando mock de ms-alumnos en puerto 5001")
        run_simple('localhost', 5001, app_alumnos, use_reloader=False, use_debugger=False)
    
    def run_especialidades():
        logger.info("Iniciando mock de ms-especialidades en puerto 5002")
        run_simple('localhost', 5002, app_especialidades, use_reloader=False, use_debugger=False)
    
    t1 = threading.Thread(target=run_alumnos, daemon=True)
    t2 = threading.Thread(target=run_especialidades, daemon=True)
    
    t1.start()
    t2.start()
    
    print("\n✓ Servicios mock ejecutándose...")
    print("Presiona Ctrl+C para detener\n")
    
    try:
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        print("\n\nServicios mock detenidos")
