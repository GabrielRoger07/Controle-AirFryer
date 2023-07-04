import i2c as i2c

class LCD:
    # Método construtor
    def __init__(self):
        self.lcd = i2c.lcd()

    # Método para mostrar as informações no display
    def mostrarInfosDisplay(self, temperaturaAmbiente, temperaturaInterna, temperaturaReferencia, modoDeInicio, temporizador, tempoRestante):    
        self.lcd.lcd_clear()
        
        if temporizador % 2 == 0:
            self.lcd.lcd_display_string(f"ta:{str(round(temperaturaAmbiente, 1))} tr:{str(round(temperaturaReferencia, 1))}", 1)

            # Só irá mostrar o tempo restante se estiver na temperatura ideal 
            if temperaturaInterna - temperaturaReferencia > 2 or temperaturaReferencia - temperaturaInterna > 2:
                 self.lcd.lcd_display_string(f"ti:{str(round(temperaturaInterna, 1))}", 2)
            else:
                self.lcd.lcd_display_string(f"ti:{str(round(temperaturaInterna, 1))} time:{tempoRestante}", 2)

        elif temporizador % 2 != 0: 
            if modoDeInicio == "dashboard":
                self.lcd.lcd_display_string("Modo dashboard", 1)
            elif modoDeInicio == "terminalManual":
                self.lcd.lcd_display_string("Modo manual", 1)
            elif modoDeInicio == "terminalAutomatico":
                self.lcd.lcd_display_string("Modo automatico", 1)


            # Se a diferença entre temperaturaInterna e temperaturaReferencia for maior que 2,
            # significa que ainda não foi atingida a temperatura ideal e o temporizador não
            # começou ainda
            if temperaturaInterna - temperaturaReferencia > 2:
                self.lcd.lcd_display_string("Pre-Resfriando...", 2)
            elif temperaturaReferencia - temperaturaInterna > 2:
                self.lcd.lcd_display_string("Pre-Aquecendo...", 2)
            else:
                self.lcd.lcd_display_string("Temperatura OK", 2)

    # Método para limpar o display
    def limparDisplay(self):
        self.lcd.lcd_clear()