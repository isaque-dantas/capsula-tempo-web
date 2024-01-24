from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)


class User(db.Model):
    MAX_LENGTH = {
        'email': 100,
        'first_name': 30,
        'last_name': 30,
        'password': 20
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(MAX_LENGTH['email']), nullable=False, unique=True)
    first_name = db.Column(db.String(MAX_LENGTH['first_name']), nullable=False)
    last_name = db.Column(db.String(MAX_LENGTH['last_name']), nullable=False)
    password = db.Column(db.String(MAX_LENGTH['password']), nullable=False)
    capsule_messages = db.relationship('CapsuleMessage', backref='user')

    @staticmethod
    def register_form(form):
        if not User.__is_email_already_registered(form.email.data):
            user = User(email=form.email.data,
                        first_name=form.first_name.data,
                        last_name=form.last_name.data,
                        password=form.password.data)
            db.session.add(user)
            db.session.commit()
        else:
            raise ValueError('O e-mail já foi registrado')

    @staticmethod
    def __is_email_already_registered(email) -> bool:
        return User.query.filter_by(email=email).first() is not None

    @staticmethod
    def is_password_valid(form) -> bool:
        right_password = User.__get_password_by_email(form.email.data)

        return str(form.password.data) == str(right_password)

    @staticmethod
    def __get_password_by_email(email: str) -> str:
        user_data = User.query.with_entities(User.password).filter_by(email=email).first()
        password = user_data[0]
        return password


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


# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
