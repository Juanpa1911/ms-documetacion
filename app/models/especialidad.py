from dataclasses import dataclass
from app import db
from app.models import TipoEspecialidad

@dataclass(init=False, repr=True, eq=True)
class Especialidad():
    id: int
    nombre: str
    letra: str
    observacion: str
    facultad: str