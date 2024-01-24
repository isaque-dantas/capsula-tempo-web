from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from app import app

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def register_form(self, form):
        if not self.__is_email_already_registered(form.email.data):
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
        right_password = User.query.with_entities(User.password).filter_by(email=form.email.data).first()

        return str(form.password.data) == str(right_password)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
