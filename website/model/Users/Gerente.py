from ... import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from .Funcionario import Funcionario

class Gerente(Funcionario):
    __mapper_args__ = {
        'polymorphic_identity': 6
    }

    def __init__(self, nome, cpf, login, senha, matricula, numero_vendas=0):
        super().__init__(nome, cpf, login, senha, matricula, nivel=3, numero_vendas=numero_vendas)
        self.tipo_usuario = 6

    def __repr__(self):
        return f"<Gerente id={self.id}, nome='{self.nome}', cpf='{self.cpf}', matricula='{self.matricula}', numero de vendas = {self.numero_vendas}, nivel {self.nivel}>"

    def gerar_relatorio(self):
        relatorio = super().gerar_relatorio()
        relatorio += "\n--- Relatório do Gerente ---\nCargo: Gerente"
        return relatorio