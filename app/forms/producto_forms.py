from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, DecimalField, IntegerField, TextAreaField, SelectField, BooleanField, ValidationError
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from app.models.producto import Producto

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del Producto', validators=[DataRequired(), Length(min=2, max=200)])
    sku = StringField('SKU', validators=[DataRequired(), Length(min=2, max=50)])
    id_categoria = SelectField('Categoría', coerce=int, validators=[DataRequired()])
    precio = DecimalField('Precio', validators=[
        DataRequired(), 
        NumberRange(min=0, message='El precio debe ser mayor o igual a 0')
    ], places=2)
    cantidad_stock = IntegerField('Cantidad en Stock', validators=[
        DataRequired(), 
        NumberRange(min=0, message='La cantidad debe ser mayor o igual a 0')
    ])
    umbral_minimo = IntegerField('Umbral Mínimo', validators=[
        DataRequired(), 
        NumberRange(min=1, message='El umbral mínimo debe ser mayor a 0')
    ], default=10)
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    imagen = FileField('Imagen del Producto', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Solo se permiten archivos de imagen')
    ])
    activo = BooleanField('Producto Activo', default=True)
    
    def validate_sku(self, sku):
        producto = Producto.query.filter_by(sku=sku.data).first()
        if producto and (not hasattr(self, 'producto_id') or producto.id != self.producto_id):
            raise ValidationError('Este SKU ya está registrado.')

class BuscarProductoForm(FlaskForm):
    termino = StringField('Buscar', validators=[Optional()])
    categoria = SelectField('Categoría', coerce=int, validators=[Optional()], default='')
    estado = SelectField('Estado', choices=[
        ('', 'Todos'),
        ('stock-normal', 'Stock Normal'),
        ('bajo-stock', 'Bajo Stock'),
        ('sin-stock', 'Sin Stock')
    ], validators=[Optional()], default='')