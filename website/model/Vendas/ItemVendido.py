from website import db
from website.model.Produtos.Produto import Produto

class ItemVendido(db.Model):
    __tablename__ = 'item_vendido'
    id = db.Column(db.Integer, primary_key = True)
    venda_id = db.Column(db.Integer, db.ForeignKey('venda.id'))
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'))
    quantidade = db.Column(db.Integer)
    preco_unitario = db.Column(db.Float)
    venda = db.relationship('Venda', back_populates='itens_vendidos', overlaps="itens,itens_vendidos")
    produto =   db.relationship('Produto')
    
    def __init__(self, venda_id, produto_id, quantidade, preco_unitario):
        self.venda_id = venda_id
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario