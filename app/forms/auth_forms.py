from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.usuario import Usuario

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')

class RegistroForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    apellido = StringField('Apellido', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[
        DataRequired(), 
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    password_confirm = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    rol = SelectField('Rol', choices=[
        ('empleado', 'Empleado'),
        ('admin', 'Administrador')
    ], default='empleado')
    
    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email ya está registrado.')

class PerfilForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    apellido = StringField('Apellido', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    def validate_email(self, email):
        if email.data != self.usuario_original.email:
            user = Usuario.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Este email ya está registrado.')

class CambiarPasswordForm(FlaskForm):
    password_actual = PasswordField('Contraseña Actual', validators=[DataRequired()])
    password_nueva = PasswordField('Nueva Contraseña', validators=[
        DataRequired(), 
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    password_confirm = PasswordField('Confirmar Nueva Contraseña', validators=[
        DataRequired(),
        EqualTo('password_nueva', message='Las contraseñas deben coincidir')
    ])