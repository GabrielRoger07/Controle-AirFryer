import serial
from time import sleep

from modbus import codificarMensagem, decodificarMensagem

class Uart:
    # Método construtor
    def __init__(self):
        self.porta = "/dev/serial0"
        self.taxaTransmissao = 9600
        self.estaConectado = False

    # Método para estabelecer conexão com a UART
    def estabelecerConexao(self):
        # Se já não estiver conectado, tenta estabelecer conexão com a porta serial que foi definida
        if not self.estaConectado:
            try:
                self.serial = serial.Serial(self.porta, self.taxaTransmissao)
                self.estaConectado = True
                print('A conexão UART foi estabelecida!')
            except serial.SerialException as e:
                print('Não foi possível estabelecer conexão UART:', str(e))
    
    # Método para codificar e enviar mensagem
    def enviarMensagem(self, mensagemEnviada, valor=None):
        self.estabelecerConexao()
        # Se estiver conectado, codifica a mensagem recebida e a envia, após ser codificada, pela porta serial
        if self.estaConectado == True:
            mensagemCodificada = codificarMensagem(mensagemEnviada, valor)
            if mensagemCodificada is not None:
                self.serial.write(mensagemCodificada)
            else:
                raise Exception('Ocorreu um erro no processo de codificação da mensagem')
        else:
            raise Exception('Não está conectado!')

    # Método para receber e decodificar mensagem
    def receberMensagem(self):
        self.estabelecerConexao()
        # Se estiver conectado, decodifica a mensagem recebida pela porta serial e retorna a mensagem e o valor decodificados
        if self.estaConectado == True:
            sleep(0.1)
            try:
                buffer = self.serial.read(9)
                msg, valor = decodificarMensagem(buffer)
                self.serial.reset_input_buffer()
                return msg, valor
            except serial.SerialException as e:
                raise Exception('Ocorreu um erro no recebimento da mensagem:', str(e))
        else:
            raise Exception('Não está conectado!')

    # Método para fechar a conexão estabelecida
    def fecharConexao(self):
        if self.estaConectado:
            self.serial.close()
            self.estaConectado = False
            print('A conexão UART foi fechada!')