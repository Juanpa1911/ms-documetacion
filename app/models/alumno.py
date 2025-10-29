from dataclasses import dataclass


from app.models import TipoDocumento,Especialidad

@dataclass(init=False, repr=True, eq=True)
class Alumno():
  
    id:int 
    nombre:str 
    apellido:str 
    nrodocumento: str
    tipo_documento :TipoDocumento
    especialidad :Especialidad
