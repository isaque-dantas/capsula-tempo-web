from flask import Flask
from flask_login import LoginManager
from app.secret_keys import FLASK_SECRET_KEY, MYSQL_USER_PASSWORD

app = Flask(__name__, static_folder='../static', template_folder='../templates')
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'mysql+pymysql://capsula_tempo_web_pycharm:{MYSQL_USER_PASSWORD}@localhost/capsula_tempo_web'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

if __name__ == '__main__':
    app.run()
