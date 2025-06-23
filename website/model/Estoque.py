from .. import db

class Estoque(db.Model):
    __tablename__ = 'estoque'  # Nome da tabela

    id = db.Column(db.Integer, primary_key=True)  # ID do Estoque
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id', ondelete='CASCADE'), unique=True, nullable=False)  # Chave estrangeira para Produto
    produto = db.relationship('Produto', back_populates='estoque')
    quantidade = db.Column(db.Integer, nullable=False, default=0)  # Quantidade de produto no estoque
    valor_total = db.Column(db.Numeric(12, 2), default=0.00)  # Valor total do estoque

    def __init__(self, produto_id, quantidade=0, valor_total=0.00):
            self.produto_id = produto_id
            self.quantidade = quantidade
            self.valor_total = valor_total