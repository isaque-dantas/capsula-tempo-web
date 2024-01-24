from flask import Flask

app = Flask(__name__, static_folder='../static', template_folder='../templates')
app.config['SECRET_KEY'] = 'lumenlearn'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'

if __name__ == '__main__':
    app.run()
