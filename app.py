from flask import Flask
from flask import render_template

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/')
@app.route('/index')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')


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


if __name__ == '__main__':
    app.run()
