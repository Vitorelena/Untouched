from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_required, current_user
from .vendaController import obter_carrinho
import random
import string
from website import mail
from flask_mail import Message
from datetime import datetime, timedelta
from ..model.Vendas.Venda import Venda
from website.model.Vendas.ProcessadorDeCompraDireta import ProcessadorDeCompraDireta
from website.model.Vendas.CarrinhoDeCompras import CarrinhoDeCompras
from website import db
from ..controller.emailutilsController import gerar_resumo_venda_email_html, criar_venda_temporaria_para_email
from ..service.UserDatabaseService import UserDatabaseService
from ..service.ProdutoDatabaseService import ProdutoDatabaseService
from ..model.Vendas.ItemVendido import ItemVendido

emailc = Blueprint('emailc', __name__)

def gerar_codigo(tam=6):
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choices(caracteres, k=tam))

def enviar_codigo(email_dest, codigo):
    try:
        msg = Message(
            subject="Código de Confirmação da Compra",
            recipients=[email_dest],
            body=f"Seu código de confirmação é: {codigo}"
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False

@emailc.route('/enviar_codigo', methods=['POST'])
def enviar_codigo_route():
    email = request.form.get('email')
    if not email:
        print('Email não fornecido.', 'warning')
        return redirect(url_for('vendaC.finalizar_venda'))

    codigo = gerar_codigo()
    session['codigo_confirmacao'] = codigo
    session['email_confirmacao'] = email

    sucesso = enviar_codigo(email, codigo)
    if sucesso:
        print('Código enviado para seu email.', 'info')
        return redirect(url_for('emailc.validar_codigo'))
    else:
        print('Erro ao enviar o código, tente novamente.', 'danger')
        return redirect(url_for('vendaC.finalizar_venda'))

@emailc.route('/pedir_email', methods=['GET', 'POST'])
@login_required
def pedir_email():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            print('Informe um email válido.', 'warning')
            return render_template('pedir_email.html')

        # Determinar cliente_id e funcionario_id seguindo a regra:
        cliente_id = None
        funcionario_id = None

        if current_user.tipo_usuario == 2:
            cliente_id = current_user.id
        elif current_user.tipo_usuario >= 3:
            cliente_id = request.form.get('cliente_id')  # Você precisa garantir que esse campo esteja no formulário!
            funcionario_id = current_user.id

        carrinho = obter_carrinho()
        itens_carrinho = carrinho.obter_itens()
        if not itens_carrinho:
            print('Seu carrinho está vazio.', 'warning')
            return redirect(url_for('vendaC.carrinho'))

        session['email_confirmacao'] = email
        # Salvar os dados da venda pendente na sessão
        session['venda_pendente'] = {
            'cliente_id': cliente_id,
            'funcionario_id': funcionario_id,
            'itens': itens_carrinho,
            'email': email
        }
        session['cliente_id'] = cliente_id
        codigo = gerar_codigo()
        sucesso = enviar_codigo(email, codigo)
        if not sucesso:
            print('Erro ao enviar email. Tente novamente.', 'danger')
            return render_template('pedir_email.html')

        session['codigo_confirmacao'] = codigo
        session['codigo_expira_em'] = (datetime.utcnow() + timedelta(minutes=20)).isoformat()

        print('Código enviado para seu email.', 'info')
        return redirect(url_for('emailc.validar_codigo'))

    # GET
    user_service = UserDatabaseService()
    clientes = None
    if current_user.tipo_usuario >= 3:
        clientes = user_service.listar_clientes()
    return render_template('pedir_email.html', clientes=clientes)



@emailc.route('/validar_codigo', methods=['GET','POST'])
@login_required
def validar_codigo():
    if request.method == 'POST':
        codigo_digitado = request.form.get('codigo')
        codigo_armazenado = session.get('codigo_confirmacao')
        expira_em_str = session.get('codigo_expira_em')

        # Verifica expiração do código
        if expira_em_str:
            expira_em = datetime.fromisoformat(expira_em_str)
            if datetime.utcnow() > expira_em:
                session.pop('codigo_confirmacao', None)
                session.pop('codigo_expira_em', None)
                print('Código expirado. Solicite um novo.', 'warning')
                return redirect(url_for('emailc.pedir_email'))

        # Valida o código
        if codigo_digitado and codigo_armazenado and codigo_digitado.upper() == codigo_armazenado:
            dados_venda = session.get('venda_pendente')
            if not dados_venda:
                print('Dados da venda não encontrados. Por favor, refaça o processo.', 'danger')
                return redirect(url_for('vendaC.carrinho'))

            # Verifica o estoque antes de continuar
            carrinho_ficticio = CarrinhoDeCompras()
            carrinho_ficticio.itens = dados_venda['itens']
            processador = ProcessadorDeCompraDireta()

            estoque_ok, mensagem_estoque = processador.verificar_estoque(carrinho_ficticio)
            if not estoque_ok:
                print(f"Erro de estoque: {mensagem_estoque}", 'danger')
                return redirect(url_for('vendaC.carrinho'))

            # Cria objeto Venda temporário para gerar o email
            venda_temp = criar_venda_temporaria_para_email(dados_venda)

            session['codigo_validado'] = True

            if dados_venda.get('email'):
                try:
                    corpo_texto, corpo_html = gerar_resumo_venda_email_html(venda_temp)
                    msg = Message(
                        subject="RESUMO DA SUA COMPRA",
                        recipients=[dados_venda['email']],
                        body=corpo_texto,
                        html=corpo_html
                    )
                    mail.send(msg)
                    print('Resumo da compra enviado por e-mail.', 'success')
                except Exception as e:
                    print(f"Erro ao enviar e-mail: {e}", 'warning')

            cliente_id = session.get('venda_pendente', {}).get('cliente_id')
            return render_template('confirmar_compra.html', cliente_id=cliente_id)

        else:
            print('Código inválido. Tente novamente.', 'danger')

    return render_template('validar_codigo.html')