from datetime import datetime, timezone

from flask import flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash
from pymysql.err import IntegrityError

from app import app

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    MAX_LENGTH = {
        'username': 20,
        'email': 100,
        'first_name': 30,
        'last_name': 30,
        'password': 8,
        'password_hash': 256
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(MAX_LENGTH['email']), nullable=False, unique=True)
    first_name = db.Column(db.String(MAX_LENGTH['first_name']), nullable=False)
    last_name = db.Column(db.String(MAX_LENGTH['last_name']), nullable=False)
    password_hash = db.Column(db.String(MAX_LENGTH['password_hash']), nullable=False)
    capsule_messages = db.relationship('CapsuleMessage', backref='user')

    @property
    def password(self):
        raise AttributeError('Não é possível obter o valor da senha.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @staticmethod
    def register(form):
        already_registered_form_attributes = \
            User.get_already_registered_form_attributes(username=form.username.data, email=form.email.data)
        # raise ValueError(already_registered_form_attributes)

        if already_registered_form_attributes:
            integrity_error_message = User.generate_integrity_error_message(already_registered_form_attributes)
            raise IntegrityError(integrity_error_message)

        user = User(username=form.username.data,
                    email=form.email.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def get_already_registered_form_attributes(username: str, email: str) -> list:
        unique_attributes = [
            {
                'name': 'nome de usuário',
                'value': username,
                'verification_method': User.__is_username_already_registered
            },
            {
                'name': 'email',
                'value': email,
                'verification_method': User.__is_email_already_registered
            },
        ]

        already_registered_form_attributes = []

        for unique_attribute in unique_attributes:
            unique_attribute_name = unique_attribute['name']
            unique_attribute_value = unique_attribute['value']
            is_attribute_already_registered = unique_attribute['verification_method']

            if is_attribute_already_registered(unique_attribute_value):
                already_registered_form_attributes.append(unique_attribute_name)

        return already_registered_form_attributes

    @staticmethod
    def generate_integrity_error_message(already_registered_form_attributes: list) -> str:
        integrity_error_message = ''
        attributes = ''

        if len(already_registered_form_attributes) == 1:
            integrity_error_message = 'O atributo "{}" já foi registrado. Insira outro valor.'
            attributes = str(already_registered_form_attributes[0])
        elif len(already_registered_form_attributes) >= 2:
            integrity_error_message = 'Os atributos "{}" já foram registrados. Insira outros valores.'
            attributes = '", "'.join(already_registered_form_attributes[:-1])
            attributes += '" e "' + already_registered_form_attributes[-1]

        return integrity_error_message.format(attributes)

    @staticmethod
    def __is_email_already_registered(email) -> bool:
        return User.get_by_email(email) is not None

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def __is_username_already_registered(username) -> bool:
        return User.get_by_username(username) is not None

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    def is_password_valid(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def already_registered_any_message(self) -> bool:
        return self.get_capsule_messages() is not None

    def get_capsule_messages(self) -> list:
        return CapsuleMessage.query.filter_by(user_id=self.id).all()

    def has_capsule_message_id(self, capsule_message_id: int) -> bool:
        capsule_message = CapsuleMessage.query.get_or_404(capsule_message_id)
        if capsule_message is not None:
            capsule_message_user_id = capsule_message.user_id
            return capsule_message_user_id == self.id
        else:
            return False

    @staticmethod
    def can_read_capsule_message(capsule_message_id: int) -> bool:
        capsule_message = CapsuleMessage.get_by_id(capsule_message_id)
        now = datetime.utcnow()

        return now >= capsule_message.datetime_can_open

    @staticmethod
    def delete_capsule_message(capsule_message_id: int):
        capsule_message = CapsuleMessage.query.get(capsule_message_id)
        db.session.delete(capsule_message)
        db.session.commit()


#     TODO: implementar método que consiga enumerar a 'capsule_message' atual baseado na contagem das que foram
#           criadas pelo mesmo usuário (ordenando por id), sem usar o id delas (do contrário, por ex se o usuário
#           tiver três mensagens, uma delas poderá ter 'id' igual a 20)


class CapsuleMessage(db.Model):
    MAX_LENGTH = {
        'title': 70
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(MAX_LENGTH['title']), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    datetime_creation = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    datetime_can_open = db.Column(db.DateTime(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @staticmethod
    def register(form, current_user):
        # flash(str_date_can_open, 'info')
        # flash(str_time_can_open, 'info')

        datetime_can_open = CapsuleMessage.convert_form_datetime_to_datetime(
            form.date_can_open.data,
            form.time_can_open.data
        )
        datetime_can_open_utc = CapsuleMessage.convert_datetime_to_utc(datetime_can_open)

        capsule_message = CapsuleMessage(title=form.title.data,
                                         content=form.content.data,
                                         datetime_can_open=datetime_can_open_utc,
                                         user_id=current_user.id)
        db.session.add(capsule_message)
        db.session.commit()

        flash('A mensagem foi registrada com sucesso.', 'success')

    @staticmethod
    def convert_form_datetime_to_datetime(date, time) -> datetime:
        str_datetime = f'{date} {time}'
        return datetime.strptime(str_datetime, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def convert_datetime_to_utc(dt: datetime) -> datetime:
        return dt.astimezone(timezone.utc)

    @staticmethod
    def get_by_id(capsule_message_id: int):
        return CapsuleMessage.query.filter_by(id=capsule_message_id).first()

    def update_title(self, new_title: str):
        self.title = new_title
        db.session.commit()

#     TODO: implementar método que converta um objeto utc_datetime para datetime na zona atual

#     TODO: implementar método que converta um objeto datetime para string, segundo o padrão brasileiro,
#           com opção de escolher entre 'date' ou 'time' (mudar a string de formatação para fazer isso)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
