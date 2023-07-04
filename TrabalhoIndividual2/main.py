class Menu:
    # Método construtor
    def __init__(self):
        self.opcoesDisponiveis = {
            1: ['Frango: 3 minutos à 50°C', 3, 50.0],
            2: ['Pão: 1 minuto à 35°C', 1, 35.0],
            3: ['Carne: 4 minutos à 45°C', 4, 45.0],
            4: ['Batata: 2 minutos à 40°C', 2, 40.0]
        }

    # Método para inicializar o menu
    def inicializarMenu(self):
        print('\n*** Esta é a AirFryer da FGA! ***')
        print('É possível escolher entre três modos(Dashboard, Terminal Manual e Terminal Automático), além de poder encerrar o programa')
        print('Digite a opção que você quer executar:\n1 - Dashboard\n2 - Terminal Manual\n3 - Terminal Automático\n4 - Encerrar programa\n')
        modoEscolhido = self.escolherOpcao([1, 2, 3, 4], 'Digite a opção que você quer executar:\n1 - Dashboard\n2 - Terminal Manual\n3 - Terminal Automático\n4 - Encerrar programa\n')
        return modoEscolhido

    # Método para mostrar o menu do modo Terminal manual
    def terminalModoManual(self):
        print('\n *** Modo Terminal Manual ***')
        print('Informe a temperatura em °C (entre 30 e 70) e o tempo em minutos (entre 1 e 10): ')
        temperatura = False
        tempo = False
        while(temperatura == False):
            valorTemperatura = float(input("Informe a temperatura, em °C: "))
            if(valorTemperatura < 30 or valorTemperatura > 70):
                print("Digite uma temperatura válida\n")
            else:
                temperatura = True
        while(tempo == False):
            valorTempo = int(input("Informe o tempo, em minutos: "))
            if(valorTempo < 1 or valorTempo > 10):
                print("Digite um tempo válido\n")
            else:
                tempo = True

        print(f'Você selecionou: {valorTemperatura}°C e {valorTempo} minutos')
        return valorTemperatura, valorTempo

    # Método para mostrar o menu do modo Terminal automático
    def terminalModoAutomatico(self):
        print('\n *** Modo Terminal Automático ***')
        print('Escolha uma das seguintes opções pré-programadas: ')
        self.opcoesModoAutomatico()
        
        quantidadeOpcoes = len(self.opcoesDisponiveis)
        opcaoEscolhida = self.escolherOpcao(list(range(1, quantidadeOpcoes + 1)), '', automatico=1)

        print('Foi selecionada a opção: ', self.opcoesDisponiveis[opcaoEscolhida][0])
        return self.opcoesDisponiveis[opcaoEscolhida]

    # Método para selecionar a opção dentre as disponíveis
    def escolherOpcao(self, opcoesDisponiveis, enunciado, automatico=0):
        opcaoValida = False
        while(opcaoValida == False):
            opcaoEscolhida = int(input('Insira o valor desejado: '))
            if opcaoEscolhida in opcoesDisponiveis:
                opcaoValida = True
            else:
                print('Você não digitou uma opção válida')
        
        if automatico == 1:
            print('Selecione uma das seguintes opções: ')
            self.opcoesModoAutomatico()
        print(enunciado)
        return opcaoEscolhida

    # Método para imprimir as opções pré-selecionadas existentes no modo automático
    def opcoesModoAutomatico(self):
        for posicaoOpcao, nomeOpcao in self.opcoesDisponiveis.items():
            print(f'{posicaoOpcao} - {nomeOpcao[0]}')

from airFryer import ControleAirFryer

if __name__ == "__main__":
    controleAirFryer = ControleAirFryer()
    menu = Menu()

    modoAcionamento = menu.inicializarMenu()

    try:
        # modoAcionamento == 4 é para sair do programa
        while modoAcionamento != 4:
            # Modo Dashboard
            if modoAcionamento == 1:
                controleAirFryer.iniciar()
                controleAirFryer.modoDeInicio = "dashboard"
                print('\n**** Modo Dashboard ****')
                print('A airFryer será acionada assim que os botões de iniciar e funcionamento estiverem ON')

                try:
                    while(1):
                        controleAirFryer.uart.enviarMensagem('comandosDeUsuario')
                        controleAirFryer.receberComando()
                        if not controleAirFryer.funcionamentoDashboardThread and controleAirFryer.iniciaTemporizador == 1:
                            break
                except KeyboardInterrupt:
                    controleAirFryer.desligar()
                    pass

            # Modo Terminal Manual
            elif modoAcionamento == 2:
                controleAirFryer.modoDeInicio = "terminalManual"
                controleAirFryer.iniciar()
                valorTemperatura, valorTempo = menu.terminalModoManual()

                controleAirFryer.temperaturaReferencia = valorTemperatura
                controleAirFryer.tempo = valorTempo

                controleAirFryer.ligarAirFryer()
                controleAirFryer.iniciarAquecimentoAirFryer()
                                
            # Modo Terminal Automático
            elif modoAcionamento == 3:
                controleAirFryer.modoDeInicio = "terminalAutomatico"
                controleAirFryer.iniciar()
                opcaoTerminal = menu.terminalModoAutomatico()
                controleAirFryer.opcaoAutomatica = opcaoTerminal
                controleAirFryer.ligarAirFryer()
                controleAirFryer.iniciarAquecimentoAirFryer()

            modoAcionamento = menu.inicializarMenu()
        
        print('O sistema está sendo finalizado...')

    except KeyboardInterrupt:
        controleAirFryer.desligar()
        print("O programa está sendo finalizado...")
        exit()