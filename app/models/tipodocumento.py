from dataclasses import dataclass

@dataclass(init=False, repr=True, eq=True)
class TipoDocumento():
    id: int
    sigla: str
    nombre: str
    

