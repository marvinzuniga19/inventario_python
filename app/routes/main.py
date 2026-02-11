from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.producto import Producto
from app.models.categoria import Categoria
from app.models.movimiento import Movimiento

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    # Estadísticas generales
    total_productos = Producto.query.filter_by(activo=True).count()
    bajo_stock = Producto.query.filter(
        Producto.cantidad_stock <= Producto.umbral_minimo,
        Producto.cantidad_stock > 0,
        Producto.activo == True
    ).count()
    sin_stock = Producto.query.filter_by(cantidad_stock=0, activo=True).count()
    
    # Calcular valor total del inventario
    valor_total = sum(p.get_valor_total() for p in Producto.query.filter_by(activo=True).all())
    
    # Movimientos recientes
    movimientos_recientes = Movimiento.query.order_by(Movimiento.fecha.desc()).limit(5).all()
    
    # Productos con bajo stock
    productos_bajo_stock = Producto.query.filter(
        Producto.cantidad_stock <= Producto.umbral_minimo,
        Producto.cantidad_stock > 0,
        Producto.activo == True
    ).order_by(Producto.cantidad_stock.asc()).limit(5).all()
    
    # Productos sin stock
    productos_sin_stock = Producto.query.filter_by(cantidad_stock=0, activo=True).limit(5).all()
    
    # Total de categorías
    total_categorias = Categoria.query.count()
    
    return render_template('dashboard/index.html',
                         total_productos=total_productos,
                         bajo_stock=bajo_stock,
                         sin_stock=sin_stock,
                         valor_total=valor_total,
                         movimientos_recientes=movimientos_recientes,
                         productos_bajo_stock=productos_bajo_stock,
                         productos_sin_stock=productos_sin_stock,
                         total_categorias=total_categorias)