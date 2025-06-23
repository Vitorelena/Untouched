from ... import db

class Produto(db.Model):
    __tablename__ = 'produto'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50))
    descricao = db.Column(db.Text(150))
    preco = db.Column(db.Numeric(10, 2))
    codigo_de_barras = db.Column(db.String(50), unique=True)
    imagem_url = db.Column(db.String(200))
    categoria = db.Column(db.String(25))
    cor = db.Column(db.String(20), nullable=True)
    tipo = db.Column(db.String(50), nullable=True) 


    estoque = db.relationship('Estoque', uselist=False, back_populates='produto', cascade='all, delete-orphan')

    __mapper_args__ = {
        'polymorphic_on': categoria,
        'polymorphic_identity': '0'  
    }
    def __init__(self, nome, descricao, preco, codigo_de_barras, imagem_url, categoria, cor=None):
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.codigo_de_barras = codigo_de_barras
        self.imagem_url = imagem_url
        self.categoria = categoria
        self.cor = cor
    def gerar_relatorio(self):
        relatorio = f"Produto: {self.nome}\nPreço: R${self.preco}\n"
        return relatorio