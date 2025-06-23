from ..model.Vendas.Venda import Venda
from ..model.Vendas.ItemVendido import ItemVendido

class VendaDatabaseService:
    @staticmethod
    def venda_por_cliente(cliente_id):
        return(Venda.query.filter_by(cliente_id=cliente_id).all())
    
    @staticmethod
    def buscar_historico_compras(cliente_id):    
        return Venda.query.filter_by(cliente_id=cliente_id).order_by(Venda.data_venda.desc()).all()
    
    @staticmethod
    def get_itens_by_venda(venda_id):
        return ItemVendido.query.filter_by(venda_id=venda_id).all()