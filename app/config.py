import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-temporal-cambiar-en-produccion'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///inventario.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de uploads
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Configuración de email (opcional para alertas)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configuración de monedas
    MONEDA_DEFAULT = os.environ.get('MONEDA_DEFAULT') or 'NIO'  # Córdoba Nicaraguense
    MONEDAS_SOPORTADAS = ['NIO', 'MXN', 'USD', 'COP']  # Monedas soportadas
    
    # API de tasas de cambio
    API_TASAS_CAMBIO = os.environ.get('API_TASAS_CAMBIO') or 'https://api.exchangerate-api.com/v4/latest/'
    API_TASAS_PROVIDER = os.environ.get('API_TASAS_PROVIDER') or 'exchangerate_api'
    API_TASAS_KEY = os.environ.get('API_TASAS_KEY')  # Opcional para algunas APIs
    
    # Frecuencia de actualización de tasas (en horas)
    ACTUALIZAR_TASAS_HORAS = int(os.environ.get('ACTUALIZAR_TASAS_HORAS') or 168)  # 7 días (semanal)
    
    # Tasas de conversión iniciales (para migración)
    CONVERSION_COP_A_NIO = float(os.environ.get('CONVERSION_COP_A_NIO') or 0.0085)
    CONVERSION_USD_A_NIO = float(os.environ.get('CONVERSION_USD_A_NIO') or 36.50)
    CONVERSION_MXN_A_NIO = float(os.environ.get('CONVERSION_MXN_A_NIO') or 2.10)
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}