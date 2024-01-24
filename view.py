from app import app
from flask import render_template, request, redirect, flash

from forms import LoginForm, RegisterForm
from model import User

# class Name:
#     def __init__(self, name_type: str):
#         self.__name_type = name_type
#
#     def __call__(self, form, field):
#         name = field.data
#         if ' ' in name:
#             raise ValidationError(f'Digite apenas um {self.__name_type}')
#         elif not name.isalpha():
#             raise ValidationError(f'Digite apenas letras')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        if User.is_password_valid(login_form):
            return redirect('/dashboard')
        else:
            flash('Email e/ou senha inválidos', category='danger')

    return render_template('login.html', form=login_form)


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        try:
            User.register_form(register_form)
            return redirect('/login')
        except ValueError:
            flash(message='O e-mail informado já foi usado anteriormente.',
                  category='danger')

    return render_template('cadastro.html', form=register_form)


@app.route('/dashboard')
def dashboard():
    usuario_ja_registrou_mensagem = False
    if usuario_ja_registrou_mensagem:
        return render_template('dashboard-com-mensagem.html')
    else:
        return render_template('dashboard-sem-mensagem.html')


@app.route('/escrever_mensagem')
def escrever_mensagem():
    return render_template('escrever-mensagem.html')


@app.route('/editar_mensagem')
def editar_mensagem():
    return render_template('editar-mensagem.html')


@app.route('/autenticar', methods=['POST'])
def autenticar():
    email = request.form.get('email')
    password = request.form.get('password')
    if email == 'admin@admin.com' and password == '123':
        return redirect('/dashboard')
    else:
        flash('Email e/ou senha inválidos')
        return redirect('/login')
