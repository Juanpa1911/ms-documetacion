import logging
import uuid
import requests
import os
from typing import Optional, Dict, Any, Tuple
from io import BytesIO

from app.models.saga_transaction import SagaTransaction, SagaState
from app.models.documentacion import Documentacion, EstadoDocumento, TipoDocumento
from app.services.redis_services import redis_service
from app.services.documento_office_services import DocumentoOfficeService

logger = logging.getLogger(__name__)


class DocumentacionService:
    """
    Servicio de orquestación SAGA para generación de documentación
    
    Coordina las llamadas a:
    - Microservicio de Alumno
    - Microservicio de Especialidad  
    - Generación de documentos (local)
    
    Patrón SAGA: Orquestación centralizada con compensaciones
    """
    
    # URLs de microservicios desde variables de entorno
    ALUMNO_SERVICE_URL = os.getenv('ALUMNO_SERVICE_URL', 'http://localhost:5001/api/v1')
    ESPECIALIDAD_SERVICE_URL = os.getenv('ESPECIALIDAD_SERVICE_URL', 'http://localhost:5002/api/v1')
    
    # Timeouts para llamadas HTTP
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))
    
    # Canales Redis para eventos
    CHANNEL_DOCUMENTO_GENERADO = 'documentacion:documento_generado'
    CHANNEL_DOCUMENTO_FALLIDO = 'documentacion:documento_fallido'
    
    @staticmethod
    def iniciar_generacion_documento(
        alumno_id: int,
        especialidad_id: int,
        tipo_documento: str = TipoDocumento.CERTIFICADO_REGULAR.value,
        formato: str = 'pdf'
    ) -> Tuple[str, SagaTransaction]:
        """
        Inicia una transacción SAGA para generar un documento
        
        Args:
            alumno_id: ID del alumno
            especialidad_id: ID de la especialidad
            tipo_documento: Tipo de documento a generar
            formato: Formato del documento (pdf, docx, odt)
            
        Returns:
            Tuple con (transaction_id, SagaTransaction)
        """
        # Generar ID único para la transacción
        transaction_id = str(uuid.uuid4())
        
        # Crear transacción SAGA
        saga = SagaTransaction(
            transaction_id=transaction_id,
            alumno_id=alumno_id,
            especialidad_id=especialidad_id,
            tipo_documento=tipo_documento,
            state=SagaState.PENDING,
            metadata={
                'formato': formato,
                'origen': 'api_rest'
            }
        )
        
        # Guardar en Redis
        redis_service.save_saga_transaction(transaction_id, saga.to_dict(), ttl=7200)
        
        logger.info(f"🚀 SAGA iniciada: {transaction_id} - Alumno: {alumno_id}, Especialidad: {especialidad_id}")
        
        return transaction_id, saga
    
    @staticmethod
    def ejecutar_saga_generacion_documento(transaction_id: str) -> Dict[str, Any]:
        """
        Ejecuta la orquestación SAGA completa para generar un documento
        
        Pasos:
        1. Obtener datos del alumno (microservicio)
        2. Obtener datos de la especialidad (microservicio)
        3. Generar documento (local)
        4. Publicar evento de éxito
        
        Si falla algún paso, ejecuta compensaciones en orden inverso (LIFO)
        
        Returns:
            Dict con resultado de la operación
        """
        # Recuperar transacción de Redis
        saga_data = redis_service.get_saga_transaction(transaction_id)
        if not saga_data:
            raise ValueError(f"Transacción SAGA no encontrada: {transaction_id}")
        
        saga = SagaTransaction.from_dict(saga_data)
        saga.update_state(SagaState.IN_PROGRESS)
        redis_service.update_saga_transaction(transaction_id, saga.to_dict())
        
        logger.info(f"⚙️ Ejecutando SAGA: {transaction_id}")
        
        try:
            # PASO 1: Obtener datos del alumno
            alumno_data = DocumentacionService._paso_obtener_alumno(saga)
            saga.add_completed_step('obtener_alumno')
            redis_service.update_saga_transaction(transaction_id, saga.to_dict())
            
            # PASO 2: Obtener datos de la especialidad
            especialidad_data = DocumentacionService._paso_obtener_especialidad(saga)
            saga.add_completed_step('obtener_especialidad')
            redis_service.update_saga_transaction(transaction_id, saga.to_dict())
            
            # PASO 3: Generar documento
            documento_bytes = DocumentacionService._paso_generar_documento(
                saga, alumno_data, especialidad_data
            )
            saga.add_completed_step('generar_documento')
            
            # Marcar como completada
            saga.update_state(SagaState.COMPLETED)
            redis_service.update_saga_transaction(transaction_id, saga.to_dict())
            
            # Publicar evento de éxito
            DocumentacionService._publicar_evento_exito(transaction_id, saga)
            
            logger.info(f"✅ SAGA completada: {transaction_id}")
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'documento': documento_bytes,
                'metadata': {
                    'alumno': alumno_data,
                    'especialidad': especialidad_data,
                    'tipo_documento': saga.tipo_documento,
                    'formato': saga.metadata.get('formato', 'pdf')
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error en SAGA {transaction_id}: {str(e)}")
            
            # Iniciar compensación
            saga.update_state(SagaState.COMPENSATING, error_message=str(e))
            redis_service.update_saga_transaction(transaction_id, saga.to_dict())
            
            DocumentacionService._ejecutar_compensaciones(saga)
            
            saga.update_state(SagaState.COMPENSATED)
            redis_service.update_saga_transaction(transaction_id, saga.to_dict())
            
            # Publicar evento de fallo
            DocumentacionService._publicar_evento_fallo(transaction_id, saga, str(e))
            
            return {
                'success': False,
                'transaction_id': transaction_id,
                'error': str(e),
                'state': saga.state.value
            }
    
    @staticmethod
    def _paso_obtener_alumno(saga: SagaTransaction) -> Dict[str, Any]:
        """Paso 1: Obtener datos del alumno desde el microservicio"""
        logger.info(f"📋 [SAGA {saga.transaction_id}] Paso 1: Obteniendo alumno {saga.alumno_id}")
        
        try:
            url = f"{DocumentacionService.ALUMNO_SERVICE_URL}/alumnos/{saga.alumno_id}"
            response = requests.get(url, timeout=DocumentacionService.REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                alumno_data = response.json()
                logger.info(f"✓ Alumno obtenido: {alumno_data.get('nombre', 'N/A')}")
                return alumno_data
            elif response.status_code == 404:
                raise ValueError(f"Alumno no encontrado: {saga.alumno_id}")
            else:
                raise Exception(f"Error al obtener alumno: HTTP {response.status_code}")
                
        except requests.Timeout:
            raise Exception(f"Timeout al conectar con servicio de alumnos")
        except requests.ConnectionError:
            raise Exception(f"No se pudo conectar con el servicio de alumnos")
    
    @staticmethod
    def _paso_obtener_especialidad(saga: SagaTransaction) -> Dict[str, Any]:
        """Paso 2: Obtener datos de la especialidad desde el microservicio"""
        logger.info(f"📋 [SAGA {saga.transaction_id}] Paso 2: Obteniendo especialidad {saga.especialidad_id}")
        
        try:
            url = f"{DocumentacionService.ESPECIALIDAD_SERVICE_URL}/especialidades/{saga.especialidad_id}"
            response = requests.get(url, timeout=DocumentacionService.REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                especialidad_data = response.json()
                logger.info(f"✓ Especialidad obtenida: {especialidad_data.get('nombre', 'N/A')}")
                return especialidad_data
            elif response.status_code == 404:
                raise ValueError(f"Especialidad no encontrada: {saga.especialidad_id}")
            else:
                raise Exception(f"Error al obtener especialidad: HTTP {response.status_code}")
                
        except requests.Timeout:
            raise Exception(f"Timeout al conectar con servicio de especialidades")
        except requests.ConnectionError:
            raise Exception(f"No se pudo conectar con el servicio de especialidades")
    
    @staticmethod
    def _paso_generar_documento(
        saga: SagaTransaction,
        alumno_data: Dict[str, Any],
        especialidad_data: Dict[str, Any]
    ) -> BytesIO:
        """Paso 3: Generar el documento en el formato solicitado"""
        logger.info(f"📋 [SAGA {saga.transaction_id}] Paso 3: Generando documento")
        
        formato = saga.metadata.get('formato', 'pdf')
        tipo_doc = saga.tipo_documento
        
        # Preparar datos para el template
        contexto = {
            'alumno': alumno_data,
            'especialidad': especialidad_data,
            'tipo_documento': tipo_doc,
            'transaction_id': saga.transaction_id
        }
        
        # Generar según formato
        if formato == 'pdf':
            documento = DocumentoOfficeService.generar_pdf_desde_html(
                template_name=f'{tipo_doc.lower()}.html',
                context=contexto
            )
        elif formato == 'docx':
            documento = DocumentoOfficeService.generar_docx(
                template_name=f'{tipo_doc.lower()}.html',
                context=contexto
            )
        elif formato == 'odt':
            documento = DocumentoOfficeService.generar_odt(
                template_name=f'{tipo_doc.lower()}.html',
                context=contexto
            )
        else:
            raise ValueError(f"Formato no soportado: {formato}")
        
        logger.info(f"✓ Documento generado en formato {formato}")
        return documento
    
    @staticmethod
    def _ejecutar_compensaciones(saga: SagaTransaction):
        """Ejecuta las compensaciones en orden inverso (LIFO)"""
        logger.warning(f"🔄 [SAGA {saga.transaction_id}] Iniciando compensaciones")
        
        while True:
            step = saga.get_next_step_to_compensate()
            if not step:
                break
            
            logger.info(f"↩️ Compensando paso: {step}")
            
            # Definir compensaciones según el paso
            if step == 'obtener_alumno':
                # Compensación: Invalidar caché de alumno
                redis_service.delete(f"cache:alumno:{saga.alumno_id}")
                
            elif step == 'obtener_especialidad':
                # Compensación: Invalidar caché de especialidad
                redis_service.delete(f"cache:especialidad:{saga.especialidad_id}")
                
            elif step == 'generar_documento':
                # Compensación: Limpiar recursos temporales
                redis_service.delete(f"temp:documento:{saga.transaction_id}")
        
        logger.info(f"✓ Compensaciones completadas para {saga.transaction_id}")
    
    @staticmethod
    def _publicar_evento_exito(transaction_id: str, saga: SagaTransaction):
        """Publica evento cuando el documento se genera exitosamente"""
        evento = {
            'event_type': 'documento_generado',
            'transaction_id': transaction_id,
            'alumno_id': saga.alumno_id,
            'especialidad_id': saga.especialidad_id,
            'tipo_documento': saga.tipo_documento,
            'formato': saga.metadata.get('formato'),
            'timestamp': saga.updated_at.isoformat()
        }
        redis_service.publish_event(DocumentacionService.CHANNEL_DOCUMENTO_GENERADO, evento)
    
    @staticmethod
    def _publicar_evento_fallo(transaction_id: str, saga: SagaTransaction, error: str):
        """Publica evento cuando falla la generación del documento"""
        evento = {
            'event_type': 'documento_fallido',
            'transaction_id': transaction_id,
            'alumno_id': saga.alumno_id,
            'especialidad_id': saga.especialidad_id,
            'tipo_documento': saga.tipo_documento,
            'error': error,
            'timestamp': saga.updated_at.isoformat()
        }
        redis_service.publish_event(DocumentacionService.CHANNEL_DOCUMENTO_FALLIDO, evento)
    
    @staticmethod
    def obtener_estado_transaccion(transaction_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado actual de una transacción SAGA"""
        saga_data = redis_service.get_saga_transaction(transaction_id)
        if saga_data:
            return saga_data
        return None
    
    @staticmethod
    def listar_transacciones_activas() -> list:
        """Lista todas las transacciones SAGA activas"""
        transaction_ids = redis_service.list_saga_transactions()
        transacciones = []
        
        for tid in transaction_ids:
            saga_data = redis_service.get_saga_transaction(tid)
            if saga_data and saga_data['state'] in ['PENDING', 'IN_PROGRESS', 'COMPENSATING']:
                transacciones.append(saga_data)
        
        return transacciones
