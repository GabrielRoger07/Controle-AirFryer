class PID:
    # Método construtor
    def __init__(self, valorMaxSinalControle=100.0, valorMinSinalControle=-100.0):
        # Kp -> coeficiente proporcional
        self.Kp = 30.0
        # Ki -> coeficiente integral
        self.Ki = 0.2
        # Kd -> coeficiente derivativo
        self.Kd = 400.0
        # T -> período de amostragem
        self.T = 1.0

        self.valorReferencia = 0.0
        self.erroTotal = 0.0
        self.erroAnterior = 0.0

        # valorMaxSinalControle e valorMinSinalControle são os limites do sinal de controle
        self.valorMaxSinalControle = valorMaxSinalControle
        self.valorMinSinalControle = valorMinSinalControle

    # Método para atualizar o valor de referência
    def atualizarValorReferencia(self, valorReferencia):
        self.valorReferencia = valorReferencia

    # Método para calcular o PID
    def calculoPid(self, medidaAtual):
        erro = self.valorReferencia - medidaAtual

        self.erroTotal = self.erroTotal + erro

        if self.erroTotal <= self.valorMinSinalControle:
            self.erroTotal = self.valorMinSinalControle
        elif self.erroTotal >= self.valorMaxSinalControle:
            self.erroTotal = self.valorMaxSinalControle

        sinalControle = ((self.Kp * erro) + (self.Ki * self.T) * self.erroTotal + (self.Kd / self.T) * (erro - self.erroAnterior))

        if sinalControle <= self.valorMinSinalControle:
            sinalControle = self.valorMinSinalControle
        elif sinalControle >= self.valorMaxSinalControle:
            sinalControle = self.valorMaxSinalControle
            
        if sinalControle < 0 and sinalControle > -40:
            sinalControle = -40

        self.erroAnterior = erro

        return int(sinalControle)
