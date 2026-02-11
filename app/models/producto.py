from datetime import datetime
from app import db

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    cantidad_stock = db.Column(db.Integer, nullable=False, default=0)
    umbral_minimo = db.Column(db.Integer, nullable=False, default=10)
    imagen_url = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    movimientos = db.relationship('Movimiento', backref='producto', lazy=True)
    
    def get_valor_total(self):
        return float(self.precio) * self.cantidad_stock
    
    def get_estado_stock(self):
        if self.cantidad_stock <= 0:
            return 'sin-stock'
        elif self.cantidad_stock <= self.umbral_minimo:
            return 'bajo-stock'
        else:
            return 'stock-normal'
    
    def get_estado_color(self):
        estado = self.get_estado_stock()
        colores = {
            'sin-stock': 'danger',
            'bajo-stock': 'warning', 
            'stock-normal': 'success'
        }
        return colores.get(estado, 'secondary')
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'