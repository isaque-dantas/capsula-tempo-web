import datetime

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
    timegrams = db.relationship('Timegram', backref='user')

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
    def get_by_id(user_id: int):
        return User.query.filter_by(id=user_id).first()

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
        return self.get_timegrams() is not None

    def get_timegrams(self) -> list:
        return Timegram.query.filter_by(user_id=self.id).all()

    def has_timegram_id(self, timegram_id: int) -> bool:
        timegram = Timegram.query.get_or_404(timegram_id)
        if timegram is not None:
            timegram_user_id = timegram.user_id
            return timegram_user_id == self.id
        else:
            return False

    @staticmethod
    def already_can_read_timegram(timegram_id: int) -> bool:
        timegram = Timegram.get_by_id(timegram_id)
        now = datetime.datetime.utcnow()

        return now >= timegram.datetime_can_open

    @staticmethod
    def delete_timegram(timegram_id: int):
        timegram = Timegram.get_by_id(timegram_id)
        db.session.delete(timegram)
        db.session.commit()

    def get_number_of_timegram(self, timegram_id: int) -> int:
        timegrams_ids = self.get_timegrams_ids()
        index_of_timegram = timegrams_ids.index(timegram_id)
        number_of_timegram = index_of_timegram + 1
        return number_of_timegram

    def get_timegrams_ids(self) -> list:
        timegrams_ids_list_of_tuples = \
            Timegram.query.with_entities(Timegram.id).filter_by(
                user_id=self.id
            ).all()

        timegrams_ids_list = []
        for timegram_id in timegrams_ids_list_of_tuples:
            timegrams_ids_list.append(*timegram_id)

        return timegrams_ids_list


class Timegram(db.Model):
    MAX_LENGTH = {
        'title': 70
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(MAX_LENGTH['title']), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    datetime_creation = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow)
    datetime_can_open = db.Column(db.DateTime(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @staticmethod
    def register(form, current_user):
        datetime_can_open = Timegram.convert_form_datetime_to_datetime(
            form.date_can_open.data,
            form.time_can_open.data
        )
        datetime_can_open_utc = Timegram.convert_datetime_to_utc_datetime(datetime_can_open)
        timegram = Timegram(title=form.title.data,
                            content=form.content.data,
                            datetime_can_open=datetime_can_open_utc,
                            user_id=current_user.id)
        db.session.add(timegram)
        db.session.commit()

        flash('O Timegram foi registrada com sucesso.', 'success')

    @staticmethod
    def get_by_id(timegram_id: int):
        return Timegram.query.filter_by(id=timegram_id).first()

    def update_title(self, new_title: str):
        self.title = new_title
        db.session.commit()

    @staticmethod
    def convert_form_datetime_to_datetime(date, time) -> datetime.datetime:
        str_datetime = f'{date} {time}'
        return datetime.datetime.strptime(str_datetime, '%Y-%m-%d %H:%M:%S')

    @property
    def datetime_creation_local_timezone(self) -> datetime.datetime:
        return self.convert_utc_datetime_to_datetime(self.datetime_creation)

    @datetime_creation_local_timezone.setter
    def datetime_creation_local_timezone(self, value: datetime.datetime):
        self.datetime_creation = self.convert_datetime_to_utc_datetime(value)

    @property
    def datetime_can_open_local_timezone(self) -> datetime.datetime:
        return self.convert_utc_datetime_to_datetime(self.datetime_can_open)

    @datetime_can_open_local_timezone.setter
    def datetime_can_open_local_timezone(self, value: datetime.datetime):
        self.datetime_can_open = self.convert_datetime_to_utc_datetime(value)

    @staticmethod
    def convert_datetime_to_utc_datetime(dt: datetime.datetime) -> datetime.datetime:
        return dt.astimezone(datetime.timezone.utc)

    @staticmethod
    def convert_utc_datetime_to_datetime(dt: datetime.datetime) -> datetime.datetime:
        converted_datetime = dt + dt.astimezone().tzinfo.utcoffset(dt)
        return converted_datetime

    def get_formatted_datetime_creation(self):
        print(self.datetime_creation_local_timezone)
        return self.get_formatted_datetime(self.datetime_creation_local_timezone)

    @staticmethod
    def get_formatted_datetime(dt: datetime.datetime) -> dict:
        date_and_time = Timegram.convert_datetime_to_date_and_time(dt)
        date = date_and_time['date']
        time = date_and_time['time']

        formatted_date = Timegram.get_formatted_date(date)
        formatted_time = Timegram.get_formatted_time(time)

        return {
            'formatted_date': formatted_date,
            'formatted_time': formatted_time
        }

    @staticmethod
    def convert_datetime_to_date_and_time(dt: datetime.datetime) -> dict:
        date = datetime.date(year=dt.year, month=dt.month, day=dt.day)
        time = datetime.time(hour=dt.hour, minute=dt.minute, second=dt.second)

        return {
            'date': date,
            'time': time
        }

    @staticmethod
    def get_formatted_date(dt: datetime.date) -> str:
        return dt.strftime('%d/%m/%Y')

    @staticmethod
    def get_formatted_time(time: datetime.time) -> str:
        return time.strftime('%H:%M')


# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
