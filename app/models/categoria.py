from datetime import datetime
from app import db

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    color = db.Column(db.String(7), default='#007bff')  # Color en formato hex
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    productos = db.relationship('Producto', back_populates='categoria', lazy=True)
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'