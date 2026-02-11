from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from wtforms import StringField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf import FlaskForm
from datetime import datetime
from app import db
from app.models.movimiento import Movimiento
from app.models.producto import Producto

class MovimientoForm(FlaskForm):
    id_producto = SelectField('Producto', coerce=int, validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[
        ('entrada', 'Entrada'),
        ('salida', 'Salida')
    ], validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[
        DataRequired(), 
        NumberRange(min=1, message='La cantidad debe ser mayor a 0')
    ])
    motivo = StringField('Motivo', validators=[DataRequired()])
    referencia = StringField('Referencia (Opcional)')

movimientos = Blueprint('movimientos', __name__)

@movimientos.route('/')
@login_required
def lista():
    page = request.args.get('page', 1, type=int)
    producto_id = request.args.get('producto_id', type=int)
    
    # Construir consulta
    query = Movimiento.query.order_by(Movimiento.fecha.desc())
    
    if producto_id:
        query = query.filter_by(id_producto=producto_id)
        # Obtener información del producto para el título
        producto = Producto.query.get(producto_id)
        titulo_filtro = f" - {producto.nombre}" if producto else ""
    else:
        titulo_filtro = ""
    
    movimientos_paginados = query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('movimientos/lista.html', 
                         movimientos=movimientos_paginados,
                         producto_filtro=producto_id,
                         titulo_filtro=titulo_filtro)

@movimientos.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    form = MovimientoForm()
    form.id_producto.choices = [(p.id, f"{p.nombre} (Stock: {p.cantidad_stock})") 
                               for p in Producto.query.filter_by(activo=True).order_by(Producto.nombre).all()]
    
    # Manejar parámetros GET para pre-seleccionar producto y tipo
    producto_id = request.args.get('producto_id', type=int)
    tipo_preseleccionado = request.args.get('tipo', '')
    
    if producto_id:
        form.id_producto.data = producto_id
        # Obtener información del producto para mostrar en el título
        producto = Producto.query.get(producto_id)
        if producto:
            # Si no se especifica tipo, deducirlo según stock
            if not tipo_preseleccionado:
                tipo_preseleccionado = 'salida' if producto.cantidad_stock > 0 else 'entrada'
    
    if tipo_preseleccionado:
        if tipo_preseleccionado in ['entrada', 'salida']:
            form.tipo.data = tipo_preseleccionado
    
    if form.validate_on_submit():
        producto = Producto.query.get(form.id_producto.data)
        
        # Validar stock disponible para salidas
        if form.tipo.data == 'salida' and producto.cantidad_stock < form.cantidad.data:
            flash(f'No hay suficiente stock. Stock disponible: {producto.cantidad_stock}', 'danger')
            return render_template('movimientos/form.html', form=form, titulo='Nuevo Movimiento')
        
        # Crear movimiento
        movimiento = Movimiento(
            id_producto=form.id_producto.data,
            id_usuario=current_user.id,
            tipo=form.tipo.data,
            cantidad=form.cantidad.data,
            motivo=form.motivo.data,
            referencia=form.referencia.data
        )
        
        # Actualizar stock del producto
        if form.tipo.data == 'entrada':
            producto.cantidad_stock += form.cantidad.data
        else:
            producto.cantidad_stock -= form.cantidad.data
        
        db.session.add(movimiento)
        db.session.commit()
        
        flash(f'¡{form.tipo.data.title()} de {form.cantidad.data} unidades registrada exitosamente!', 'success')
        return redirect(url_for('movimientos.lista'))
    
    titulo = 'Nuevo Movimiento'
    if producto_id:
        producto = Producto.query.get(producto_id)
        if producto:
            titulo = f'Registrar {tipo_preseleccionado.title()} - {producto.nombre}'
    
    # Obtener todos los productos para el JavaScript
    productos = Producto.query.filter_by(activo=True).all()
    
    return render_template('movimientos/form.html', 
                         form=form, 
                         titulo=titulo, 
                         producto_seleccionado=producto_id,
                         productos=productos)