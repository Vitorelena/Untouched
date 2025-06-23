from flask import Blueprint,render_template, request, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required, login_manager
from ..model.Users.User import User
from werkzeug.security import check_password_hash
from .. import db

loginC = Blueprint('loginC', __name__)

@loginC.route('/login', methods=['GET','POST'])
def login_page():
    if current_user.is_authenticated:
        return(redirect(url_for('homeC.home')))
    if request.method == 'POST':
        data = request.form
        login = data.get('login')
        senha = data.get('senha')
        remember = data.get('remember') is not None
        if not login or not senha:
            return render_template("login.html", error="Por favor, preencha todos os campos.")
        user = User.query.filter_by(login = login).first()
        print(f"Usuário encontrado no banco de dados: {user}")
        if user:
            print(f"Senha armazenada (hash): {user.senha}") # Adicione este log
            print(f"Senha digitada (texto plano): {senha}")
        if user and check_password_hash(user.senha, senha):
            login_user(user, remember=remember)
            if user.tipo_usuario == 2:
                return redirect(url_for('homeC.home_cliente'))
            elif user.tipo_usuario >= 3:
                return redirect(url_for('homeC.home_funcionario'))
            else:
                print("Usuario invalido")
        else:
            print("Login ou senha inválidos.")
            return render_template("login.html")
                    
    return render_template("login.html")
@loginC.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('homeC.home'))