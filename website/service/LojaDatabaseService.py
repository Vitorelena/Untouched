from .. import db
from ..model.Loja import Loja # Importar o modelo Loja

from .. import db
from ..model.Loja import Loja

class LojaDatabaseService:
    @staticmethod
    def adicionar_loja(endereco, cnpj, latitude, longitude, nome):
        try:
            nova_loja = Loja(endereco, cnpj, latitude, longitude, nome)
            db.session.add(nova_loja)
            db.session.commit()
            return nova_loja
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao adicionar loja: {e}")
            return None

    @staticmethod
    def listar_lojas():
        return Loja.query.all()

    @staticmethod
    def excluir_loja(loja_id):
        loja = Loja.query.get(loja_id)
        if loja:
            try:
                db.session.delete(loja)
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao excluir loja: {e}")
                return False
        return False