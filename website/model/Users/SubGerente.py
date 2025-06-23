from ... import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from .Funcionario import Funcionario


class SubGerente(Funcionario):
    __mapper_args__ = {
        'polymorphic_identity': 5
    }

    def __init__(self, nome, cpf, login, senha, matricula, numero_vendas=0):
        super().__init__(nome, cpf, login, senha, matricula, nivel=2, numero_vendas=numero_vendas)
        self.tipo_usuario = 5

    def __repr__(self):
        return f"<SubGerente id={self.id}, nome='{self.nome}', cpf='{self.cpf}', matricula='{self.matricula}', numero de vendas = {self.numero_vendas}>"

    def gerar_relatorio(self):
        relatorio = super().gerar_relatorio()
        relatorio += "\n--- Relatório do SubGerente ---\nCargo: SubGerente"
        return relatorio