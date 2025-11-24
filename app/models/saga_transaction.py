from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional


class SagaState(Enum):
    """Estados de una transacción SAGA"""
    PENDING = "PENDING"              # Transacción iniciada
    IN_PROGRESS = "IN_PROGRESS"      # En proceso
    COMPLETED = "COMPLETED"          # Completada exitosamente
    FAILED = "FAILED"                # Falló
    COMPENSATING = "COMPENSATING"    # Ejecutando compensación
    COMPENSATED = "COMPENSATED"      # Compensación completada
    

class SagaTransaction:
    """
    Modelo para representar una transacción SAGA en el sistema de documentación
    """
    def __init__(
        self,
        transaction_id: str,
        alumno_id: int,
        especialidad_id: int,
        tipo_documento: str,
        state: SagaState = SagaState.PENDING,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.transaction_id = transaction_id
        self.alumno_id = alumno_id
        self.especialidad_id = especialidad_id
        self.tipo_documento = tipo_documento
        self.state = state
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.steps_completed = []
        self.steps_to_compensate = []
        self.error_message = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la transacción a diccionario para almacenamiento"""
        return {
            'transaction_id': self.transaction_id,
            'alumno_id': self.alumno_id,
            'especialidad_id': self.especialidad_id,
            'tipo_documento': self.tipo_documento,
            'state': self.state.value,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'steps_completed': self.steps_completed,
            'steps_to_compensate': self.steps_to_compensate,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SagaTransaction':
        """Crea una transacción desde un diccionario"""
        transaction = cls(
            transaction_id=data['transaction_id'],
            alumno_id=data['alumno_id'],
            especialidad_id=data['especialidad_id'],
            tipo_documento=data['tipo_documento'],
            state=SagaState(data['state']),
            metadata=data.get('metadata', {})
        )
        transaction.created_at = datetime.fromisoformat(data['created_at'])
        transaction.updated_at = datetime.fromisoformat(data['updated_at'])
        transaction.steps_completed = data.get('steps_completed', [])
        transaction.steps_to_compensate = data.get('steps_to_compensate', [])
        transaction.error_message = data.get('error_message')
        return transaction
    
    def update_state(self, new_state: SagaState, error_message: Optional[str] = None):
        """Actualiza el estado de la transacción"""
        self.state = new_state
        self.updated_at = datetime.utcnow()
        if error_message:
            self.error_message = error_message
    
    def add_completed_step(self, step_name: str):
        """Registra un paso completado"""
        if step_name not in self.steps_completed:
            self.steps_completed.append(step_name)
            self.steps_to_compensate.insert(0, step_name)  # LIFO para compensación
            self.updated_at = datetime.utcnow()
    
    def get_next_step_to_compensate(self) -> Optional[str]:
        """Obtiene el siguiente paso a compensar (LIFO)"""
        if self.steps_to_compensate:
            return self.steps_to_compensate.pop(0)
        return None
