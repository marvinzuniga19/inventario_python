from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf import FlaskForm
from app import db
from app.models.categoria import Categoria

class CategoriaForm(FlaskForm):
    nombre = StringField('Nombre de la Categoría', validators=[DataRequired(), Length(min=2, max=100)])
    color = StringField('Color', validators=[Optional(), Length(min=7, max=7)], default='#007bff')
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])

categorias = Blueprint('categorias', __name__)

@categorias.route('/')
@login_required
def lista():
    page = request.args.get('page', 1, type=int)
    categorias_paginadas = Categoria.query.order_by(Categoria.nombre).paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Calcular total de productos activos para estas categorías
    total_productos_activos = 0
    for categoria in categorias_paginadas.items:
        total_productos_activos += len([p for p in categoria.productos if p.activo])
    
    return render_template('categorias/lista.html', 
                         categorias=categorias_paginadas,
                         total_productos_activos=total_productos_activos)

@categorias.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    form = CategoriaForm()
    
    if form.validate_on_submit():
        categoria = Categoria(
            nombre=form.nombre.data,
            color=form.color.data or '#007bff',
            descripcion=form.descripcion.data
        )
        
        db.session.add(categoria)
        db.session.commit()
        
        flash('¡Categoría creada exitosamente!', 'success')
        return redirect(url_for('categorias.lista'))
    
    return render_template('categorias/form.html', form=form, titulo='Nueva Categoría')

@categorias.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    categoria = Categoria.query.get_or_404(id)
    form = CategoriaForm(obj=categoria)
    
    if form.validate_on_submit():
        categoria.nombre = form.nombre.data
        categoria.color = form.color.data or '#007bff'
        categoria.descripcion = form.descripcion.data
        
        db.session.commit()
        
        flash('¡Categoría actualizada exitosamente!', 'success')
        return redirect(url_for('categorias.lista'))
    
    return render_template('categorias/form.html', form=form, categoria=categoria, titulo='Editar Categoría')

@categorias.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    categoria = Categoria.query.get_or_404(id)
    
    # Verificar si hay productos asociados
    productos_asociados = len([p for p in categoria.productos if p.activo])
    if productos_asociados > 0:
        flash(f'No se puede eliminar la categoría "{categoria.nombre}" porque tiene {productos_asociados} productos asociados. Elimina o reasigna los productos primero.', 'danger')
        return redirect(url_for('categorias.lista'))
    
    db.session.delete(categoria)
    db.session.commit()
    
    flash('¡Categoría eliminada exitosamente!', 'success')
    return redirect(url_for('categorias.lista'))