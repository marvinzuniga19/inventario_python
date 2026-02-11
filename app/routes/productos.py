from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app import db
from app.models.producto import Producto
from app.models.categoria import Categoria
from app.forms.producto_forms import ProductoForm, BuscarProductoForm

productos = Blueprint('productos', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@productos.route('/')
@login_required
def lista():
    page = request.args.get('page', 1, type=int)
    termino = request.args.get('termino', '')
    categoria_id = request.args.get('categoria', '', type=int)
    estado = request.args.get('estado', '')
    
    form = BuscarProductoForm()
    form.categoria.choices = [(0, 'Todas')] + [(c.id, c.nombre) for c in Categoria.query.order_by(Categoria.nombre).all()]
    
    # Construir consulta
    query = Producto.query.filter_by(activo=True)
    
    if termino:
        query = query.filter(
            Producto.nombre.ilike(f'%{termino}%') |
            Producto.sku.ilike(f'%{termino}%') |
            Producto.descripcion.ilike(f'%{termino}%')
        )
    
    if categoria_id:
        query = query.filter_by(id_categoria=categoria_id)
    
    if estado == 'bajo-stock':
        query = query.filter(Producto.cantidad_stock <= Producto.umbral_minimo)
        query = query.filter(Producto.cantidad_stock > 0)
    elif estado == 'sin-stock':
        query = query.filter_by(cantidad_stock=0)
    elif estado == 'stock-normal':
        query = query.filter(Producto.cantidad_stock > Producto.umbral_minimo)
    
    productos_paginados = query.order_by(Producto.nombre).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Calcular estadísticas
    total_productos = Producto.query.filter_by(activo=True).count()
    bajo_stock = Producto.query.filter(
        Producto.cantidad_stock <= Producto.umbral_minimo,
        Producto.cantidad_stock > 0,
        Producto.activo == True
    ).count()
    sin_stock = Producto.query.filter_by(cantidad_stock=0, activo=True).count()
    valor_total = sum(p.get_valor_total() for p in Producto.query.filter_by(activo=True).all())
    
    return render_template('productos/lista.html', 
                         productos=productos_paginados,
                         form=form,
                         termino=termino,
                         categoria_id=categoria_id,
                         estado=estado,
                         stats={
                             'total_productos': total_productos,
                             'bajo_stock': bajo_stock,
                             'sin_stock': sin_stock,
                             'valor_total': valor_total
                         })

@productos.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    form = ProductoForm()
    form.id_categoria.choices = [(c.id, c.nombre) for c in Categoria.query.order_by(Categoria.nombre).all()]
    
    if form.validate_on_submit():
        # Manejar imagen
        imagen_url = None
        if form.imagen.data and allowed_file(form.imagen.data.filename):
            filename = secure_filename(form.imagen.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.imagen.data.save(upload_path)
            imagen_url = filename
        
        producto = Producto(
            nombre=form.nombre.data,
            sku=form.sku.data,
            id_categoria=form.id_categoria.data,
            precio=form.precio.data,
            cantidad_stock=form.cantidad_stock.data,
            umbral_minimo=form.umbral_minimo.data,
            descripcion=form.descripcion.data,
            imagen_url=imagen_url,
            activo=form.activo.data
        )
        
        db.session.add(producto)
        db.session.commit()
        
        flash('¡Producto creado exitosamente!', 'success')
        return redirect(url_for('productos.lista'))
    
    return render_template('productos/form.html', form=form, titulo='Nuevo Producto')

@productos.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    producto = Producto.query.get_or_404(id)
    form = ProductoForm(obj=producto)
    form.producto_id = id  # Para validación de SKU
    form.id_categoria.choices = [(c.id, c.nombre) for c in Categoria.query.order_by(Categoria.nombre).all()]
    
    if form.validate_on_submit():
        # Manejar imagen
        if form.imagen.data and allowed_file(form.imagen.data.filename):
            # Eliminar imagen anterior si existe
            if producto.imagen_url:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], producto.imagen_url)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            filename = secure_filename(form.imagen.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.imagen.data.save(upload_path)
            producto.imagen_url = filename
        
        producto.nombre = form.nombre.data
        producto.sku = form.sku.data
        producto.id_categoria = form.id_categoria.data
        producto.precio = form.precio.data
        producto.cantidad_stock = form.cantidad_stock.data
        producto.umbral_minimo = form.umbral_minimo.data
        producto.descripcion = form.descripcion.data
        producto.activo = form.activo.data
        
        db.session.commit()
        
        flash('¡Producto actualizado exitosamente!', 'success')
        return redirect(url_for('productos.lista'))
    
    return render_template('productos/form.html', form=form, producto=producto, titulo='Editar Producto')

@productos.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    producto = Producto.query.get_or_404(id)
    
    # Eliminar imagen si existe
    if producto.imagen_url:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], producto.imagen_url)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Marcar como inactivo en lugar de eliminar
    producto.activo = False
    db.session.commit()
    
    flash('¡Producto eliminado exitosamente!', 'success')
    return redirect(url_for('productos.lista'))

@productos.route('/ver/<int:id>')
@login_required
def ver(id):
    producto = Producto.query.get_or_404(id)
    return render_template('productos/detalle.html', producto=producto)