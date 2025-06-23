from .. import db
from ..model.Estoque import Estoque
from ..model.Produtos.Produto import Produto

class EstoqueDatabaseService:

    @staticmethod
    @staticmethod
    def criar_estoque(produto_id, quantidade, valor_total):
        estoque_existente = Estoque.query.filter_by(produto_id=produto_id).first()
        if not estoque_existente:
            novo_estoque = Estoque(
                produto_id=produto_id,
                quantidade=quantidade,
                valor_total=valor_total
            )
            db.session.add(novo_estoque)
            db.session.commit()
            return True
        else:
            return False, "Estoque já existe para este produto."
            
    @staticmethod
    def adicionar_ao_estoque(produto_id, quantidade):
        estoque = Estoque.query.filter_by(produto_id=produto_id).first()
        if not estoque:
            return False, "Estoque não encontrado para este produto."
        if quantidade > 0:
            estoque.quantidade += quantidade
            estoque.valor_total += estoque.produto.preco * quantidade
            db.session.commit()
            EstoqueDatabaseService.atualizar_valor_total_estoque(produto_id)
            return True, None, estoque.quantidade
        else:
            return False, "Quantidade a adicionar deve ser maior que zero."

    @staticmethod
    def subtrair_do_estoque(produto_id, quantidade):
        estoque_item = Estoque.query.filter_by(produto_id=produto_id).first()
        if estoque_item:
            if estoque_item.quantidade >= quantidade:
                estoque_item.quantidade -= quantidade
                try:
                    db.session.commit()
                    return True, None # Sucesso, sem mensagem de erro
                except Exception as e:
                    db.session.rollback()
                    return False, f"Erro ao atualizar o estoque no banco de dados: {e}"
            else:
                return False, f"Estoque insuficiente para o produto ID {produto_id}."
        else:
            return False, f"Item de estoque não encontrado para o produto ID {produto_id}."

    @staticmethod
    def get_estoque_por_produto_id(produto_id):
        return Estoque.query.filter_by(produto_id=produto_id).first()

    @staticmethod
    def get_todos_itens_estoque():
        return Estoque.query.all()

    @staticmethod
    def atualizar_valor_total_estoque(produto_id):
        estoque = Estoque.query.filter_by(produto_id=produto_id).first()
        produto = Produto.query.get(produto_id)
        if estoque and produto:
            estoque.valor_total = estoque.quantidade * produto.preco
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_valor_total_estoque():
        todos_estoques = Estoque.query.all()
        valor_total_geral = sum(estoque.valor_total for estoque in todos_estoques)
        return valor_total_geral

    @staticmethod
    def excluir_estoque_do_produto(produto_id):
        try:
            estoque = Estoque.query.filter_by(produto_id=produto_id).first()
            if estoque:
                produto = estoque.produto
                if produto:
                    db.session.delete(produto)
                    db.session.commit()
                    print(f"Produto {produto_id} e estoque deletados via estoque.")
                    return True
                else:
                    print(f"Produto associado ao estoque não encontrado para produto_id={produto_id}.")
                    return False
            else:
                print(f"Nenhum estoque encontrado para produto_id={produto_id}.")
                return False
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao excluir produto e estoque via estoque: {e}")
            return False