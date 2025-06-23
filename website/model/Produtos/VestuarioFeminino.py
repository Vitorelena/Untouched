from website.model.Produtos.Produto import Produto
from ... import db

class VestuarioFeminino(Produto):
    __mapper_args__ = {
        'polymorphic_identity': '1'
    }

    tamanho_feminino = db.Column(db.String(5))
    tecido_feminino = db.Column(db.String(20))

    def __init__(self, nome, descricao, preco, codigo_de_barras, imagem_url, **kwargs):
        super().__init__(
            nome=nome, descricao=descricao, preco=preco, codigo_de_barras=codigo_de_barras,
            imagem_url=imagem_url, categoria='1', cor=kwargs.get('cor_vestuario')
        )
        self.tamanho_feminino = kwargs.get('tamanho_feminino')
        self.tecido_feminino = kwargs.get('tecido_feminino')

    def gerar_relatorio(self):
        base = super().gerar_relatorio()
        return f"{base}\nTamanho: {self.tamanho_feminino}\nCor: {self.cor}\nTecido: {self.tecido_feminino}"