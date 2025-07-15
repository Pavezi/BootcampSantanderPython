

# Importações necessárias
import textwrap
from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime

# --- Classes de Domínio ---

# Conceito: Abstração e Herança
# A classe Cliente é uma abstração para qualquer tipo de cliente do banco.
# Ela define o comportamento básico que um cliente deve ter, como ter contas e realizar transações.
# PessoaFisica herda de Cliente, especializando-a com atributos específicos de uma pessoa física.
class Cliente:
    """
    Representa um cliente do banco.
    
    Atributos:
        endereco (str): O endereço do cliente.
        contas (list): Lista de contas associadas ao cliente.
    """
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    # Conceito: Composição
    # O método realizar_transacao delega a responsabilidade de registrar a transação
    # para o objeto Transacao, demonstrando composição. O cliente "tem uma" transação.
    def realizar_transacao(self, conta, transacao):
        """Realiza uma transação em uma das contas do cliente."""
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        """Adiciona uma nova conta à lista de contas do cliente."""
        self.contas.append(conta)


class PessoaFisica(Cliente):
    """
    Representa um cliente do tipo Pessoa Física, herdando da classe Cliente.
    
    Atributos:
        nome (str): Nome completo do cliente.
        data_nascimento (str): Data de nascimento no formato dd-mm-aaaa.
        cpf (str): CPF do cliente (somente números).
    """
    def __init__(self, nome, data_nascimento, cpf, endereco):
        # Conceito: Herança
        # super().__init__() chama o construtor da classe pai (Cliente)
        # para inicializar os atributos herdados.
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


# Conceito: Encapsulamento
# Atributos como _saldo, _numero, etc., são prefixados com um underscore,
# indicando que são "protegidos" e não devem ser acessados diretamente fora da classe.
# O acesso é feito através de properties.
class Conta:
    """
    Classe base para contas bancárias.
    
    Atributos:
        _saldo (float): Saldo da conta.
        _numero (int): Número da conta.
        _agencia (str): Número da agência.
        _cliente (Cliente): Objeto cliente associado à conta.
        _historico (Historico): Objeto que armazena o histórico de transações.
    """
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    # Conceito: Método de Classe (@classmethod)
    # Permite criar uma nova instância da classe sem precisar instanciá-la diretamente.
    # É uma "fábrica" de objetos Conta.
    @classmethod
    def nova_conta(cls, cliente, numero):
        """Cria uma nova conta."""
        return cls(numero, cliente)

    # Conceito: Properties
    # Properties permitem tratar métodos como atributos, oferecendo uma interface
    # de acesso controlada aos atributos "protegidos".
    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        """Realiza um saque na conta se houver saldo suficiente."""
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
        elif valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
        return False

    def depositar(self, valor):
        """Realiza um depósito na conta."""
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False


# Conceito: Herança e Polimorfismo
# ContaCorrente herda de Conta e especializa seu comportamento.
# O método sacar é um exemplo de polimorfismo, pois ele sobrescreve o
# método da classe pai, adicionando novas regras (limite de valor e de saques).
class ContaCorrente(Conta):
    """
    Representa uma Conta Corrente, que herda de Conta.
    
    Atributos:
        limite (float): Limite de valor por saque.
        limite_saques (int): Número máximo de saques permitidos.
    """
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    # Conceito: Polimorfismo (Sobrescrita de Método)
    # O método sacar da ContaCorrente tem um comportamento diferente do método sacar da Conta.
    def sacar(self, valor):
        """Realiza um saque aplicando as regras de limite e número de saques."""
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
        else:
            # Se passar nas validações, chama o método da classe pai para efetuar o saque.
            return super().sacar(valor)
        return False

    # O método __str__ é um "método mágico" que define a representação em string do objeto.
    def __str__(self):
        """Retorna uma representação em string da conta."""
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class Historico:
    """Armazena o histórico de transações de uma conta."""
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        """Adiciona uma transação ao histórico."""
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

# Conceito: Classe Abstrata (ABC - Abstract Base Class)
# Transacao é uma classe abstrata que define um "contrato".
# Qualquer classe que herdar de Transacao DEVE implementar a property 'valor'
# e o método 'registrar'. Isso garante uma interface comum para todas as transações.
class Transacao(ABC):
    """Classe base abstrata para todas as transações."""
    @property
    @abstractproperty
    def valor(self):
        """Property abstrata para o valor da transação."""
        pass

    @abstractmethod
    def registrar(self, conta):
        """Método abstrato para registrar a transação na conta."""
        pass


class Saque(Transacao):
    """Representa uma transação de saque."""
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        """Registra o saque na conta."""
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    """Representa uma transação de depósito."""
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        """Registra o depósito na conta."""
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


# --- Funções Auxiliares (Interface com o Usuário) ---

def menu():
    """Exibe o menu de opções e retorna a escolha do usuário."""
    menu_text = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu_text))


def filtrar_cliente(cpf, clientes):
    """Busca um cliente na lista pelo CPF."""
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    """Recupera uma conta de um cliente, permitindo a escolha se houver várias."""
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return None

    # Se o cliente tiver apenas uma conta, retorna essa conta diretamente.
    if len(cliente.contas) == 1:
        return cliente.contas[0]

    # Se o cliente tiver várias contas, permite a escolha.
    print("\nO cliente possui mais de uma conta. Por favor, escolha uma:")
    for i, conta in enumerate(cliente.contas):
        print(f"[{i + 1}] Conta Corrente nº: {conta.numero}")

    while True:
        try:
            escolha = int(input("Digite o número da conta desejada: "))
            if 1 <= escolha <= len(cliente.contas):
                return cliente.contas[escolha - 1]
            else:
                print("\n@@@ Opção inválida. Por favor, escolha um número da lista. @@@")
        except ValueError:
            print("\n@@@ Entrada inválida. Por favor, digite um número. @@@")



def depositar(clientes):
    """Função para orquestrar a operação de depósito."""
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    try:
        valor = float(input("Informe o valor do depósito: "))
        transacao = Deposito(valor)
    except ValueError:
        print("\n@@@ Valor inválido! A operação de depósito foi cancelada. @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    """Função para orquestrar a operação de saque."""
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    try:
        valor = float(input("Informe o valor do saque: "))
        transacao = Saque(valor)
    except ValueError:
        print("\n@@@ Valor inválido! A operação de saque foi cancelada. @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    """Função para exibir o extrato de um cliente."""
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f} - {transacao['data']}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")


def criar_cliente(clientes):
    """Função para criar um novo cliente (Pessoa Física)."""
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")


def criar_conta(numero_conta, clientes):
    """Função para criar uma nova conta corrente."""
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado. Por favor, crie um novo usuário (opção 'nu') antes de criar uma conta. @@@")
        return None

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    cliente.adicionar_conta(conta)

    print("\n=== Conta criada com sucesso! ===")
    return conta


def listar_contas(contas):
    """Lista todas as contas criadas."""
    if not contas:
        print("\n@@@ Nenhuma conta foi criada ainda. @@@")
        return
        
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


# --- Função Principal ---

def main():
    """
    Função principal que executa o loop do sistema bancário.
    Aqui, as listas 'clientes' e 'contas' armazenam o estado do sistema em memória.
    """
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)
        elif opcao == "s":
            sacar(clientes)
        elif opcao == "e":
            exibir_extrato(clientes)
        elif opcao == "nu":
            criar_cliente(clientes)
        elif opcao == "nc":
            numero_conta = len(contas) + 1
            nova_conta = criar_conta(numero_conta, clientes)
            if nova_conta:
                contas.append(nova_conta)
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "q":
            print("\nSaindo do sistema... Obrigado por usar nosso banco!")
            break
        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


# Ponto de entrada do programa
# A verificação if __name__ == "__main__": garante que a função main()
# só será executada quando o script for rodado diretamente.
if __name__ == "__main__":
    main()
