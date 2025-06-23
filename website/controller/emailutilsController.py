from datetime import datetime
from ..model.Vendas.Venda import Venda
from ..model.Vendas.ItemVendido import ItemVendido
from ..service.ProdutoDatabaseService import ProdutoDatabaseService

def gerar_resumo_venda_email_html(venda):
    itens = venda.itens_vendidos
    texto = f"Resumo da sua compra\n"
    texto += f"Data: {venda.data_venda.strftime('%d/%m/%Y %H:%M')}\n\n"
    texto += "Itens:\n"
    for item in itens:
        produto_nome = item.produto.nome if item.produto else "Produto desconhecido"
        subtotal = item.quantidade * item.preco_unitario
        texto += f"- {produto_nome} | Qtde: {item.quantidade} | Unit: R$ {item.preco_unitario:.2f} | Subtotal: R$ {subtotal:.2f}\n"
    total = sum(item.quantidade * item.preco_unitario for item in itens)
    texto += f"\nTotal da compra: R$ {total:.2f}\n"

    html = f"""
    <html>
    <body>        
        <h2>Resumo da sua compra</h2>
        <p>Data: {venda.data_venda.strftime('%d/%m/%Y')}</p>
        <p>Obrigada por comprar na Untouched, você só cresce se comprar conosco!</p>        
        <table border="1" cellpadding="5" cellspacing="0">
            <thead>
                <tr><th>Produto</th><th>Quantidade</th><th>Preço Unit.</th><th>Subtotal</th></tr>
            </thead>
            <tbody>
    """
    for item in itens:
        produto_nome = item.produto.nome if item.produto else "Produto desconhecido"
        subtotal = item.quantidade * item.preco_unitario
        html += f"<tr><td>{produto_nome}</td><td>{item.quantidade}</td><td>R$ {item.preco_unitario:.2f}</td><td>R$ {subtotal:.2f}</td></tr>"
    html += f"""
            </tbody>
        </table>
        <p><strong>Total: R$ {total:.2f}</strong></p>
        <p>Em breve nós liberaremos o segredo dos monstros, are you ready?</p>
    </body>
    </html>
    """
    print(texto)
    return texto, html



def criar_venda_temporaria_para_email(dados_venda):
    venda = Venda(
        data_venda=datetime.utcnow(),
        cliente_id=dados_venda.get('cliente_id'),
        funcionario_id=dados_venda.get('funcionario_id')
    )
    venda.id = 0  # ID fictício apenas para exibição

    venda.itens_vendidos = []
    produto_service = ProdutoDatabaseService()

    for produto_id, quantidade in dados_venda['itens'].items():
        produto = produto_service.get_produto_por_id(int(produto_id))
        if produto:
            item = ItemVendido(
    produto_id=produto.id,
    quantidade=quantidade,
    preco_unitario=produto.preco,
    venda_id=0
)
            item.produto = produto  # Necessário para gerar o nome no email
            venda.itens_vendidos.append(item)

    return venda