import os, logging
from app import create_app

#obtener contexto desde variable de entorno
flask_context = os.getenv('FLASK_CONFIG', 'development')

app = create_app()

with app.app_context():
    pass  # El contexto se activa aquí si es necesario

log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"Aplicación iniciada en: {flask_context} modo")

#entry point para graian
if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Servidor corriendo en el puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=flask_context != 'production')