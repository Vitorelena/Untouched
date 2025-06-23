from abc import ABC, abstractmethod
from .CarrinhoDeCompras import CarrinhoDeCompras

class ProcessadorDeCompra(ABC):
    @abstractmethod
    def processar_compra(self, carrinho: CarrinhoDeCompras, usuario = None):
        pass
    @abstractmethod
    def verificar_estoque(self, carrinho: CarrinhoDeCompras) -> bool:
        pass
    @abstractmethod
    def atualizar_estoque(self, carrinho: CarrinhoDeCompras) -> bool:
        pass
    @abstractmethod
    def registrar_venda(self, carrinho: CarrinhoDeCompras, usuario = None) -> bool:
        pass
                        