from .ProcessadorDeCompra import ProcessadorDeCompra
from .CarrinhoDeCompras import CarrinhoDeCompras
from ...service.EstoqueDatabaseService import EstoqueDatabaseService
from ...service.ProdutoDatabaseService import ProdutoDatabaseService
from .Venda import Venda
from ..Vendas.ItemVendido import ItemVendido
from datetime import datetime
from ... import db
from flask_login import current_user

class ProcessadorDeCompraDireta(ProcessadorDeCompra):
    def verificar_estoque(self, carrinho: CarrinhoDeCompras) -> tuple[bool, str]:
        for produto_id, quantidade in carrinho.obter_itens().items():
            estoque = EstoqueDatabaseService.get_estoque_por_produto_id(produto_id)
            if not estoque:
                return False, f"Produto {produto_id} não possui registro de estoque."
            if estoque.quantidade < quantidade:
                return False, f"Produto {produto_id} com estoque insuficiente: {estoque.quantidade} disponível, {quantidade} solicitado."
        return True, "Estoque verificado com sucesso."
    
    def atualizar_estoque(self, carrinho: CarrinhoDeCompras) -> bool:
        for produto_id, quantidade in carrinho.obter_itens().items():
            sucesso, mensagem = EstoqueDatabaseService.subtrair_do_estoque(produto_id, quantidade)
            if not sucesso:
                print(f"Erro ao subtrair estoque do produto {produto_id}: {mensagem}")
                return False
        return True

    def registrar_venda(self, carrinho: CarrinhoDeCompras, usuario=None, funcionario=None):
        try:
            # Cria a venda com os IDs de cliente e funcionário (se houver)
            venda = Venda(
                data_venda=datetime.utcnow(),
                cliente_id= usuario.id if usuario else None,
                funcionario_id=funcionario.id if funcionario else None
            )
            db.session.add(venda)
            db.session.flush()  # Garante que venda.id está disponível

            # Para cada item no carrinho, adiciona o item vendido e atualiza estoque
            for produto_id, quantidade in carrinho.obter_itens().items():
                produto = ProdutoDatabaseService.get_produto_por_id(produto_id)
                if not produto:
                    # Produto não existe, aborta registro da venda
                    raise ValueError(f"Produto com id {produto_id} não encontrado.")

                # Cria registro do item vendido
                item_vendido = ItemVendido(
                    venda_id=venda.id,
                    produto_id=produto.id,
                    quantidade=quantidade,
                    preco_unitario=produto.preco
                )
                db.session.add(item_vendido)

                # Atualiza estoque do produto
                if produto.estoque.quantidade < quantidade:
                    raise ValueError(f"Estoque insuficiente para o produto {produto.id}")
                
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao registrar a venda: {e}")
            return False, str(e)

    
    def processar_compra(self, carrinho: CarrinhoDeCompras, usuario=None, funcionario=None):
        if self.verificar_estoque(carrinho):
            if self.atualizar_estoque(carrinho):
                if self.registrar_venda(carrinho, usuario, funcionario):
                    carrinho.esvaziar()
                    return True, None
                else:
                    return False, "Erro ao registrar a venda."
            else:
                return False, "Erro ao atualizar o estoque."
        else:
            return False, "Estoque insuficiente para um ou mais itens."