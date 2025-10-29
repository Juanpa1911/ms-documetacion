from dataclasses import dataclass
from app import db

@dataclass(init=False, repr=True, eq=True)
class TipoDocumento():
    id: int
    sigla: str
    nombre: str
    

