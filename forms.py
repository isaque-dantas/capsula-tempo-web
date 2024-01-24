from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import ValidationError, DataRequired, Length


class RegisterForm(FlaskForm):
    first_name = StringField('Primeiro nome', validators=[DataRequired(), Length(2, 30)])
    last_name = StringField('Sobrenome', validators=[DataRequired(), Length(2, 30)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    email = EmailField('E-mail', validators=[DataRequired(), Length(3, 100)])
    submit = SubmitField('Confirmar')


class LoginForm(FlaskForm):
    email = EmailField('E-mail', validators=[DataRequired(), Length(3, 100)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    submit = SubmitField('Confirmar')
