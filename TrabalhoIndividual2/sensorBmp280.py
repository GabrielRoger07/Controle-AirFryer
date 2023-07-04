from bmp280 import BMP280
from smbus import SMBus

class SensorBMP:
    # Método construtor
    def __init__(self):
        self.endereco = 0x76
    
    # Método que retorna a temperatura do sensor
    def temperatura(self):
        self.bus = SMBus(1)
        self.bmp280 = BMP280(i2c_dev=self.bus)
        temperatura = self.bmp280.get_temperature()
        return round(temperatura, 2)
    
    # Método para fechar a conexão
    def fecharConexao(self):
        self.bus.close()