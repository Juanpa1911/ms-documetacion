from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tipodocumento import TipoDocumento
    from .especialidad import Especialidad

@dataclass(init=False, repr=True, eq=True)
class Alumno:
    id: int
    nombre: str
    apellido: str
    nrodocumento: str
    tipo_documento: 'TipoDocumento'
    especialidad: 'Especialidad'
