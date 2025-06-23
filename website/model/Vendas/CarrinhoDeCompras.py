class CarrinhoDeCompras:
    def __init__(self):
        self.itens = {}
    
    def adicionar_item(self, produto_id, quantidade = 1):
        produto_id = str(produto_id)
        if produto_id in self.itens:
            self.itens[produto_id] += quantidade
        else:
            self.itens[produto_id] = quantidade
    
    def remover_item(self, produto_id):
        produto_id = str(produto_id)
        if produto_id in self.itens:
            del self.itens[produto_id]
    
    def atualizar_quantidade(self, produto_id, quantidade):
        produto_id = str(produto_id)
        if produto_id in self.itens:
            if quantidade > 0:
                self.itens[produto_id] = quantidade
            else:
                self.remover_item(produto_id)
    
    def obter_itens(self):
        return self.itens
    
    def calcular_total(self, produto_service):
        total = 0
        for produto_id, quantidade in self.itens.items():
            produto_id = int(produto_id)
            produto = produto_service.get_produto_por_id(produto_id)
            if produto:
                total += produto.preco * quantidade
        return total
    
    def esvaziar(self):
        self.itens = {}
    
    def __len__(self):
        return sum(self.itens.values())