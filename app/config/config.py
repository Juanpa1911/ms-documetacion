from dotenv import load_dotenv
from pathlib import Path
import os
import logging

basedir = os.path.abspath(Path(__file__).parents[2])
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    TESTING = False
    
    # Redis Configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    # Microservices URLs (soporta variables del docker-compose)
    # Prioriza ALUMNOS_HOST y ACADEMICA_HOST del docker-compose del profesor
    ALUMNO_SERVICE_URL = os.getenv('ALUMNOS_HOST') or os.getenv('ALUMNO_SERVICE_URL', 'http://localhost:5001/api/v1')
    ESPECIALIDAD_SERVICE_URL = os.getenv('ACADEMICA_HOST') or os.getenv('ESPECIALIDAD_SERVICE_URL', 'http://localhost:5002/api/v1')
    
    # Cache TTL (Time To Live) en segundos
    CACHE_ALUMNO_TTL = int(os.getenv('CACHE_ALUMNO_TTL', 300))  # 5 minutos
    CACHE_ESPECIALIDAD_TTL = int(os.getenv('CACHE_ESPECIALIDAD_TTL', 600))  # 10 minutos
    
    # HTTP Request Configuration
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 10))  # segundos
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @staticmethod
    def init_app(app):
        log_level = getattr(logging, app.config['LOG_LEVEL'])
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )

class TestConfig(Config):
    TESTING = True
    DEBUG = True
    
class DevelopmentConfig(Config):
    TESTING = True
    DEBUG = True
        
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

def factory(app: str) -> Config:
    configuration = {
        'testing': TestConfig,
        'development': DevelopmentConfig,
        'production': ProductionConfig
    }
    
    return configuration[app]