# Em service/ProdutoDatabaseService.py

from .. import db
from ..model.Produtos.Produto import Produto
from ..model.Estoque import Estoque 

# Importe TODAS as suas subclasses de Produto
from ..model.Produtos.VestuarioFeminino import VestuarioFeminino
from ..model.Produtos.VestuarioMasculino import VestuarioMasculino
from ..model.Produtos.Calcados import Calcados
from ..model.Produtos.Suplementos import Suplementos
from ..model.Produtos.Equipamentos import Equipamentos
from ..model.Produtos.Outros import Outros


class ProdutoDatabaseService:

    @staticmethod
    def criar_produto(nome, descricao, preco, codigo_de_barras, imagem_url, tipo, **kwargs):
        tipo_para_classe = {
            'vestuario_feminino': VestuarioFeminino,
            'vestuario_masculino': VestuarioMasculino,
            'calcados': Calcados,
            'suplementos': Suplementos,
            'equipamentos': Equipamentos,
            'outros': Outros
        }

        ClasseProduto = tipo_para_classe.get(tipo)
        if not ClasseProduto:
            raise ValueError(f"Tipo de produto inválido: {tipo}")

        args_comuns = {
            'nome': nome,
            'descricao': descricao,
            'preco': preco,
            'codigo_de_barras': codigo_de_barras,
            'imagem_url': imagem_url,
            # NÃO PASSAR categoria aqui
        }

        todos_args = {**args_comuns, **kwargs}

        produto = ClasseProduto(**todos_args)  # categoria é definido no __init__ da subclasse

        db.session.add(produto)
        db.session.commit()

        return produto

    
    @staticmethod
    def atualizar_produto(produto_id,
                      nome=None, descricao=None, preco=None, codigo_de_barras=None,
                      imagem_url=None, categoria=None,
                      tamanho_feminino=None, tecido_feminino=None, cor_vestuario=None,
                      tamanho_masculino=None, tecido_masculino=None,
                      numero_calcado=None, material_calcado=None, cor_calcado=None,
                      tipo_equipamento=None, marca_equipamento=None,
                      peso_suplemento=None, sabor_suplemento=None, tipo_suplemento=None,
                      detalhes_outros=None):
    
        produto = Produto.query.get(produto_id)
        if not produto:
            return False

        # Atualiza atributos da classe base
        if nome is not None:
            produto.nome = nome
        if descricao is not None:
            produto.descricao = descricao
        if preco is not None:
            produto.preco = preco
        if codigo_de_barras is not None:
            produto.codigo_de_barras = codigo_de_barras
        if imagem_url is not None:
            produto.imagem_url = imagem_url
        if categoria is not None:
            produto.categoria = categoria

        # Atualiza cor
        if cor_vestuario is not None:
            produto.cor = cor_vestuario
        elif cor_calcado is not None:
            produto.cor = cor_calcado

        # Atualiza atributos específicos
        if isinstance(produto, VestuarioFeminino):
            if tamanho_feminino is not None:
                produto.tamanho_feminino = tamanho_feminino
            if tecido_feminino is not None:
                produto.tecido_feminino = tecido_feminino

        elif isinstance(produto, VestuarioMasculino):
            if tamanho_masculino is not None:
                produto.tamanho_masculino = tamanho_masculino
            if tecido_masculino is not None:
                produto.tecido_masculino = tecido_masculino

        elif isinstance(produto, Calcados):
            if numero_calcado is not None:
                produto.numero = numero_calcado
            if material_calcado is not None:
                produto.material = material_calcado

        elif isinstance(produto, Equipamentos):
            if tipo_equipamento is not None:
                produto.tipo_equipamento = tipo_equipamento
            if marca_equipamento is not None:
                produto.marca = marca_equipamento

        elif isinstance(produto, Suplementos):
            if peso_suplemento is not None:
                produto.peso = peso_suplemento
            if sabor_suplemento is not None:
                produto.sabor = sabor_suplemento
            if tipo_suplemento is not None:
                produto.tipo_suplemento = tipo_suplemento

        elif isinstance(produto, Outros):
            if detalhes_outros is not None:
                produto.detalhes = detalhes_outros

        db.session.commit()
        return True
    @staticmethod
    def excluir_produto(produto_id):
        produto = Produto.query.get(produto_id)
        if produto:
            db.session.delete(produto)
            db.session.commit() 
            return True
        return False
    
        
    @staticmethod
    def get_produto_por_id(produto_id):
        return Produto.query.get(produto_id)

    @staticmethod
    def get_produto_por_codigo_barras(codigo_de_barras):
        return Produto.query.filter_by(codigo_de_barras=codigo_de_barras).first()

    @staticmethod
    def get_todos_produtos():
        return Produto.query.all()
    
    @staticmethod
    def get_produtos_por_categoria(categoria):
        return Produto.query.filter_by(categoria = categoria).all()

    @staticmethod
    def get_nome_por_id(produto_id):
        produto = Produto.query.get(produto_id)
        if produto:
            return produto.nome
        return None