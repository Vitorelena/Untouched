from website.model.Produtos.Produto import Produto
from ... import db

class Outros(Produto):
    __mapper_args__ = {
        'polymorphic_identity': '6'
    }

    detalhes = db.Column(db.String(100))

    def __init__(self, nome, descricao, preco, codigo_de_barras, imagem_url, **kwargs):
        super().__init__(
            nome=nome, descricao=descricao, preco=preco, codigo_de_barras=codigo_de_barras,
            imagem_url=imagem_url, categoria='6'
        )
        self.detalhes = kwargs.get('detalhes_outros')

    def gerar_relatorio(self):
        base = super().gerar_relatorio()
        return f"{base}\nDetalhes: {self.detalhes}"