from flask import Blueprint, render_template, request, redirect, url_for
from ..model.Users.Cliente import Cliente
from ..service.UserDatabaseService import UserDatabaseService
from ..service.VendaDatabaseService import VendaDatabaseService
from ..service.ProdutoDatabaseService import ProdutoDatabaseService
from flask_login import current_user, login_required

clienteC = Blueprint('clienteC', __name__)

@clienteC.route('/cliente/editar/<int:usuario_id>', methods=['GET', 'POST'])
def editar_cliente(usuario_id):
    cliente = Cliente.query.get(usuario_id)
    if not cliente or cliente.tipo_usuario != 2:
        return "Cliente não encontrado ou inválido", 404

    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        login = request.form.get('login')
        senha = request.form.get('senha')
        numero_compras = request.form.get('numero_compras')

        # Converte numero_compras para int ou None
        if numero_compras == '' or numero_compras is None:
            numero_compras = None
        else:
            try:
                numero_compras = int(numero_compras)
            except ValueError:
                numero_compras = None

        sucesso = UserDatabaseService.editar_cliente(
            usuario_id,
            nome=nome if nome != '' else None,
            cpf=cpf if cpf != '' else None,
            login=login if login != '' else None,
            senha=senha if senha != '' else None,
            numero_compras=numero_compras
        )
        if sucesso:
            return render_template('editar_cliente.html', cliente=cliente, sucesso=True)
        else:
            return render_template('editar_cliente.html', cliente=cliente, erro=True)

    return render_template('editar_cliente.html', cliente=cliente)

@clienteC.route('/cliente/historico_compras')
def historico_compras():
    cliente_id = current_user.id
    vendas = VendaDatabaseService.buscar_historico_compras(cliente_id)

    historico = []
    for venda in vendas:
        nome_funcionario = "Compra online"
        if venda.funcionario_id:
            nome = UserDatabaseService.get_nome_por_id(venda.funcionario_id)
            if nome:
                nome_funcionario = nome

        historico.append({
            'data_venda': venda.data_venda,
            'nome_funcionario': nome_funcionario
        })

    return render_template("historico_compras.html", historico=historico)

@clienteC.route('/cliente/historico_pedidos')
@login_required
def lista_pedidos():
    cliente_id = current_user.id
    vendas = VendaDatabaseService.venda_por_cliente(cliente_id)

    itens_por_venda = {}
    nomes_produtos = {}

    for venda in vendas:
        itens = VendaDatabaseService.get_itens_by_venda(venda.id)
        itens_por_venda[venda.id] = itens

        for item in itens:
            pid = item.produto_id
            if pid not in nomes_produtos:
                nomes_produtos[pid] = ProdutoDatabaseService.get_nome_por_id(pid)

    return render_template('lista_pedidos.html', vendas=vendas, itens_por_venda=itens_por_venda, nomes_produtos=nomes_produtos)