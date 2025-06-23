from website.model.Produtos.Produto import Produto
from ... import db

class Calcados(Produto):
    __mapper_args__ = {
        'polymorphic_identity': '3'
    }

    numero = db.Column(db.String(5))
    material = db.Column(db.String(20))

    def __init__(self, nome, descricao, preco, codigo_de_barras, imagem_url, **kwargs):
        super().__init__(
            nome=nome, descricao=descricao, preco=preco, codigo_de_barras=codigo_de_barras,
            imagem_url=imagem_url, categoria='3', cor=kwargs.get('cor_calcado')
        )
        self.numero = kwargs.get('numero_calcado')
        self.material = kwargs.get('material_calcado')
        
    def gerar_relatorio(self):
        base = super().gerar_relatorio()
        # self.cor será acessado da classe Produto
        return f"{base}\nNúmero: {self.numero}\nCor: {self.cor}\nMaterial: {self.material}"