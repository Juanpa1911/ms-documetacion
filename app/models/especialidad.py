from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.facultad import Facultad

@dataclass(init=False, repr=True, eq=True)
class Especialidad():
    id: int
    nombre: str
    letra: str
    observacion: str
    facultad: 'Facultad'  # Puede ser objeto Facultad o string según el response del API