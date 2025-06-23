from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from .User import User
from ..Vendas.Venda import Venda

class Funcionario(User):
    __mapper_args__ = {
        'polymorphic_identity': 3
    }

    matricula = db.Column(db.String(20))
    nivel = db.Column(db.Integer)
    numero_vendas = db.Column(db.Integer)
    vendas = db.relationship('Venda', backref='funcionario', foreign_keys=[Venda.__table__.c.funcionario_id])

    def __init__(self, nome, cpf, login, senha, matricula, nivel=1, numero_vendas=0):
        super().__init__(nome, cpf, login, senha)
        self.tipo_usuario = 3
        self.matricula = matricula
        self.nivel = nivel
        self.numero_vendas = numero_vendas

    def __repr__(self):
        return f"<Funcionario id={self.id}, nome='{self.nome}', cpf='{self.cpf}', matricula='{self.matricula}', numero de vendas = {self.numero_vendas}>"

    def gerar_relatorio(self):
        relatorio = super().gerar_relatorio()
        relatorio += "\n--- Sessão do Funcionário ---\n"
        relatorio += f"Matrícula: {self.matricula}\n"
        relatorio += f"Numero de vendas: {self.numero_vendas}\n"
        return relatorio