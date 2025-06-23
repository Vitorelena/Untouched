from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

# Importe os serviços e modelos necessários
from ..service.UserDatabaseService import UserDatabaseService
from ..model.Users.User import User # Importe o modelo base User para verificações de existência
from ..model.Users.Ceo import Ceo   # Certifique-se de que Ceo esteja importado (se necessário aqui, ou só no service)

signC = Blueprint('signC', __name__)

# --- Rota de Login (apenas um placeholder, complete com sua lógica real) ---
@signC.route('/login_page', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        login = request.form.get('login')
        senha = request.form.get('senha')
        remember = True if request.form.get('remember') else False # Exemplo de "lembrar-me"

        user = User.query.filter_by(login=login).first()

        # Verifica se o usuário existe e a senha está correta
        if user and check_password_hash(user.senha, senha):
            login_user(user, remember=remember)
            print('Login realizado com sucesso!', 'success')
            # Redireciona para a home específica após o login
            if user.tipo_usuario == 2:
                return redirect(url_for('homeC.home_cliente'))
            elif user.tipo_usuario >= 3: # Assumindo que 3+ são funcionários
                return redirect(url_for('homeC.home_funcionario'))
            else:
                return redirect(url_for('homeC.home')) # Home padrão
        else:
            print('Login ou senha inválidos.', 'danger')

    return render_template('login.html') # Você deve ter um template 'login.html'

# --- Rota de Logout ---
@signC.route('/logout')
@login_required # Garante que apenas usuários logados possam deslogar
def logout():
    logout_user()
    print('Você foi desconectado(a).', 'info')
    return redirect(url_for('homeC.home')) # Redireciona para a home padrão

# --- Rota de Cadastro Geral (Cliente, Funcionário) ---
@signC.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        login = request.form.get('login')
        senha_insegura = request.form.get('senha')
        confirm_senha = request.form.get('confirm_senha') # Campo para confirmar senha

        # 1. Validação de Senha
        if senha_insegura != confirm_senha:
            print('As senhas não coincidem!', 'danger')
            return render_template('sign_up.html') # Retorna ao formulário

        hashed_senha = generate_password_hash(senha_insegura) # Gerar hash da senha

        # 2. Verificação de Usuário Existente (Login ou CPF)
        user_exists = User.query.filter_by(login=login).first() or \
                      User.query.filter_by(cpf=cpf).first()
        if user_exists:
            print('Login ou CPF já cadastrados. Por favor, use outros dados.', 'danger')
            return render_template('sign_up.html') # Retorna ao formulário

        # 3. Processamento por Tipo de Usuário
        # O valor do campo 'tipo_usuario' virá como string, converta para int
        try:
            tipo_usuario = int(request.form.get('tipo_usuario'))
        except (ValueError, TypeError):
            print("Tipo de usuário inválido selecionado.", 'danger')
            return render_template('sign_up.html')

        novo_usuario_cadastrado = None # Variável para armazenar o objeto usuário criado

        if tipo_usuario == 2: # Cliente
            novo_usuario_cadastrado = UserDatabaseService.adicionar_cliente(
                nome=nome,
                cpf=cpf,
                login=login,
                senha=hashed_senha # Passa a senha hashed
            )
            if novo_usuario_cadastrado:
                print(f"Cliente '{nome}' cadastrado com sucesso!", 'success')
                login_user(novo_usuario_cadastrado, remember=True) # Loga o cliente automaticamente
                return redirect(url_for('homeC.home_cliente')) # Redireciona para home do cliente
            else:
                print("Erro ao cadastrar o cliente. Verifique os dados e tente novamente.", 'danger')
        
        elif tipo_usuario == 3: # Funcionário (Staff, SubGerente, Gerente)
            # O valor do campo 'nivel_funcionario' virá como string, converta para int
            try:
                nivel_funcionario = int(request.form.get('nivel_funcionario'))
            except (ValueError, TypeError):
                print("Nível de funcionário inválido selecionado.", 'danger')
                return render_template('sign_up.html')

            matricula = request.form.get('matricula')
            
            if nivel_funcionario == 1: # Staff
                novo_usuario_cadastrado = UserDatabaseService.adicionar_staff(
                    nome=nome, cpf=cpf, login=login, senha=hashed_senha, matricula=matricula
                )
            elif nivel_funcionario == 2: # Sub-Gerente
                novo_usuario_cadastrado = UserDatabaseService.adicionar_subgerente(
                    nome=nome, cpf=cpf, login=login, senha=hashed_senha, matricula=matricula
                )
            elif nivel_funcionario == 3: # Gerente
                novo_usuario_cadastrado = UserDatabaseService.adicionar_gerente(
                    nome=nome, cpf=cpf, login=login, senha=hashed_senha, matricula=matricula
                )
            else:
                print("Nível de funcionário inválido.", 'danger') # Nível numérico fora do range 1-3
                return render_template('sign_up.html')

            if novo_usuario_cadastrado:
                print(f"Funcionário '{nome}' (Nível {nivel_funcionario}) cadastrado com sucesso!", 'success')
                login_user(novo_usuario_cadastrado, remember=True) # Loga o funcionário automaticamente
                return redirect(url_for('homeC.home_funcionario')) # Redireciona para home do funcionário
            else:
                print("Erro ao cadastrar o funcionário. Verifique a matrícula ou outros dados.", 'danger')
        else: # Tipo de usuário (2 ou 3) inválido.
            print("Tipo de usuário inválido selecionado.", 'danger')

        # Se houver alguma falha não coberta pelos redirects anteriores
        return render_template("sign_up.html")

    # Para requisições GET, renderiza o formulário
    return render_template("sign_up.html")

# --- Rota de Cadastro de CEO (exclusiva) ---
@signC.route('/sign_up_ceo', methods=['GET', 'POST'])
def sign_up_ceo():
    # CUIDADO: Em uma aplicação real e segura, você só permitiria criar um CEO
    # se não houver CEOs existentes, ou se a requisição viesse de um super-administrador já logado.
    # Por enquanto, esta rota está aberta para facilitar o teste inicial de cadastro do CEO.

    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        matricula = request.form.get('matricula')
        login = request.form.get('login')
        senha = request.form.get('senha')
        confirm_senha = request.form.get('confirm_senha')

        if senha != confirm_senha:
            print('As senhas não coincidem!', 'danger')
            return render_template('sign_up_ceo.html')

        # Verifique se o login ou CPF já existem no banco de dados
        user_exists = User.query.filter_by(login=login).first() or \
                      User.query.filter_by(cpf=cpf).first()
        if user_exists:
            print('Login ou CPF já cadastrados. Por favor, use outros dados.', 'danger')
            return render_template('sign_up_ceo.html')

        hashed_senha = generate_password_hash(senha) # HASHEAR A SENHA!

        try:
            novo_ceo = UserDatabaseService.adicionar_ceo(
                nome=nome,
                cpf=cpf,
                login=login,
                senha=hashed_senha, # Passa a senha hashed
                matricula=matricula
            )

            if novo_ceo:
                print('Conta de CEO criada com sucesso! Você foi logado(a) automaticamente.', 'success')
                login_user(novo_ceo, remember=True) # Loga o CEO automaticamente
                return redirect(url_for('homeC.home_funcionario')) # CEO geralmente vai para painel de funcionario/admin
            else:
                print('Não foi possível criar a conta de CEO. Tente novamente.', 'danger')
                return render_template('sign_up_ceo.html')
        except Exception as e:
            print(f'Ocorreu um erro inesperado ao criar a conta: {e}', 'danger')
            print(f"Erro ao adicionar CEO: {e}") # Para depuração no console
            return render_template('sign_up_ceo.html')

    return render_template('sign_up_ceo.html')