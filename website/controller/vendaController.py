from flask import Blueprint, session, render_template, redirect, url_for, request
from ..model.Vendas.CarrinhoDeCompras import CarrinhoDeCompras
from ..service.ProdutoDatabaseService import ProdutoDatabaseService
from ..model.Vendas.Venda import Venda
from ..model.Vendas.ItemVendido import ItemVendido
from website import db
from flask_login import current_user, login_required
from ..service.UserDatabaseService import UserDatabaseService
from website.model.Vendas.ProcessadorDeCompraDireta import ProcessadorDeCompraDireta


vendaC = Blueprint('vendaC', __name__)

def obter_carrinho():
    if 'carrinho' not in session:
        session['carrinho'] = CarrinhoDeCompras().itens
    carrinho = CarrinhoDeCompras()
    carrinho.itens = session['carrinho']
    return carrinho

def salvar_carrinho(carrinho):
    session['carrinho'] = carrinho.itens

@vendaC.route('/adicionar_ao_carrinho/<int:produto_id>', methods=['POST'])
def adicionar_ao_carrinho(produto_id):
    carrinho = obter_carrinho()
    quantidade = int(request.form.get('quantidade', 1))
    carrinho.adicionar_item(produto_id, quantidade)
    salvar_carrinho(carrinho)
    if current_user.tipo_usuario == 2:
        return redirect(url_for('vendaC.carrinho'))
    elif current_user.tipo_usuario > 3:
        return redirect(url_for('vendaC.carrinho_venda'))

@vendaC.route('/remover_do_carrinho/<int:produto_id>')
def remover_do_carrinho(produto_id):
    carrinho = obter_carrinho()
    carrinho.remover_item(produto_id)
    salvar_carrinho(carrinho)
    return redirect(url_for('vendaC.carrinho'))

@vendaC.route('/atualziar_quantidade/<int:produto_id>', methods=['POST'])
def atualizar_quantidade(produto_id):
    carrinho = obter_carrinho()
    quantidade = int(request.form.get('quantidade'))    
    carrinho.atualizar_quantidade(produto_id, quantidade)
    salvar_carrinho(carrinho)
    return redirect(url_for('vendaC.carrinho'))

@vendaC.route('/carrinho')
def carrinho():
    carrinho = obter_carrinho()
    produtos_no_carrinho = []
    produto_service = ProdutoDatabaseService()
    for produto_id, quantidade in carrinho.obter_itens().items():
        produto = produto_service.get_produto_por_id(int(produto_id))
        if produto:
            produtos_no_carrinho.append({'produto': produto, 'quantidade': quantidade})
    total = carrinho.calcular_total(produto_service)
    return render_template('carrinho.html', carrinho=produtos_no_carrinho, total=total)

@vendaC.route('/carrinho_venda')
@login_required
def carrinho_venda():
    if current_user.tipo_usuario < 3:
        print("Acesso restrito a funcionários.", "danger")
        return redirect(url_for('vendaC.carrinho'))

    carrinho = obter_carrinho()
    produtos_no_carrinho = []
    produto_service = ProdutoDatabaseService()
    for produto_id, quantidade in carrinho.obter_itens().items():
        produto = produto_service.get_produto_por_id(int(produto_id))
        if produto:
            produtos_no_carrinho.append({'produto': produto, 'quantidade': quantidade})
    total = carrinho.calcular_total(produto_service)

    user_service = UserDatabaseService()
    clientes = user_service.listar_clientes()

    return render_template(
        'carrinho_venda.html',
        carrinho=produtos_no_carrinho,
        total=total,
        clientes=clientes
    )

@vendaC.route('/finalizar_venda')
@login_required
def finalizar_venda():
    if current_user.tipo_usuario >= 3:
        user_service = UserDatabaseService()
        clientes = user_service.listar_clientes()
        return render_template('identificar_cliente.html', clientes=clientes)
    else:
        return redirect(url_for('vendaC.processar_compra'))

@vendaC.route('/processar_compra', methods=['POST'])
@login_required
def processar_compra():
    if not session.get('codigo_validado'):
        print('Você precisa confirmar o código enviado ao email antes de finalizar a venda.', 'danger')
        return redirect(url_for('emailc.pedir_email'))

    carrinho = obter_carrinho()
    itens_carrinho = carrinho.obter_itens()

    if not itens_carrinho:
        print('Seu carrinho está vazio.', 'warning')
        return redirect(url_for('vendaC.carrinho'))

    processador = ProcessadorDeCompraDireta()

    usuario = None
    funcionario = None

    if current_user.tipo_usuario == 2:  # Cliente comprando
        usuario = current_user
    elif current_user.tipo_usuario >= 3:  # Funcionário vendendo
        cliente_id = request.form.get('cliente_id')
        if not cliente_id:
            print('Cliente não selecionado.', 'danger')
            return redirect(url_for('vendaC.carrinho_venda'))
        from ..model.Users.Cliente import Cliente
        usuario = Cliente.query.get(cliente_id)
        if not usuario:
            print('Cliente inválido.', 'danger')
            return redirect(url_for('vendaC.carrinho_venda'))
        funcionario = current_user
    else:
        print('Tipo de usuário inválido para realizar compras.', 'danger')
        return redirect(url_for('vendaC.carrinho'))

    teste, msg = processador.verificar_estoque(carrinho)
    print("Resultado do teste de estoque:", teste, "-", msg)

    if teste:
        sucesso, mensagem = processador.processar_compra(carrinho, usuario, funcionario)
        if sucesso:
            user_service = UserDatabaseService()
            user_service.cliente_fez_compra(usuario.id)
            if funcionario:
                user_service.funcionario_fez_venda(funcionario.id)
            session.pop('carrinho', None)
            session.pop('codigo_validado', None)    
            session.pop('codigo', None)
            session.pop('codigo_expiracao', None)
            print('Compra realizada com sucesso!', 'success')
            return redirect(url_for('vendaC.compra_realizada'))
        else:
            print(f'Ocorreu um erro ao finalizar a compra: {mensagem}', 'danger')
            return redirect(url_for('vendaC.carrinho'))
    else:
        print(f'Erro de estoque: {msg}', 'danger')
        return redirect(url_for('vendaC.carrinho'))

@vendaC.route('/compra_realizada')
@login_required
def compra_realizada():
    return render_template('compra_sucesso.html')