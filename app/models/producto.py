from datetime import datetime
from app import db

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    
    # Moneda y precio
    moneda_original_id = db.Column(db.Integer, db.ForeignKey('monedas.id'))
    precio_original = db.Column(db.Numeric(10, 2), nullable=False)  # Precio en moneda original
    precio_base = db.Column(db.Numeric(10, 2), nullable=False)  # Precio en NIO (moneda base)
    
    cantidad_stock = db.Column(db.Integer, nullable=False, default=0)
    umbral_minimo = db.Column(db.Integer, nullable=False, default=10)
    imagen_url = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    movimientos = db.relationship('Movimiento', backref='producto', lazy=True)
    categoria = db.relationship('Categoria', back_populates='productos')
    moneda_original = db.relationship('Moneda', foreign_keys=[moneda_original_id], back_populates='productos_origen')
    
    def get_valor_total(self):
        """Valor total en moneda base (NIO)"""
        return float(self.precio_base) * self.cantidad_stock
    
    def get_precio_en_moneda(self, moneda_destino_id=None):
        """Convertir precio a moneda específica"""
        if moneda_destino_id is None:
            # Si no se especifica, usar moneda base (NIO)
            return float(self.precio_base)
        
        from .tasa_cambio import TasaCambio
        from .moneda import Moneda
        
        # Obtener moneda base (NIO)
        moneda_nio = Moneda.get_by_codigo('NIO')
        if not moneda_nio:
            return float(self.precio_base)
        
        # Si se solicita en NIO, retornar precio base
        if moneda_destino_id == moneda_nio.id:
            return float(self.precio_base)
        
        # Buscar tasa de conversión NIO -> moneda_destino
        tasa = TasaCambio.get_tasa_actual(moneda_nio.id, moneda_destino_id)
        if tasa:
            return float(self.precio_base) * float(tasa.tasa)
        else:
            # Si no hay tasa, retornar precio base
            return float(self.precio_base)
    
    def get_precio_formateado(self, moneda_destino=None):
        """Obtener precio formateado en moneda específica"""
        from .moneda import Moneda
        
        if moneda_destino is None:
            moneda = Moneda.get_default() or Moneda.get_by_codigo('NIO')
        else:
            moneda = moneda_destino
        
        if isinstance(moneda_destino, str):
            moneda = Moneda.get_by_codigo(moneda_destino)
        
        precio = self.get_precio_en_moneda(moneda.id if moneda else None)
        
        # Formateo simple basado en locale
        if moneda and moneda.locale == 'es-NI':
            return f"C${precio:,.2f}"
        elif moneda and moneda.locale == 'es-MX':
            return f"${precio:,.2f} MXN"
        elif moneda and moneda.locale == 'en-US':
            return f"${precio:,.2f} USD"
        else:
            return f"${precio:,.2f}"
    
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
    
    @property
    def precio(self):
        """Propiedad legacy para compatibilidad con código existente"""
        return self.precio_base