from dataclasses import dataclass
from app.models.universidad import Universidad

@dataclass(init=False, repr=True, eq=True)
class Facultad():
    id: int
    nombre: str
    ciudad: str
    provincia: str
    universidad: 'Universidad'  # Forward reference

