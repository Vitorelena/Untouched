from flask import Blueprint,render_template, request, redirect, url_for
import folium
from .. import db
from ..model.Loja import Loja
from ..model.Users.Cliente import Cliente
from ..model.Produtos.Produto import Produto
from sqlalchemy.orm import joinedload
from ..service.ProdutoDatabaseService import ProdutoDatabaseService
from ..service.UserDatabaseService import UserDatabaseService
from ..service.LojaDatabaseService import LojaDatabaseService
from flask_login import current_user, login_required


homeC = Blueprint('homeC', __name__)

@homeC.route('/teste')
def teste():
    return render_template("layout.html")

@homeC.route('/', defaults={'categoria_id': None})
@homeC.route('/categoria/<int:categoria_id>')
def home(categoria_id):
    lojas = Loja.query.all()
    map_center = [-19.92083, -43.93778]
    m = folium.Map(location=map_center, zoom_start=10)

    for loja in lojas:
        folium.Marker(
            location = [loja.latitude, loja.longitude],
            popup=f"<strong>{loja.nome}</strong><br>{loja.endereco}").add_to(m)
    
    map_html = m._repr_html_()

    categoria_templates = {
        1: 'feminino',  # Assumindo que 1 é 'VestuarioFeminino'
        2: 'masculino', # Assumindo que 2 é 'VestuarioMasculino'
        3: 'calcados',   # Assumindo que 3 é 'Calcados'
        4: 'esportivos', # Assumindo que 4 é 'EquipamentosEsportivos'
        5: 'suplementos', # Corresponde ao seu 'Suplementos' com identity 5
        6: 'outros'      # Assumindo que 6 é 'Outros'
    }
    produtos_em_estoque = []
    todos_produtos = ProdutoDatabaseService.get_todos_produtos()
    for produto in todos_produtos:
        produto_com_estoque = db.session.query(Produto).options(joinedload(Produto.estoque)).filter_by(id=produto.id).first()
        if produto_com_estoque and produto_com_estoque.estoque and produto_com_estoque.estoque.quantidade > 0:
            produtos_em_estoque.append(produto_com_estoque)

    if categoria_id and categoria_id in categoria_templates:
        nome_template = categoria_templates[categoria_id] + '.html'
        produtos_categoria = ProdutoDatabaseService.get_produtos_por_categoria(categoria_id)
        produtos_com_estoque_categoria = []
        for produto in produtos_categoria:
            produto_estoque = db.session.query(Produto).options(joinedload(Produto.estoque)).filter_by(id=produto.id).first()
            if produto_estoque:
                produtos_com_estoque_categoria.append(produto_estoque)
        return render_template(nome_template, produtos=produtos_com_estoque_categoria, produtos_estoque_home=produtos_em_estoque)
    else:
        return render_template("home.html", map_html = map_html, produtos_estoque_home=produtos_em_estoque)

@homeC.route('/home_cliente')
def home_cliente():
    produtos_em_estoque = []
    todos_produtos = ProdutoDatabaseService.get_todos_produtos()
    for produto in todos_produtos:
        produto_com_estoque = db.session.query(Produto).options(joinedload(Produto.estoque)).filter_by(id=produto.id).first()
        if produto_com_estoque and produto_com_estoque.estoque and produto_com_estoque.estoque.quantidade > 0:
            produtos_em_estoque.append(produto_com_estoque)
    relatorio = current_user.gerar_relatorio()
    return render_template("home_cliente.html", current_user=current_user, relatorio=relatorio, produtos_estoque_home=produtos_em_estoque)

@homeC.route('/home_funcionario')
def home_funcionario():
    produtos_em_estoque = []
    todos_produtos = ProdutoDatabaseService.get_todos_produtos()
    for produto in todos_produtos:
        produto_com_estoque = db.session.query(Produto).options(joinedload(Produto.estoque)).filter_by(id=produto.id).first()
        if produto_com_estoque and produto_com_estoque.estoque and produto_com_estoque.estoque.quantidade > 0:
            produtos_em_estoque.append(produto_com_estoque)
    relatorio = current_user.gerar_relatorio()
    return(render_template("home_funcionario.html",current_user=current_user, relatorio=relatorio, produtos_estoque_home=produtos_em_estoque))

@homeC.route('/gerenciar_funcionarios', methods=['GET'])
@login_required
def gerenciar_funcionarios():
    # Apenas o CEO (nível 4) pode acessar esta página
    if not (current_user.is_authenticated and current_user.nivel == 4):
        print("Você não tem permissão para visualizar a lista de funcionários.", 'danger')
        return redirect(url_for('homeC.home_funcionario')) # Redireciona para o painel de funcionario

    funcionarios = UserDatabaseService.listar_funcionarios() # Obtenha todos os funcionários

    return render_template('gerenciar_funcionarios.html', funcionarios=funcionarios)

@homeC.route('/promover_funcionario_page', methods=['GET'])
@login_required
def promover_funcionario_page():
    # Apenas o CEO (nível 4) pode acessar esta página
    if not (current_user.is_authenticated and current_user.nivel == 4):
        print("Você não tem permissão para gerenciar promoções de funcionários.", 'danger')
        return redirect(url_for('homeC.home_funcionario'))

    # Lista funcionários elegíveis para promoção (excluindo CEO)
    funcionarios_promocao = UserDatabaseService.listar_funcionarios(exclude_ceo=True)

    return render_template('promover_funcionario.html', funcionarios=funcionarios_promocao)

@homeC.route('/promover_funcionario_action/<int:funcionario_id>', methods=['POST'])
@login_required
def promover_funcionario_action(funcionario_id):
    # Apenas o CEO (nível 4) pode realizar esta ação
    if not (current_user.is_authenticated and current_user.nivel == 4):
        print("Você não tem permissão para realizar promoções de funcionários.", 'danger')
        return redirect(url_for('homeC.home_funcionario'))
    
    success, message = UserDatabaseService.promover_funcionario(funcionario_id)
    if success:
        print(message, 'success')
    else:
        print(message, 'danger')
    
    return redirect(url_for('homeC.promover_funcionario_page'))
@homeC.route('/desligar_funcionario_page', methods=['GET'])
@login_required
def desligar_funcionario_page():
    # Apenas o CEO (nível 4) pode acessar esta página
    if not (current_user.is_authenticated and current_user.nivel == 4):
        print("Você não tem permissão para desligar funcionários.", 'danger')
        return redirect(url_for('homeC.home_funcionario'))

    # Lista todos os funcionários exceto o próprio CEO (CEO não pode desligar a si mesmo)
    funcionarios_desligamento = UserDatabaseService.listar_funcionarios(exclude_ceo=True) 
    funcionarios_desligamento = [f for f in funcionarios_desligamento if f.id != current_user.id]

    return render_template('desligar_funcionario.html', funcionarios=funcionarios_desligamento)

@homeC.route('/desligar_funcionario_action/<int:funcionario_id>', methods=['POST'])
@login_required
def desligar_funcionario_action(funcionario_id):
    # Apenas o CEO (nível 4) pode realizar esta ação
    if not (current_user.is_authenticated and current_user.nivel == 4):
        print("Você não tem permissão para realizar esta ação.", 'danger')
        return redirect(url_for('homeC.home_funcionario'))
    
    # Converte o ID para inteiro
    try:
        funcionario_id = int(funcionario_id)
    except (ValueError, TypeError):
        print("ID de funcionário inválido.", 'danger')
        return redirect(url_for('homeC.desligar_funcionario_page'))

    # O CEO não pode desligar a si mesmo
    if funcionario_id == current_user.id:
        print("Você não pode desligar sua própria conta de CEO.", 'danger')
        return redirect(url_for('homeC.desligar_funcionario_page'))

    success, message = UserDatabaseService.deletar_usuario_funcionario(funcionario_id)
    if success:
        print(message, 'success')
    else:
        print(message, 'danger')
    
    # Redireciona de volta para a página de listagem de desligamento
    return redirect(url_for('homeC.desligar_funcionario_page'))

@homeC.route('/gerenciar_unidades_page', methods=['GET', 'POST'])
@login_required
def gerenciar_unidades_page():
    # Apenas o CEO (nível 4) pode acessar esta página
    if not (current_user.is_authenticated and current_user.nivel == 4):
        print("Você não tem permissão para gerenciar unidades.", 'danger')
        return redirect(url_for('homeC.home_funcionario'))

    # Para GET: Exibe a lista de unidades
    if request.method == 'GET':
        lojas = LojaDatabaseService.listar_lojas()
        return render_template('gerenciar_unidades.html', lojas=lojas)

    # Para POST: Processa as ações de gerenciamento de unidades
    if request.method == 'POST':
        action = request.form.get('action')
        loja_id = request.form.get('loja_id')

        try:
            loja_id = int(loja_id)
        except (ValueError, TypeError):
            print("ID da loja inválido.", 'danger')
            return redirect(url_for('homeC.gerenciar_unidades_page'))

        if action == 'excluir_unidade':
            success = LojaDatabaseService.excluir_loja(loja_id)
            if success:
                print(f"Unidade ID {loja_id} excluída com sucesso.", 'success')
            else:
                print(f"Erro ao excluir unidade ID {loja_id}.", 'danger')
        # Adicione aqui outras ações POST como 'adicionar unidade', 'editar unidade', etc.

        return redirect(url_for('homeC.gerenciar_unidades_page'))
    
@homeC.route('/sign_up_loja', methods=['GET', 'POST'])
@login_required
def sign_up_loja():
    # Apenas o CEO (nível 4) pode cadastrar novas unidades
    if not (current_user.is_authenticated and current_user.nivel == 4):
        print("Você não tem permissão para cadastrar novas unidades.", 'danger')
        return redirect(url_for('homeC.home_funcionario')) # Redireciona para o painel de funcionario

    if request.method == 'POST':
        nome = request.form.get('nome')
        endereco = request.form.get('endereco')
        cnpj = request.form.get('cnpj')
        
        # Latitude e Longitude podem vir como string, converta para float
        try:
            latitude = float(request.form.get('latitude'))
            longitude = float(request.form.get('longitude'))
        except (ValueError, TypeError):
            print("Latitude e Longitude devem ser números válidos.", 'danger')
            return render_template('sign_up_loja.html')

        nova_loja = LojaDatabaseService.adicionar_loja(
            nome=nome,
            endereco=endereco,
            cnpj=cnpj,
            latitude=latitude,
            longitude=longitude
        )

        if nova_loja:
            print(f"Unidade '{nova_loja.nome}' cadastrada com sucesso!", 'success')
            return redirect(url_for('homeC.gerenciar_unidades_page')) # Redireciona para a página de gerenciamento
        else:
            print("Erro ao cadastrar a unidade. Verifique os dados (CNPJ pode já existir).", 'danger')
            return render_template('sign_up_loja.html')

    return render_template('sign_up_loja.html')