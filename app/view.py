import werkzeug

from app import app, login_manager
from flask import render_template, request, redirect, flash, url_for
from flask_login import AnonymousUserMixin, login_required, login_user, logout_user, current_user

from app.forms import LoginForm, RegisterForm, CapsuleMessageForm, EditCapsuleMessageTitleForm
from app.model import User, CapsuleMessage


# TODO: adicionar página com o erro 404 e colocar nela a opção de ir para a página anterior
# TODO: desenvolver página com o erro 403 e colocar nela a opção de ir para a página anterior
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not isinstance(current_user, AnonymousUserMixin):
        return redirect(url_for('dashboard'))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        user = User.get_by_email(login_form.email.data)

        if user is not None and user.is_password_valid(login_form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Email e/ou senha inválidos',
                  category='danger')

    return render_template('login.html', form=login_form)


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        try:
            User.register(register_form)
        except Exception as e:
            flash(message=str(e), category='danger')
        else:
            return redirect('/login')

    return render_template('cadastro.html', form=register_form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard-lista-mensagens.html',
                           first_name=current_user.first_name,
                           capsule_messages=current_user.get_capsule_messages(),
                           enumerate=enumerate,
                           format=format)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/mensagem/<int:capsule_message_id>', methods=['GET', 'POST'])
@app.route('/mensagem/<int:capsule_message_id>/', methods=['GET', 'POST'])
@login_required
def mensagem(capsule_message_id: int):
    form = EditCapsuleMessageTitleForm()
    capsule_message = CapsuleMessage.get_by_id(capsule_message_id)

    if form.validate_on_submit():
        capsule_message.update_title(form.title.data)
        return redirect(url_for('mensagem', capsule_message_id=capsule_message_id))

    if current_user.has_capsule_message_id(capsule_message_id):
        usuario_pode_ler_a_mensagem = \
            current_user.can_read_capsule_message(capsule_message_id)

        return render_template('dashboard-mensagem.html',
                               capsule_message=capsule_message,
                               usuario_pode_ler_a_mensagem=usuario_pode_ler_a_mensagem,
                               form=form)
    else:
        return (
            render_template('http_403_forbidden.html'),
            werkzeug.exceptions.Forbidden().code
        )


@app.route('/escrever_mensagem', methods=['GET', 'POST'])
def escrever_mensagem():
    capsule_message_form = CapsuleMessageForm()

    if capsule_message_form.validate_on_submit():
        CapsuleMessage.register(capsule_message_form, current_user)
        return redirect(url_for('dashboard'))

    return render_template('escrever-mensagem.html',
                           form=capsule_message_form)


@app.route('/excluir_mensagem/<int:capsule_message_id>')
@app.route('/excluir_mensagem/<int:capsule_message_id>/')
@login_required
def excluir_mensagem(capsule_message_id: int):
    if current_user.has_capsule_message_id(capsule_message_id):
        current_user.delete_capsule_message(capsule_message_id)
        return redirect(url_for('dashboard'))
    else:
        return (
            render_template('http_403_forbidden.html'),
            werkzeug.exceptions.Forbidden().code
        )
