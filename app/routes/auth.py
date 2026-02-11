from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models.usuario import Usuario
from app.forms.auth_forms import LoginForm, RegistroForm, PerfilForm, CambiarPasswordForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data) and user.activo:
            login_user(user, remember=form.remember_me.data)
            user.fecha_ultimo_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            
            flash(f'¡Bienvenido {user.get_nombre_completo()}!', 'success')
            return redirect(next_page)
        else:
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistroForm()
    if form.validate_on_submit():
        user = Usuario(
            email=form.email.data,
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            rol=form.rol.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('¡Usuario registrado exitosamente! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    form = PerfilForm()
    form.usuario_original = current_user
    
    if form.validate_on_submit():
        current_user.nombre = form.nombre.data
        current_user.apellido = form.apellido.data
        current_user.email = form.email.data
        db.session.commit()
        
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('auth.perfil'))
    elif request.method == 'GET':
        form.nombre.data = current_user.nombre
        form.apellido.data = current_user.apellido
        form.email.data = current_user.email
    
    return render_template('auth/perfil.html', form=form)

@auth.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    form = CambiarPasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.password_actual.data):
            current_user.set_password(form.password_nueva.data)
            db.session.commit()
            
            flash('Contraseña actualizada correctamente', 'success')
            return redirect(url_for('auth.perfil'))
        else:
            flash('La contraseña actual es incorrecta', 'danger')
    
    return render_template('auth/cambiar_password.html', form=form)