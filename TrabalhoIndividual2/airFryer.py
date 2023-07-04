from pid import PID
from sensorBmp280 import SensorBMP
from lcd import LCD
from uart import Uart
from potencia import ControladorPWM
from geradorCsv import gerarLog

from time import sleep
from threading import Thread

class ControleAirFryer:
    # Método constutor
    def __init__(self):
        self.pid = PID()
        self.bmp = SensorBMP()
        self.lcd = LCD()
        self.uart = Uart()
        self.controladorPwm = ControladorPWM()
        self.ligado = False
        self.funcionando = False
        self.modoDeInicio = "dashboard"
        self.temperaturaInterna = 30.0
        self.temperaturaAmbiente = 25.0
        self.temperaturaReferencia = 35.0
        self.sinalControle = 0
        self.tempo = 0
        self.tempoRestante = 0
        self.opcaoAutomatica = None
        self.iniciaTemporizador = 0
        self.iterador = 0
        self.temporizador = 0
        self.funcionamentoDashboardThread = False
        self.funcionamentoTerminalManualThread = False
        self.funcionamentoTerminalAutomaticoThread = False
    
    # Método que prepara o dispositivo para funcionamento
    def iniciar(self):
        self.controladorPwm.iniciar()
        self.uart.enviarMensagem('sistemaDesligado')
        sleep(0.1)
        self.uart.enviarMensagem('funcionandoNao')
        self.uart.enviarMensagem('controleTemperaturaManual')

        self.uart.enviarMensagem('contadorTempo', 0)
        self.tempo = 0
        self.tempoRestante = 0
        self.iniciaTemporizador = 0
        self.iterador = 0
        print('O sistema foi inicializado')

    # Método que controla a temperatura da airFryer e calcula o sinal de controle para os atuadores
    def controlarTemperatura(self):
        # Se o dispositivo estiver em funcionamento, atualiza a temperatura ambiente
        if self.ligado and self.funcionando:
            self.temperaturaAmbiente = self.bmp.temperatura()
            self.uart.enviarMensagem('temperaturaAmbiente', self.temperaturaAmbiente)
            sleep(0.1)

            # Se estiver no modo dashboard, ajusta a temperatura de referência
            if self.modoDeInicio == "dashboard":
                if self.iterador == 0:
                    self.receberComando()
                    self.iterador = self.iterador + 1
                
                self.uart.enviarMensagem('temperaturaReferencia')
                descarte, valor = self.uart.receberMensagem()
                if type(valor) == float:
                    self.temperaturaReferencia = valor
            
            # Ajuste da temperatura interna
            self.uart.enviarMensagem('temperaturaInterna')
            sleep(0.5)
            descarte, valor = self.uart.receberMensagem()
            if valor == None:
                return
            self.temperaturaInterna = valor
            
            # Se ainda estiver ligado e funcionando, atualiza o valor de referência do PID e calcula o sinal de controle
            # O sinal de controle é usado para controlar os atuadores (resistor e ventoinha)
            if self.ligado and self.funcionando:
                self.pid.atualizarValorReferencia(self.temperaturaReferencia)
                self.sinalControle = self.pid.calculoPid(self.temperaturaInterna)
                self.controladorPwm.ventoinhaOuResistor(self.sinalControle)
                self.uart.enviarMensagem('sinalControle', self.sinalControle)
            sleep(0.1)
    
    # Método que chama o método executarModoSelecionado, passando o Modo Dashboard como parâmetro
    def modoUsoDashboard(self):
        while self.funcionamentoDashboardThread == True:
            self.executarModoSelecionado("Modo Dashboard")
        return

    # Método que chama o método executarModoSelecionado, passando o Modo Terminal Automático como parâmetro
    def modoUsoTerminalAutomatico(self):
        if self.opcaoAutomatica == None:
            print('Você não selecionou nenhum dos modos disponíveis')
            return
        else:
            # Informando tempo e sinal de controle
            self.tempo = self.opcaoAutomatica[1]
            self.uart.enviarMensagem('contadorTempo', self.tempo)
            self.temperaturaReferencia = self.opcaoAutomatica[2]
            self.uart.enviarMensagem('sinalReferencia', self.temperaturaReferencia)

        while self.funcionamentoTerminalAutomaticoThread == True:
            self.executarModoSelecionado("Modo Terminal Automático")
        return

    # Método que chama o método executarModoSelecionado, passando o Modo Terminal Manual como parâmetro
    def modoUsoTerminalManual(self):
        while self.funcionamentoTerminalManualThread == True:
            self.executarModoSelecionado("Modo Terminal Manual")
        return

    # De acordo com o modo selecionado, realiza diferentes operações
    def executarModoSelecionado(self, modoSelecionado):
        print(f'\nFoi selecionado o {modoSelecionado}!')
        print('Para abortar o funcionamento você precisa apertar CTRL+C')
        if modoSelecionado == "Modo Terminal Automático":
            print(self.opcaoAutomatica[0])

        if self.ligado == True and self.funcionando == True:
            self.controlarTemperatura()

            # Printa na tela o tempo restante da execução da airFryer de acordo com o escolhido pelo usuário
            if self.iniciaTemporizador == 1:
                self.tempoRestante = self.tempoRestante - 1
                print('Restam', self.tempoRestante, 'segundos para o fim da execução')
                if self.tempoRestante == 0:
                    print('Desligando... o período de aquecimento encerrou')
                    self.desligar()
                    return

            if self.iniciaTemporizador == 0 and (self.temperaturaInterna >= self.temperaturaReferencia - 2 and self.temperaturaInterna <= self.temperaturaReferencia + 2):
                self.tempoRestante = self.tempo * 60
                self.iniciaTemporizador = 1
                print('Restam', self.tempoRestante, 'segundos para o fim da execução')

            self.lcd.mostrarInfosDisplay(self.temperaturaAmbiente, self.temperaturaInterna, self.temperaturaReferencia, self.modoDeInicio, self.temporizador, self.tempoRestante)
            self.temporizador = self.temporizador + 1

            gerarLog(self.temperaturaInterna, self.temperaturaAmbiente, self.temperaturaReferencia, self.sinalControle)
        sleep(1)
    
    # Método que define o modo de funcionamento e inicia a correspondente Thread
    def iniciarAquecimentoAirFryer(self):
        if self.ligado and not self.funcionando:
            self.uart.enviarMensagem('funcionandoSim')
            self.funcionando = True

            if self.modoDeInicio == 'dashboard':
                self.funcionamentoDashboardThread = True
                self.uart.enviarMensagem('controleTemperaturaManual')
                self.threadModoDashboard = Thread(target=self.modoUsoDashboard)
                self.threadModoDashboard.start()
                self.threadModoDashboard.join()
                if not self.funcionamentoDashboardThread:
                    return
            
            elif self.modoDeInicio == "terminalManual":
                self.funcionamentoTerminalManualThread = True
                self.uart.enviarMensagem('controleTemperaturaManual')
                self.uart.enviarMensagem('sinalReferencia', self.temperaturaReferencia)
                self.uart.enviarMensagem('contadorTempo', self.tempo)

                self.threadModoTerminalManual = Thread(target=self.modoUsoTerminalManual)
                self.threadModoTerminalManual.start()
                self.threadModoTerminalManual.join()
                if not self.funcionamentoTerminalManualThread:
                    return
                    
            elif self.modoDeInicio == "terminalAutomatico":
                self.funcionamentoTerminalAutomaticoThread = True
                self.uart.enviarMensagem('controleTemperaturaAutomatico')
                self.threadModoTerminalAutomatico = Thread(target=self.modoUsoTerminalAutomatico)
                self.threadModoTerminalAutomatico.start() 
                self.threadModoTerminalAutomatico.join()
                if not self.funcionamentoTerminalAutomaticoThread:
                    return
                    
    # Método para ligar a airFryer, comunicando com a UART
    def ligarAirFryer(self):
        self.uart.enviarMensagem('sistemaLigado')
        self.ligado = True
    
    # Método para desligar a airFryer, comunicando com a UART
    def desligarAirFryer(self):
        self.uart.enviarMensagem('sistemaDesligado')
        self.ligado = False
        # print('Botão de ligado desativado')
        self.desligarAquecimentoAirFryer()
    
    # Método para desligar o aquecimento da airFryer, comunicando com a UART
    def desligarAquecimentoAirFryer(self):
        self.uart.enviarMensagem("funcionandoNao")
        self.funcionando = False
    
    # Método que adiciona mais tempo no tempo total de execução da airFryer
    def adicionarTempo(self):
        self.tempo = self.tempo + 1
        self.uart.enviarMensagem('contadorTempo', self.tempo)
    
    # Método que reduz tempo no tempo total de execução da airFryer
    def reduzirTempo(self):
        if self.tempo > 0:
            self.tempo = self.tempo - 1
        self.uart.enviarMensagem('contadorTempo', self.tempo)
    
    # Método para casos em que não é necessária nenhuma ação
    def passar(self):
        pass

    # Método que recebe e processa comandos do usuário através da UART
    def receberComando(self):
        sleep(0.1)
        comandos = {
            "ligaAirFryer": self.ligarAirFryer,
            "desligaAirFryer": self.desligarAirFryer,
            "iniciaAquecimento": self.iniciarAquecimentoAirFryer,
            "cancelaProcesso": self.desligarAquecimentoAirFryer,
            "adicionaTempo": self.adicionarTempo,
            "reduzTempo": self.reduzirTempo,
            "acionaMenu": "mudou menu",
        }

        comando, valor = self.uart.receberMensagem()
        if comando == 'comandosDeUsuario' and self.modoDeInicio == 'dashboard':
            comandos.get(valor, self.passar)()
        return 

    # Método em que fecha as conexões e desliga o sistema
    def desligar(self):
        self.funcionamentoDashboardThread = False
        self.funcionamentoTerminalManualThread = False
        self.funcionamentoTerminalAutomaticoThread = False

        self.uart.enviarMensagem('sinalControle', -100) 
        sleep(0.1)
        self.uart.enviarMensagem('sinalReferencia', self.temperaturaAmbiente)
        sleep(0.1)
        self.uart.enviarMensagem('sistemaDesligado')
        self.ligado = False
        sleep(0.1)
        self.uart.enviarMensagem('funcionandoNao')
        self.funcionando = False
        sleep(0.1)

        self.uart.enviarMensagem('controleTemperaturaManual')
        self.uart.enviarMensagem('contadorTempo', 0)

        self.controladorPwm.pararSinalPwm()
        self.bmp.fecharConexao()
        self.uart.fecharConexao()
        self.lcd.limparDisplay()
        print('O sistema foi desligado\n')