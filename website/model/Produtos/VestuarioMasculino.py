from website.model.Produtos.Produto import Produto
from ... import db

class VestuarioMasculino(Produto):
    __mapper_args__ = {
        'polymorphic_identity': '2'
    }

    tamanho_masculino = db.Column(db.String(5))
    tecido_masculino = db.Column(db.String(20))

    def __init__(self, nome, descricao, preco, codigo_de_barras, imagem_url, **kwargs):
        super().__init__(
            nome=nome, descricao=descricao, preco=preco, codigo_de_barras=codigo_de_barras,
            imagem_url=imagem_url, categoria='2', cor=kwargs.get('cor_vestuario')
        )
        self.tamanho_masculino = kwargs.get('tamanho_masculino')
        self.tecido_masculino = kwargs.get('tecido_masculino')
            
    def gerar_relatorio(self):
        base = super().gerar_relatorio()
        # Usando self.tamanho e self.tecido, que são as colunas específicas desta classe
        return f"{base}\nTamanho: {self.tamanho}\nCor: {self.cor}\nTecido: {self.tecido}"