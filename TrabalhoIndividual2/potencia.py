import RPi.GPIO as GPIO

class ControladorPWM:
    # Método construtor
    def __init__(self):
        self.pinoResistor = 23
        self.pinoVentoinha = 24

        # Configuração dos pinos GPIO:
        # GPIO definida como BCM e pinos do resistor e da ventoinha configurados como pinos de saída
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pinoResistor, GPIO.OUT)
        GPIO.setup(self.pinoVentoinha, GPIO.OUT)

        self.pwmResistor = GPIO.PWM(self.pinoResistor, 1200)
        self.pwmVentoinha = GPIO.PWM(self.pinoVentoinha, 1200)
    
    # Método que inicializa o sinal PWM para o resistor e a ventoinha, com os ciclos de trabalho em 0%
    def iniciar(self, cicloTrabalhoInicial=0):
        self.pwmResistor.start(cicloTrabalhoInicial)
        self.pwmVentoinha.start(cicloTrabalhoInicial)

    # Método que permite alterar o ciclo de trabalho do resistor
    def alterarCicloTrabalhoResistor(self, cicloTrabalho):
        self.pwmResistor.ChangeDutyCycle(cicloTrabalho)

    # Método que permite alterar o ciclo de trabalho da ventoinha
    def alterarCicloTrabalhoVentoinha(self, cicloTrabalho):
        self.pwmVentoinha.ChangeDutyCycle(cicloTrabalho)

    # Método que define se vai trabalhar a ventoinha ou o resistor
    # Se o sinal for negativo, trabalhará a ventoinha
    # Se o sinal for positivo, trabalhará o resistor
    def ventoinhaOuResistor(self, sinalControle):
        if sinalControle < 0:
            self.alterarCicloTrabalhoResistor(0)
            self.alterarCicloTrabalhoVentoinha(-sinalControle)
        else:
            self.alterarCicloTrabalhoResistor(sinalControle)
            self.alterarCicloTrabalhoVentoinha(0)

    # Método que para o sinal PWM para o resistor e a ventoinha, "limpando" os pinos da GPIO
    def pararSinalPwm(self):
        self.pwmResistor.stop()
        self.pwmVentoinha.stop()
        GPIO.cleanup()