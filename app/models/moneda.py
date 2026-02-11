from app import db
from datetime import datetime

class Moneda(db.Model):
    __tablename__ = 'monedas'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(3), unique=True, nullable=False)  # NIO, MXN, USD, COP
    nombre = db.Column(db.String(50), nullable=False)  # Córdoba Nicaraguense
    simbolo = db.Column(db.String(5), nullable=False)  # C$, $
    locale = db.Column(db.String(10), nullable=False)  # es-NI, es-MX, en-US
    activo = db.Column(db.Boolean, default=True)
    es_default = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    productos_origen = db.relationship('Producto', foreign_keys='Producto.moneda_original_id', back_populates='moneda_original')
    usuarios_preferencia = db.relationship('Usuario', foreign_keys='Usuario.moneda_preferida_id', back_populates='moneda_preferida')
    
    def __repr__(self):
        return f'<Moneda {self.codigo} - {self.nombre}>'
    
    @classmethod
    def get_default(cls):
        """Obtener la moneda configurada como default"""
        return cls.query.filter_by(es_default=True, activo=True).first()
    
    @classmethod
    def get_by_codigo(cls, codigo):
        """Obtener moneda por código (NIO, MXN, etc.)"""
        return cls.query.filter_by(codigo=codigo, activo=True).first()
    
    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'simbolo': self.simbolo,
            'locale': self.locale,
            'activo': self.activo,
            'es_default': self.es_default
        }