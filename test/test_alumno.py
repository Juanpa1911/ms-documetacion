import os
import unittest
from datetime import date
from flask import current_app
from app import create_app, db
from app.models import Alumno, TipoDocumento
from app.services.alumno_service import AlumnoService
from test.base_test import BaseTestCase
from test.instancias import nuevoAlumno

class AlumnoTestCase(BaseTestCase):
    
    def test_crear_alumno(self):
        alumno = nuevoAlumno()
        AlumnoService.crear_alumno(alumno)
        self.assertIsNotNone(alumno.id)
        alumno_db = AlumnoService.buscar_alumno_id(alumno.id)
        self.assertEqual(alumno_db.apellido, alumno.apellido)
        self.assertEqual(alumno_db.nro_legajo, alumno.nro_legajo)
        self.assertEqual(alumno_db.apellido, "Pérez")
        self.assertEqual(alumno_db.nombre, "Juan")
        self.assertEqual(alumno_db.nro_documento, "30123456")
        self.assertEqual(alumno_db.tipo_documento.nombre, "DNI")
        self.assertEqual(alumno_db.sexo, "M")
        self.assertEqual(alumno_db.nro_legajo, 12345)

    def test_actualizar_alumno(self):
        alumno = nuevoAlumno()
        AlumnoService.crear_alumno(alumno)
        alumno.apellido = "González"
        alumno.nro_legajo = 54321
        AlumnoService.actualizar_alumno(alumno)
        alumno_actualizado = AlumnoService.buscar_alumno_id(alumno.id)
        self.assertEqual(alumno_actualizado.apellido, "González")
        self.assertEqual(alumno_actualizado.nro_legajo, 54321)
    
    def test_eliminar_alumno(self):
        alumno = nuevoAlumno()
        AlumnoService.crear_alumno(alumno)
        alumno_id = alumno.id
        AlumnoService.borrar_alumno_id(alumno_id)
        alumno_eliminado = AlumnoService.buscar_alumno_id(alumno_id)
        self.assertIsNone(alumno_eliminado)
    
    def test_buscar_por_legajo(self):
        alumno = nuevoAlumno()
        AlumnoService.crear_alumno(alumno)
        alumno_encontrado = AlumnoService.buscar_alumno_legajo(alumno.nro_legajo)
        self.assertIsNotNone(alumno_encontrado)
        self.assertEqual(alumno_encontrado.nro_documento, alumno.nro_documento)