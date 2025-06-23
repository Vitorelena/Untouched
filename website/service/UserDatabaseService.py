from .. import db
from ..model.Users.User import User
from ..model.Users.Staff import Staff
from ..model.Users.SubGerente import SubGerente
from ..model.Users.Gerente import Gerente
from ..model.Users.Cliente import Cliente
from ..model.Users.Funcionario import Funcionario
from ..model.Users.Ceo import Ceo
from ..model.Vendas.Venda import Venda  

class UserDatabaseService:
    @staticmethod
    def adicionar_staff(nome, cpf, login, senha, matricula):
        novo_funcionario = Staff(nome, cpf, login, senha, matricula)
        db.session.add(novo_funcionario)
        db.session.commit()
        return novo_funcionario

    @staticmethod
    def adicionar_subgerente(nome, cpf, login, senha, matricula):
        novo_funcionario = SubGerente(nome, cpf, login, senha, matricula)
        db.session.add(novo_funcionario)
        db.session.commit()
        return novo_funcionario  

    @staticmethod
    def adicionar_gerente(nome, cpf, login, senha, matricula):
        novo_funcionario = Gerente(nome, cpf, login, senha, matricula)
        db.session.add(novo_funcionario)
        db.session.commit()
        return novo_funcionario

    @staticmethod
    def adicionar_ceo(nome, cpf, login, senha, matricula):
        novo_funcionario = Ceo(nome, cpf, login, senha, matricula)
        db.session.add(novo_funcionario)
        db.session.commit()
        return novo_funcionario

    @staticmethod
    def adicionar_cliente(nome, cpf, login, senha):
        novo_cliente = Cliente(nome, cpf, login, senha)
        db.session.add(novo_cliente)
        db.session.commit()
        return novo_cliente

    
    @staticmethod
    def obter_usuario_por_id(usuario_id):
        return User.query.get(usuario_id)
    
    @staticmethod
    def listar_usuarios():
        return User.query.all()
    
    @staticmethod
    def listar_funcionarios(exclude_ceo=False): # Adicionar opção para excluir CEO
        """Lista todos os usuários que são funcionários (incluindo Staff, SubGerente, Gerente, CEO)."""
        query = Funcionario.query # Isso já filtra para Funcionario e suas subclasses
        if exclude_ceo:
            query = query.filter(User.tipo_usuario != 7) # Filtra onde tipo_usuario não é 7 (CEO)
        return query.all()
    
    @staticmethod
    def listar_clientes():
        return Cliente.query.all()
    
    @staticmethod
    def editar_funcionario(usuario_id , nome=None, cpf=None, login=None, senha=None, matricula=None, numero_vendas=None):
        funcionario = Funcionario.query.get(usuario_id)
        if funcionario and funcionario.tipo_usuario >= 3:
            if nome:
                funcionario.nome = nome
            if cpf:
                funcionario.cpf = cpf
            if login:
                funcionario.login = login
            if senha:
                funcionario.senha = senha
            if matricula:
                funcionario.matricula = matricula
            if numero_vendas is not None:
                funcionario.numero_vendas = numero_vendas
            db.session.commit()
            return(True)
        return(False)
    
    @staticmethod
    def promover_funcionario(funcionario_id):
        """
        Promove um funcionário para o próximo nível/cargo, se elegível.
        Retorna (True, 'Mensagem de Sucesso') ou (False, 'Mensagem de Erro').
        """
        funcionario = Funcionario.query.get(funcionario_id)
        if not funcionario:
            return False, "Funcionário não encontrado."

        # Gerente (tipo_usuario 6) e CEO (tipo_usuario 7) não podem ser promovidos
        if funcionario.tipo_usuario == 6 or funcionario.tipo_usuario == 7:
            return False, f"{funcionario.nome} já está no cargo máximo ou não é elegível para promoção."

        # Regras de Promoção
        novo_tipo_usuario = None
        novo_nivel = None
        mensagem_sucesso = ""

        # Staff (tipo_usuario 4, nivel 1)
        if funcionario.tipo_usuario == 4 and funcionario.nivel == 1:
            # Opções de promoção: SubGerente (tipo 5, nivel 2) ou Gerente (tipo 6, nivel 3)
            # Para simplificar a lógica inicial, vamos promover Staff para SubGerente diretamente.
            # Se você quiser permitir Staff -> Gerente, a UI precisaria de uma escolha.
            novo_tipo_usuario = 5 # SubGerente
            novo_nivel = 2      # Nível de SubGerente
            mensagem_sucesso = f"Funcionário '{funcionario.nome}' promovido para SubGerente."

        # SubGerente (tipo_usuario 5, nivel 2)
        elif funcionario.tipo_usuario == 5 and funcionario.nivel == 2:
            novo_tipo_usuario = 6 # Gerente
            novo_nivel = 3      # Nível de Gerente
            mensagem_sucesso = f"Funcionário '{funcionario.nome}' promovido para Gerente."
        
        # Se chegou aqui e não se encaixou nas regras de promoção (ex: tipo 3 - Funcionario base, mas sem nível 1)
        else:
             return False, "Funcionário não elegível para promoção neste momento."


        if novo_tipo_usuario is not None:
            # Atualiza o tipo de usuário e o nível
            funcionario.tipo_usuario = novo_tipo_usuario
            funcionario.nivel = novo_nivel
            
            try:
                db.session.commit()
                return True, mensagem_sucesso
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao promover funcionário {funcionario.nome}: {e}")
                return False, f"Erro no banco de dados ao promover: {e}"
        
        return False, "Regras de promoção não aplicadas." # Fallback de segurança
    
    @staticmethod 
    def funcionario_fez_venda(usuario_id):
        funcionario = Funcionario.query.get(usuario_id)
        if funcionario and funcionario.tipo_usuario >= 3:
            funcionario.numero_vendas += 1
            db.session.commit()
            return(True)
        return(False)
    
    @staticmethod
    def editar_cliente(usuario_id, nome=None, cpf=None, login=None, senha=None, numero_compras=None):
        cliente = Cliente.query.get(usuario_id)
        if cliente and cliente.tipo_usuario == 2:
            if nome:
                cliente.nome = nome
            if cpf:
                cliente.cpf = cpf
            if login:
                cliente.login = login
            if senha:
                cliente.senha = senha
            if numero_compras is not None:
                cliente.numero_compras = numero_compras
            db.session.commit()
            return(True)
        return(False)
    
    @staticmethod
    def cliente_fez_compra(usuario_id):
        cliente = Cliente.query.get(usuario_id)
        if cliente and cliente.tipo_usuario == 2:
            cliente.numero_compras += 1
            db.session.commit()
            return(True)
        return(False)
    
    @staticmethod
    def deletar_usuario(usuario_id):
        usuario = User.query.get(usuario_id)
        if usuario:
            db.session.delete(usuario) 
            db.session.commit()
            return(True)
        return(False)       
    @staticmethod
    def deletar_usuario_funcionario(funcionario_id):
        """
        Deleta um funcionário pelo ID, com verificações de segurança.
        Retorna (True, 'Mensagem de Sucesso') ou (False, 'Mensagem de Erro').
        """
        funcionario = Funcionario.query.get(funcionario_id)
        if not funcionario:
            return False, "Funcionário não encontrado."
        
        # Não permitir deletar CEOs através desta função (se você tiver apenas um CEO e for ele)
        # Ou se o CEO que está logado não puder deletar a si mesmo (o controller já verifica isso)
        if funcionario.tipo_usuario == 7: # CEO
            return False, "Não é permitido desligar a conta de CEO por esta função."

        try:
            db.session.delete(funcionario)
            db.session.commit()
            return True, f"Funcionário '{funcionario.nome}' (ID: {funcionario_id}) desligado com sucesso."
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao desligar funcionário {funcionario_id}: {e}")
            return False, f"Erro no banco de dados ao desligar funcionário: {e}"
   
    @staticmethod
    def get_nome_por_id(usuario_id):
        usuario = User.query.get(usuario_id)
        if usuario:
            return usuario.nome
        return None