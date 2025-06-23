from flask import Blueprint, render_template, request, redirect, url_for
from website import db
from ..service.ProdutoDatabaseService import ProdutoDatabaseService
from ..service.EstoqueDatabaseService import EstoqueDatabaseService
from ..model.Produtos.VestuarioFeminino import VestuarioFeminino
from ..model.Produtos.VestuarioMasculino import VestuarioMasculino
from ..model.Produtos.Calcados import Calcados
from ..model.Produtos.Suplementos import Suplementos
from ..model.Produtos.Equipamentos import Equipamentos
from ..model.Produtos.Outros import Outros
from flask_login import current_user, login_required

productC = Blueprint('productC', __name__)

@productC.route('/criar_produto', methods=['GET', 'POST'])
@login_required
def criar_produto():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        preco = float(request.form.get('preco'))
        codigo_de_barras = request.form.get('codigo_de_barras')
        imagem_url = request.form.get('imagem_url')
        categoria_id = request.form.get('categoria')

        categoria_para_tipo = {
            "1": "vestuario_feminino",
            "2": "vestuario_masculino",
            "3": "calcados",
            "4": "equipamentos",
            "5": "suplementos",
            "6": "outros"
        }

        tipo = categoria_para_tipo.get(str(categoria_id))
        if not tipo:
            print("Categoria inválida.", "danger")
            return render_template('criar_produto.html')

        specific_attrs = {
            'tamanho_feminino': request.form.get('tamanho_feminino'),
            'cor_vestuario': request.form.get('cor_vestuario'),
            'tecido_feminino': request.form.get('tecido_feminino'),
            'tamanho_masculino': request.form.get('tamanho_masculino'),
            'tecido_masculino': request.form.get('tecido_masculino'),
            'numero_calcado': request.form.get('numero_calcado'),
            'cor_calcado': request.form.get('cor_calcado'),
            'material_calcado': request.form.get('material_calcado'),
            'tipo_equipamento': request.form.get('tipo_equipamento'),
            'marca_equipamento': request.form.get('marca_equipamento'),
            'peso_suplemento': request.form.get('peso_suplemento'),
            'sabor_suplemento': request.form.get('sabor_suplemento'),
            'tipo_suplemento': request.form.get('tipo_suplemento'),
            'detalhes_outros': request.form.get('detalhes_outros')
        }
        specific_attrs = {k: v for k, v in specific_attrs.items() if v not in (None, '')}

        try:
            novo_produto = ProdutoDatabaseService.criar_produto(
                nome=nome,
                descricao=descricao,
                preco=preco,
                codigo_de_barras=codigo_de_barras,
                imagem_url=imagem_url,
                tipo=tipo,  # removeu categoria daqui
                **specific_attrs
            )
            print("Produto criado com sucesso!", "success")
            return redirect(url_for('productC.criar_estoque', produto_id=novo_produto.id))
        except Exception as e:
            print(f"Ocorreu um erro ao criar produto: {e}", "danger")
            print(f"Erro ao criar produto: {e}")
            return render_template('criar_produto.html')

    return render_template('criar_produto.html')


@productC.route('/editar_produto/<int:produto_id>', methods=['GET', 'POST'])
@login_required
def editar_produto(produto_id):
    if not (current_user.is_authenticated and current_user.nivel >= 2):
        print("Você não tem permissão para editar produtos.", 'danger')
        return redirect(url_for('homeC.home'))

    produto = ProdutoDatabaseService.get_produto_por_id(produto_id)
    if not produto:
        print("Produto não encontrado.", 'danger')
        return redirect(url_for('productC.gerenciar_produtos'))

    if request.method == 'POST':
        # Campos comuns para todos os produtos
        common_attrs = {
            'nome': request.form.get('nome'),
            'descricao': request.form.get('descricao'),
            'preco': request.form.get('preco'),
            'codigo_de_barras': request.form.get('codigo_de_barras'),
            'imagem_url': request.form.get('imagem_url')
        }

        # Campos específicos conforme o tipo de produto
        specific_attrs = {}

        if isinstance(produto, VestuarioFeminino):
            specific_attrs = {
                'tamanho_feminino': request.form.get('tamanho_vestuario'),
                'tecido_feminino': request.form.get('tecido_vestuario'),
                'cor_vestuario': request.form.get('cor_vestuario')
            }
        elif isinstance(produto, VestuarioMasculino):
            specific_attrs = {
                'tamanho_masculino': request.form.get('tamanho_vestuario'),
                'tecido_masculino': request.form.get('tecido_vestuario'),
                'cor_vestuario': request.form.get('cor_vestuario')
            }
        elif isinstance(produto, Calcados):
            specific_attrs = {
                'numero_calcado': request.form.get('numero_calcado'),
                'material_calcado': request.form.get('material_calcado'),
                'cor_calcado': request.form.get('cor_calcado')
            }
        elif isinstance(produto, Equipamentos):
            specific_attrs = {
                'tipo_equipamento': request.form.get('tipo_equipamento'),
                'marca_equipamento': request.form.get('marca_equipamento')
            }
        elif isinstance(produto, Suplementos):
            specific_attrs = {
                'peso_suplemento': request.form.get('peso_suplemento'),
                'sabor_suplemento': request.form.get('sabor_suplemento'),
                'tipo_suplemento': request.form.get('tipo_suplemento')
            }
        elif isinstance(produto, Outros):
            specific_attrs = {
                'detalhes_outros': request.form.get('detalhes_outros')
            }

        # Combina todos os atributos e remove os que estão vazios
        all_attrs = {**common_attrs, **specific_attrs}
        all_attrs = {k: v for k, v in all_attrs.items() if v not in (None, '')}

        success = ProdutoDatabaseService.atualizar_produto(produto_id=produto.id, **all_attrs)

        if success:
            print(f"Produto '{produto.nome}' atualizado com sucesso!", 'success')
            return redirect(url_for('productC.gerenciar_produtos'))
        else:
            print("Erro ao atualizar o produto.", 'danger')

    return render_template('editar_produto.html', produto=produto)
@productC.route('/criar_estoque/<int:produto_id>', methods=['GET', 'POST'])
def criar_estoque(produto_id):
    produto = ProdutoDatabaseService.get_produto_por_id(produto_id)
    if not produto:
        return "Produto não encontrado.", 404

    if request.method == 'POST':
        quantidade = int(request.form.get('quantidade'))
        valor_total = produto.preco * quantidade

        estoque_criado = EstoqueDatabaseService.criar_estoque(
            produto_id=produto_id,
            quantidade=quantidade,
            valor_total=valor_total
        )

        if estoque_criado is True:
            return redirect(url_for('homeC.home'))
        else:
            # Trate o erro na criação do estoque (estoque já existe ou outro erro)
            pass

    return render_template('criar_estoque.html', produto_id=produto_id)
@productC.route('/visualizar_estoque', methods=['GET'])
@login_required # Garante que apenas usuários logados possam acessar
def visualizar_estoque():
    show_valor_total = False # Flag para controlar a visibilidade do valor total (default é False)

    # Lógica de permissão e determinação de show_valor_total
    if current_user.is_authenticated:
        # Se for um funcionário (tipo_usuario >= 3)
        if current_user.tipo_usuario >= 3:
            # Gerente/CEO (nivel >= 3) - pode ver o total geral e por item
            if current_user.nivel >= 3: 
                show_valor_total = True
            # SubGerente/Staff (nivel >= 1 e < 3) - pode ver estoque, mas SEM valores totais
            elif current_user.nivel >= 1: 
                show_valor_total = False
            # Caso de funcionário com tipo >=3 mas sem nível ou nível inválido (não deveria acontecer)
            else:
                print("Você não tem permissão para visualizar o estoque.", 'danger')
                return redirect(url_for('homeC.home'))
        # Cliente (tipo_usuario == 2) - pode ver estoque, mas SEM valores totais
        elif current_user.tipo_usuario == 2:
            show_valor_total = False
        # Outros tipos de usuário não previstos ou sem permissão (barra acesso)
        else:
            print("Você não tem permissão para visualizar o estoque.", 'danger')
            return redirect(url_for('homeC.home'))
    else:
        # Este 'else' é tecnicamente redundante devido ao '@login_required',
        # mas serve como um fallback claro em caso de desautenticação inesperada.
        print("Você precisa estar logado para visualizar o estoque.", 'danger')
        return redirect(url_for('loginC.login_page'))

    # Coleta os dados do estoque após as verificações de permissão
    itens_estoque = EstoqueDatabaseService.get_todos_itens_estoque()
    valor_total_geral = EstoqueDatabaseService.get_valor_total_estoque()

    # Renderiza o template, PASSANDO A FLAG show_valor_total
    return render_template(
        'estoquecompleto.html', # <--- Certifique-se que o nome do seu template HTML está correto aqui
        itens_estoque=itens_estoque,
        valor_total_geral=valor_total_geral,
        show_valor_total=show_valor_total # AGORA A VARIÁVEL ESTÁ SENDO PASSADA CORRETAMENTE!
    )
@productC.route('/gerenciar_estoque', methods=['GET', 'POST'])
@login_required
def gerenciar_estoque():
    # Verificação de nível de acesso
    if not (current_user.is_authenticated and current_user.nivel >= 3):
        print("Você não tem permissão para gerenciar o estoque.", 'danger')
        return redirect(url_for('homeC.home')) # Redireciona para a home se não tiver permissão

    todos_produtos = ProdutoDatabaseService.get_todos_produtos()
    
    # Lógica para processar as ações de gerenciamento de estoque
    if request.method == 'POST':
        action = request.form.get('action')
        produto_id = request.form.get('produto_id')
        quantidade = request.form.get('quantidade')
        
        # Converte para os tipos corretos
        try:
            produto_id = int(produto_id)
            quantidade = int(quantidade)
        except (ValueError, TypeError):
            print("ID do produto ou quantidade inválidos.", 'danger')
            return redirect(url_for('productC.gerenciar_estoque'))

        if action == 'adicionar_quantidade':
            success, message, new_quantity = EstoqueDatabaseService.adicionar_ao_estoque(produto_id, quantidade)
            if success:
                print(f"Estoque do produto ID {produto_id} atualizado. Nova quantidade: {new_quantity}", 'success')
            else:
                print(f"Erro ao adicionar estoque: {message}", 'danger')
        elif action == 'subtrair_quantidade':
            success, message = EstoqueDatabaseService.subtrair_do_estoque(produto_id, quantidade)
            if success:
                print(f"Estoque do produto ID {produto_id} subtraído com sucesso.", 'success')
            else:
                print(f"Erro ao subtrair estoque: {message}", 'danger')
        elif action == 'excluir_estoque':
            success = EstoqueDatabaseService.excluir_estoque_do_produto(produto_id)
            if success:
                print(f"Estoque do produto ID {produto_id} excluído com sucesso.", 'success')
            else:
                print(f"Erro ao excluir estoque.", 'danger')
        # Adicione outras ações de gerenciamento aqui (editar, etc.)

        return redirect(url_for('productC.gerenciar_estoque')) # Redireciona para atualizar a lista

    return render_template(
        'gerenciar_estoque.html',
        todos_produtos=todos_produtos # Passa todos os produtos para a tabela de gerenciamento
    )
@productC.route('/gerenciar_produtos', methods=['GET', 'POST'])
@login_required
def gerenciar_produtos():
    # Verificação de nível de acesso (o mesmo do estoque, Gerente ou superior)
    if not (current_user.is_authenticated and current_user.nivel >= 2):
        print("Você não tem permissão para gerenciar produtos.", 'danger')
        return redirect(url_for('homeC.home'))

    # Para GET: Exibe a lista de produtos
    if request.method == 'GET':
        todos_produtos = ProdutoDatabaseService.get_todos_produtos()
        return render_template('gerenciar_produtos.html', todos_produtos=todos_produtos)

    # Para POST: Processa as ações de gerenciamento de produtos
    if request.method == 'POST':
        action = request.form.get('action')
        produto_id = request.form.get('produto_id')

        try:
            produto_id = int(produto_id)
        except (ValueError, TypeError):
            print("ID do produto inválido.", 'danger')
            return redirect(url_for('productC.gerenciar_produtos'))

        if action == 'excluir_produto':
            success = ProdutoDatabaseService.excluir_produto(produto_id)
            if success:
                print(f"Produto ID {produto_id} excluído com sucesso.", 'success')
            else:
                print(f"Erro ao excluir produto ID {produto_id}.", 'danger')
        # Adicione aqui outras ações POST como 'ativar/desativar', etc.

        return redirect(url_for('productC.gerenciar_produtos')) # Redireciona para atualizar a lista
 