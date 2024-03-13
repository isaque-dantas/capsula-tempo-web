from app import app, login_manager
from flask import render_template, redirect, flash, url_for, abort, request
from flask_login import AnonymousUserMixin, login_required, login_user, logout_user, current_user

from app.forms import LoginForm, RegisterForm, TimegramForm, TimegramTitleForm, EditUserForm
from app.model import User, Timegram


# TODO: (nova feature) integrar Flask-Babel para deixar o site em inglês e português

# TODO: (nova feature) criar opção de cadastro de usuários por categoria (
#    pessoa física -> envio de timegrams para apenas um usuário,
#    empresa -> envio de timegrams para um grupo pré-determinado; criar grupos de pessoas (times)
#  )


def is_current_user_logged_in() -> bool:
    return not isinstance(current_user, AnonymousUserMixin)


@app.errorhandler(403)
def forbidden(e):
    return render_template(
        'http_error_code.html',
        current_user_is_logged_in=is_current_user_logged_in(),
        error_code=403,
        error_description='Você não tem permissão para acessar essa página.'
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template(
        'http_error_code.html',
        current_user_is_logged_in=is_current_user_logged_in(),
        error_code=404,
        error_description='A página que você tentou acessar não foi encontrada.'
    )


@app.errorhandler(405)
def page_not_found(e):
    return render_template(
        'http_error_code.html',
        current_user_is_logged_in=is_current_user_logged_in(),
        error_code=405,
        error_description='O método de acesso à página não é permitido.'
    )


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_current_user_logged_in():
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

    if request.method == 'POST':
        return redirect(url_for('login'))

    return render_template('login.html', form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        try:
            User.register(register_form)
        except Exception as e:
            flash(message=str(e), category='danger')
        else:
            # user = User.get_by_username(register_form.username.data)
            # profile_picture_filename = user.profile_picture_filename

            # profile_picture = request.files[register_form.profile_picture.name]
            # profile_picture_type = profile_picture.filename.rsplit('.', 1)[1].lower()
            #
            # profile_picture_filename = \
            #     url_for('static', filename=f'img/user/{register_form.username.data}.{profile_picture_type}')
            #
            # profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_picture_filename))
            # profile_picture.close()

            return redirect(url_for('login'))

    # if request.method == 'POST':
    #     return redirect(url_for('register'))

    return render_template('register-user.html', form=register_form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template(
        template_name_or_list='dashboard-timegrams.html',
        first_name=current_user.first_name,
        timegrams=current_user.get_timegrams(),
        enumerate=enumerate,
        format=format,
        current_user_username=current_user.username
    )


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/timegram/<int:timegram_id>', methods=['GET', 'POST'])
@app.route('/timegram/<int:timegram_id>/', methods=['GET', 'POST'])
@login_required
def access_timegram(timegram_id: int):
    if current_user.has_timegram_id(timegram_id):
        timegram = Timegram.get_by_id(timegram_id)

        timegram_title_form = TimegramTitleForm()
        if timegram_title_form.validate_on_submit():
            timegram.update_title(timegram_title_form.title.data)

        if request.method == 'POST':
            return redirect(url_for('access_timegram', timegram_id=timegram_id))

        return render_template(
            'dashboard-timegram-details.html',
            timegram=timegram,
            form=timegram_title_form,
            formatted_datetime_creation=timegram.get_formatted_datetime_creation(),
            user_already_can_read_timegram=current_user.already_can_read_timegram(timegram_id),
            number_of_timegram=current_user.get_number_of_timegram(timegram_id),
            current_user_username=current_user.username
        )
    else:
        abort(403)


@app.route('/register_timegram', methods=['GET', 'POST'])
def register_timegram():
    timegram_form = TimegramForm()

    if timegram_form.validate_on_submit():
        Timegram.register(timegram_form, current_user)
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        return redirect(url_for('register_timegram'))

    return render_template('register-timegram.html',
                           form=timegram_form)


@app.route('/delete_timegram/<int:timegram_id>')
@app.route('/delete_timegram/<int:timegram_id>/')
@login_required
def delete_timegram(timegram_id: int):
    if current_user.has_timegram_id(timegram_id):
        current_user.delete_timegram(timegram_id)
        return redirect(url_for('dashboard'))
    else:
        abort(403)


@app.route('/timegram_datetime_can_open/<int:timegram_id>', methods=['POST'])
@app.route('/timegram_datetime_can_open/<int:timegram_id>/', methods=['POST'])
@login_required
def timegram_datetime_can_open(timegram_id: int):
    if current_user.has_timegram_id(timegram_id):
        timegram = Timegram.get_by_id(timegram_id)
        return timegram.get_datetime_can_open_dict()
    else:
        abort(403)


@app.route('/user/<username>', methods=['GET', 'POST'])
@app.route('/user/<username>/', methods=['GET', 'POST'])
@login_required
def user_profile(username: str):
    if current_user.username == username:
        edit_user_form = EditUserForm()

        if edit_user_form.validate_on_submit():
            try:
                current_user.edit(edit_user_form)
            except AttributeError as err:
                flash(str(err), category='danger')

        if request.method == 'POST':
            return redirect(url_for('user_profile', username=current_user.username))

        return render_template(
            'user_profile.html',
            form=edit_user_form,
            user=current_user,
            current_user_username=current_user.username,
            format=format
        )
    else:
        abort(403)


@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
@app.route('/delete_user/<int:user_id>/', methods=['DELETE'])
@login_required
def delete_user(user_id: int):
    if current_user.id == user_id:
        current_user.delete()
        print('I\'m here!')

        flash('O usuário foi deletado com sucesso.', category='success')
        return redirect(url_for('login'))
    else:
        abort(403)


@app.route('/search_user', methods=['GET', 'POST'])
@login_required
def search_user():
    return redirect(url_for('dashboard'))
