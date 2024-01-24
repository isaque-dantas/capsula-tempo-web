from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, DateField, TimeField, TextAreaField
from wtforms.validators import DataRequired, Length

from model import User, CapsuleMessage


class RegisterForm(FlaskForm):
    first_name = StringField('Primeiro nome',
                             validators=[
                                 DataRequired(),
                                 Length(2, User.MAX_LENGTH['first_name'])
                             ])

    last_name = StringField('Sobrenome',
                            validators=[
                                DataRequired(),
                                Length(2, User.MAX_LENGTH['last_name'])
                            ])

    password = PasswordField('Senha',
                             validators=[
                                 DataRequired(),
                                 Length(6, User.MAX_LENGTH['password'])
                             ])

    email = EmailField('E-mail',
                       validators=[
                           DataRequired(),
                           Length(max=User.MAX_LENGTH['email'])
                       ])

    submit = SubmitField('Confirmar')


class LoginForm(FlaskForm):
    email = EmailField('E-mail',
                       validators=[
                           DataRequired(),
                           Length(max=User.MAX_LENGTH['email'])
                       ])

    password = PasswordField('Senha',
                             validators=[
                                 DataRequired(),
                                 Length(max=User.MAX_LENGTH['password'])
                             ])

    submit = SubmitField('Confirmar')


class CapsuleMessageForm(FlaskForm):
    title = StringField('Título',
                        validators=[
                            DataRequired(),
                            Length(max=CapsuleMessage.MAX_LENGTH['title'])
                        ])

    content = TextAreaField('Conteúdo',
                            validators=[
                                DataRequired()
                            ])

    date_can_open = DateField('O momento em que a mensagem será liberada')
    time_can_open = TimeField('O momento em que a mensagem será liberada')

    submit = SubmitField('Confirmar')
