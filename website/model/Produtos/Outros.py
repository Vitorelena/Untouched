from website.model.Produtos.Produto import Produto
from ... import db

class Equipamentos(Produto):
    __mapper_args__ = {
        'polymorphic_identity': '4'
    }

    tipo_equipamento = db.Column(db.String(50))
    marca = db.Column(db.String(30))

    def __init__(self, nome, descricao, preco, codigo_de_barras, imagem_url, **kwargs):
        super().__init__(
            nome=nome, descricao=descricao, preco=preco, codigo_de_barras=codigo_de_barras,
            imagem_url=imagem_url, categoria='4'
        )
        self.tipo_equipamento = kwargs.get('tipo_equipamento')
        self.marca = kwargs.get('marca_equipamento')

    def gerar_relatorio(self):
        base = super().gerar_relatorio()
        # Use o atributo com o nome da coluna específica
        return f"{base}\nTipo: {self.tipo_equipamento}\nMarca: {self.marca}"