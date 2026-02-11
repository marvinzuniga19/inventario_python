from app import db
from datetime import datetime
from .moneda import Moneda

class TasaCambio(db.Model):
    __tablename__ = 'tasas_cambio'
    
    id = db.Column(db.Integer, primary_key=True)
    moneda_origen_id = db.Column(db.Integer, db.ForeignKey('monedas.id'), nullable=False)
    moneda_destino_id = db.Column(db.Integer, db.ForeignKey('monedas.id'), nullable=False)
    tasa = db.Column(db.Numeric(12, 6), nullable=False)  # Tasa de cambio (ej: 0.0085)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    moneda_origen = db.relationship('Moneda', foreign_keys=[moneda_origen_id])
    moneda_destino = db.relationship('Moneda', foreign_keys=[moneda_destino_id])
    
    # Índice compuesto para búsquedas eficientes
    __table_args__ = (
        db.UniqueConstraint('moneda_origen_id', 'moneda_destino_id', name='uq_tasa_cambio'),
        db.Index('idx_tasa_busqueda', 'moneda_origen_id', 'moneda_destino_id', 'fecha_actualizacion'),
    )
    
    def __repr__(self):
        return f'<TasaCambio {self.moneda_origen.codigo}->{self.moneda_destino.codigo}: {self.tasa}>'
    
    @classmethod
    def get_tasa_actual(cls, moneda_origen_id, moneda_destino_id):
        """Obtener la tasa de cambio más reciente entre dos monedas"""
        return cls.query.filter_by(
            moneda_origen_id=moneda_origen_id,
            moneda_destino_id=moneda_destino_id
        ).order_by(cls.fecha_actualizacion.desc()).first()
    
    @classmethod
    def get_tasa_por_codigo(cls, codigo_origen, codigo_destino):
        """Obtener tasa usando códigos de moneda en lugar de IDs"""
        moneda_origen = Moneda.get_by_codigo(codigo_origen)
        moneda_destino = Moneda.get_by_codigo(codigo_destino)
        
        if not moneda_origen or not moneda_destino:
            return None
            
        return cls.get_tasa_actual(moneda_origen.id, moneda_destino.id)
    
    @classmethod
    def actualizar_tasa(cls, moneda_origen_id, moneda_destino_id, nueva_tasa):
        """Actualizar o crear una tasa de cambio"""
        tasa_existente = cls.get_tasa_actual(moneda_origen_id, moneda_destino_id)
        
        if tasa_existente:
            tasa_existente.tasa = nueva_tasa
            tasa_existente.fecha_actualizacion = datetime.utcnow()
            db.session.commit()
            return tasa_existente
        else:
            nueva_tasa_cambio = cls(
                moneda_origen_id=moneda_origen_id,
                moneda_destino_id=moneda_destino_id,
                tasa=nueva_tasa
            )
            db.session.add(nueva_tasa_cambio)
            db.session.commit()
            return nueva_tasa_cambio
    
    @classmethod
    def obtener_todas_tasas(cls, moneda_base_id):
        """Obtener todas las tasas desde una moneda base"""
        return cls.query.filter_by(moneda_origen_id=moneda_base_id).all()
    
    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'id': self.id,
            'moneda_origen': self.moneda_origen.codigo,
            'moneda_destino': self.moneda_destino.codigo,
            'tasa': float(self.tasa),
            'fecha_actualizacion': self.fecha_actualizacion.isoformat()
        }