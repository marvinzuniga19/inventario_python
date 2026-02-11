from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from app.config import config

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configurar LoginManager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Registrar blueprints
    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.routes.productos import productos as productos_blueprint
    app.register_blueprint(productos_blueprint, url_prefix='/productos')
    
    from app.routes.categorias import categorias as categorias_blueprint
    app.register_blueprint(categorias_blueprint, url_prefix='/categorias')
    
    from app.routes.movimientos import movimientos as movimientos_blueprint
    app.register_blueprint(movimientos_blueprint, url_prefix='/movimientos')
    
    # Crear directorio de uploads si no existe
    import os
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Importar modelos para que SQLAlchemy los reconozca
    from app.models import usuario, producto, categoria, movimiento
    
    # Cargar usuario actual
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.usuario import Usuario
        return Usuario.query.get(int(user_id))
    
    # Procesador de contexto global para alertas de bajo stock
    @app.context_processor
    def inject_alert_counts():
        from flask_login import current_user
        from app.models.producto import Producto
        
        bajo_stock_count = 0
        try:
            if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                bajo_stock_count = Producto.query.filter(
                    Producto.cantidad_stock <= Producto.umbral_minimo,
                    Producto.cantidad_stock > 0,
                    Producto.activo == True
                ).count()
        except:
            pass  # Manejar caso de usuario no autenticado
        
        return {'bajo_stock_count': bajo_stock_count}
    
    return app