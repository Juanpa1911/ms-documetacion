from dataclasses import dataclass

@dataclass(init=False, repr=True, eq=True)
class Universidad():
    id: int
    nombre: str
