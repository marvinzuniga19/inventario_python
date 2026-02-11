from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.Enum('admin', 'empleado', name='rol_usuario'), default='empleado')
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_ultimo_login = db.Column(db.DateTime)
    
    # Moneda preferida del usuario
    moneda_preferida_id = db.Column(db.Integer, db.ForeignKey('monedas.id'), default=1)
    
    # Tema preferido del usuario
    tema_preferido = db.Column(db.String(20), default='default')  # default, blue_ocean, green_forest, etc.
    sidebar_config = db.Column(db.JSON, default={})  # Configuración personalizada de sidebar
    
    # Relaciones
    movimientos = db.relationship('Movimiento', backref='usuario', lazy=True)
    moneda_preferida = db.relationship('Moneda', foreign_keys=[moneda_preferida_id], back_populates='usuarios_preferencia')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    def get_moneda_preferida(self):
        """Obtener la moneda preferida del usuario o la default del sistema"""
        if self.moneda_preferida and self.moneda_preferida.activo:
            return self.moneda_preferida
        else:
            # Si el usuario no tiene moneda preferida o está inactiva, usar la default
            from .moneda import Moneda
            return Moneda.get_default()
    
    def get_tema_preferido(self):
        """Obtener el tema preferido del usuario"""
        return self.tema_preferido or 'default'
    
    def set_tema_preferido(self, tema):
        """Establecer el tema preferido del usuario"""
        self.tema_preferido = tema
    
    def __repr__(self):
        return f'<Usuario {self.email}>'