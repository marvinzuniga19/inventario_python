from datetime import datetime
from app import db

class Movimiento(db.Model):
    __tablename__ = 'movimientos'
    
    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo = db.Column(db.Enum('entrada', 'salida', name='tipo_movimiento'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    referencia = db.Column(db.String(100))  # Referencia externa como factura, orden de compra, etc.
    
    def get_tipo_clase(self):
        return 'success' if self.tipo == 'entrada' else 'danger'
    
    def get_tipo_icono(self):
        return 'bi-plus-circle' if self.tipo == 'entrada' else 'bi-dash-circle'
    
    def __repr__(self):
        return f'<Movimiento {self.tipo} {self.cantidad} unidades>'