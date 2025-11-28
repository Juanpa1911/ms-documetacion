from app import db
from app.models import Alumno

class AlumnoRepository:
    
    @staticmethod
    def crear_alumno(alumno):
        """Crea un nuevo alumno en la base de datos"""
        db.session.add(alumno)
        db.session.commit()
        return alumno
    
    @staticmethod
    def buscar_todos():
        """Obtiene todos los alumnos"""
        return Alumno.query.all()
    
    @staticmethod
    def buscar_alumno_id(alumno_id):
        """Obtiene un alumno por su ID"""
        return Alumno.query.get(alumno_id)
    
    @staticmethod
    def buscar_alumno_legajo(nro_legajo):
        """Obtiene un alumno por su número de legajo"""
        return Alumno.query.filter_by(nro_legajo=nro_legajo).first()
    
    @staticmethod
    def buscar_alumno_documento(nro_documento):
        """Obtiene un alumno por su número de documento"""
        return Alumno.query.filter_by(nro_documento=nro_documento).first()
    
    @staticmethod
    def actualizar_alumno(alumno):
        """Actualiza un alumno existente"""
        db.session.commit()
        return alumno
    
    @staticmethod
    def borrar_alumno_id(alumno_id):
        """Elimina un alumno por su ID"""
        alumno = AlumnoRepository.buscar_alumno_id(alumno_id)
        if alumno:
            db.session.delete(alumno)
            db.session.commit()
        return True