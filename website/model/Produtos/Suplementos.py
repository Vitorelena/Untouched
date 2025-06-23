from website.model.Produtos.Produto import Produto
from ... import db

class Suplementos(Produto):
    __mapper_args__ = {
        'polymorphic_identity': '5'
    }

    peso = db.Column(db.String(10))
    sabor = db.Column(db.String(30))
    tipo_suplemento = db.Column(db.String(20))

    def __init__(self, nome, descricao, preco, codigo_de_barras, imagem_url, **kwargs):
        super().__init__(
            nome=nome, descricao=descricao, preco=preco, codigo_de_barras=codigo_de_barras,
            imagem_url=imagem_url, categoria='5'
        )
        self.peso = kwargs.get('peso_suplemento')
        self.sabor = kwargs.get('sabor_suplemento')
        self.tipo_suplemento = kwargs.get('tipo_suplemento')

    def gerar_relatorio(self):
        base = super().gerar_relatorio()
        return f"{base}\nTipo: {self.tipo_suplemento}\nSabor: {self.sabor}\nQuantidade: {self.peso}"