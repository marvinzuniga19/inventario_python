from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models.usuario import Usuario
from app.forms.auth_forms import LoginForm, RegistroForm, PerfilForm, CambiarPasswordForm

# Decorador personalizado para eximir CSRF
def no_csrf(f):
    """Decorador para eximir validación CSRF en endpoints específicos"""
    f.__no_csrf__ = True
    return f

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
        
        # Guardar tema preferido si se envió
        if hasattr(form, 'tema_preferido') and form.tema_preferido.data:
            current_user.set_tema_preferido(form.tema_preferido.data)
        
        db.session.commit()
        
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('auth.perfil'))
    elif request.method == 'GET':
        form.nombre.data = current_user.nombre
        form.apellido.data = current_user.apellido
        form.email.data = current_user.email
        if hasattr(form, 'tema_preferido'):
            form.tema_preferido.data = current_user.get_tema_preferido()
    
    # Obtener temas disponibles
    THEME_PRESETS = {
        'default': {
            'nombre': 'Azul Default',
            'descripcion': 'Profesional y moderno - Azul corporativo',
            'gradient_start': '#4f46e5',
            'gradient_end': '#6366f1'
        },
        'blue_ocean': {
            'nombre': 'Océano Azul',
            'descripcion': 'Fresco y corporativo - Tonos azules marinos',
            'gradient_start': '#0891b2',
            'gradient_end': '#06b6d4'
        },
        'green_forest': {
            'nombre': 'Bosque Verde',
            'descripcion': 'Natural y eco-friendly - Tonos verdes frescos',
            'gradient_start': '#059669',
            'gradient_end': '#10b981'
        },
        'purple_night': {
            'nombre': 'Noche Púrpura',
            'descripcion': 'Creativo y moderno - Tonos púrpura elegantes',
            'gradient_start': '#7c3aed',
            'gradient_end': '#8b5cf6'
        },
        'orange_sunset': {
            'nombre': 'Atardecer Naranja',
            'descripcion': 'Energético y cálido - Tonos naranja vibrantes',
            'gradient_start': '#ea580c',
            'gradient_end': '#f97316'
        },
        'dark_minimal': {
            'nombre': 'Oscuro Minimalista',
            'descripcion': 'Elegante y profesional - Tonos grises oscuros',
            'gradient_start': '#1f2937',
            'gradient_end': '#374151'
        },
        'rose_modern': {
            'nombre': 'Rosa Moderno',
            'descripcion': 'Diseño y creatividad - Tonos rosas contemporáneos',
            'gradient_start': '#e11d48',
            'gradient_end': '#f43f5e'
        },
        'sky_light': {
            'nombre': 'Cielo Azul Claro',
            'descripcion': 'Ligero y aéreo - Tonos azules claros',
            'gradient_start': '#0284c7',
            'gradient_end': '#0ea5e9'
        }
    }
    
    return render_template('auth/perfil.html', 
                         form=form,
                         themes=THEME_PRESETS,
                         current_theme=current_user.get_tema_preferido())

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

@auth.route('/guardar-tema', methods=['POST'])
@login_required
@no_csrf  # Eximir de CSRF para API AJAX
def guardar_tema():
    """API endpoint para guardar tema preferido del usuario"""
    try:
        
        data = request.get_json()
        if not data or 'tema_preferido' not in data:
            return jsonify({'error': 'Tema no especificado'}), 400
        
        tema_nombre = data['tema_preferido']
        
        # Validar que el tema exista
        THEME_PRESETS = {
            'default': {'nombre': 'Azul Default'},
            'blue_ocean': {'nombre': 'Océano Azul'},
            'green_forest': {'nombre': 'Bosque Verde'},
            'purple_night': {'nombre': 'Noche Púrpura'},
            'orange_sunset': {'nombre': 'Atardecer Naranja'},
            'dark_minimal': {'nombre': 'Oscuro Minimalista'},
            'rose_modern': {'nombre': 'Rosa Moderno'},
            'sky_light': {'nombre': 'Cielo Azul Claro'}
        }
        
        if tema_nombre not in THEME_PRESETS:
            return jsonify({'error': 'Tema no válido'}), 400
        
        # Guardar tema del usuario
        current_user.set_tema_preferido(tema_nombre)
        db.session.commit()
        
        # El meta tag se actualiza automáticamente en el template base
        # cuando el usuario recarga la página
        
        return jsonify({
            'success': True,
            'message': 'Tema guardado exitosamente',
            'tema': tema_nombre,
            'tema_info': THEME_PRESETS[tema_nombre]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error guardando tema: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500