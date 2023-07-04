import struct

# Método para calcular o valor do crc
def calcularCrc(data):
    crc = 0x0000
    for byte in data:
        # Faz um XOR do valor atual do crc com o byte atual
        crc ^= byte
        for _ in range(8): # 8 vezes, uma vez para cada bit no byte
            if crc & 0x0001:
                crc >>= 1
                # Se o bit menos significativo do crc for 1, desloca um bit para a direita e faz um XOR com 0xA001
                crc ^= 0xA001
            else:
                # Se o bit menos significativo não for 1, simplesmente desloca um bit para a direita
                crc >>= 1
    return crc

# Método para verificar se o crc é válido
def verificarCrc(buffer):
    crcValido = calcularCrc(buffer[:-2]).to_bytes(2, "little")
    crcRecebido = buffer[-2:]
    if crcRecebido != crcValido:
        raise Exception('CRC inválido')

ultimosDigitosMatricula = [8, 2, 4, 8]

# Tabela com Códigos do Protocolo de Comunicação

# Endereço da ESP32    Código    Sub-código + Matricula    Comando de Solicitação de Dados    Mensagem de Retorno
# 0x01    0x23    0xC1 N N N N    Solicita Temperatura Interna    0x00 0x23 0xC1 + float (4 bytes)
# 0x01    0x23    0xC2 N N N N    Solicita Temperatura de Referência    0x00 0x23 0xC2 + float (4 bytes)
# 0x01    0x23    0xC3 N N N N    Lê comandos do usuário    0x00 0x23 0xC3 + int (4 bytes de comando)
# 0x01    0x16    0xD1 N N N N    Envia sinal de controle Int (4 bytes)    0x00 0x16 0xD1
# 0x01    0x16    0xD2 N N N N    Envia sinal de Referência Float (4 bytes)    0x00 0x16 0xD2
# 0x01    0x16    0xD3 N N N N    Envia Estado do Sistema (Ligado = 1 / Desligado = 0)    0x00 0x16 0xD3 + int (4 bytes de estado)
# 0x01    0x16    0xD4 N N N N    Modo de Controle da Temperatura de referência (Dashboard = 0 / Curva/Terminal = 1) (1 byte)    0x00 0x16 0xD4 + int (4 bytes de modo de controle)
# 0x01    0x16    0xD5 N N N N    Envia Estado de Funcionamento (Funcionando = 1 / Parado = 0)    0x00 0x16 0xD5 + int (4 bytes de estado)
# 0x01    0x16    0xD6 N N N N    Envia Temperatura Ambiente (Float))    0x00 0x16 0xD6 + float (4 bytes)
# 0x01    0x16    0xD7 N N N N    Envia Contador de Tempo (usado no modo de pré-programação)    0x00 0x16 0xD7 + int (4 bytes )
# 0x01    0x16    0xD8 N N N N    Envia String do Display LCD para o Dashboard    0x00 0x16 0xD8 + 1 byte: tamanho da string + N bytes da String 

codigosProtocoloComunicacao = {
    "temperaturaInterna": [0x01, 0x23, 0xC1, *ultimosDigitosMatricula],
    "temperaturaReferencia": [0x01, 0x23, 0xC2, *ultimosDigitosMatricula],
    "comandosDeUsuario": [0x01, 0x23, 0xC3, *ultimosDigitosMatricula],
    "sinalControle": [0x01, 0x16, 0xD1, *ultimosDigitosMatricula],
    "sinalReferencia": [0x01, 0x16, 0xD2, *ultimosDigitosMatricula],
    "sistemaLigado": [0x01, 0x16, 0xD3, *ultimosDigitosMatricula, 1],
    "sistemaDesligado": [0x01, 0x16, 0xD3, *ultimosDigitosMatricula, 0],
    "controleTemperaturaManual": [0x01, 0x16, 0xD4, *ultimosDigitosMatricula, 0],
    "controleTemperaturaAutomatico": [0x01, 0x16, 0xD4, *ultimosDigitosMatricula, 1],
    "funcionandoSim": [0x01, 0x16, 0xD5, *ultimosDigitosMatricula, 1],
    "funcionandoNao": [0x01, 0x16, 0xD5, *ultimosDigitosMatricula, 0],
    "temperaturaAmbiente": [0x01, 0x16, 0xD6, *ultimosDigitosMatricula],
    "contadorTempo": [0x01, 0x16, 0xD7, *ultimosDigitosMatricula],
    "stringDisplayLCD": [0x01, 0x16, 0xD8, *ultimosDigitosMatricula]
}

mensagensRetorno = {
    0xC1: "temperaturaInterna",
    0xC2: "temperaturaReferencia",
    0xC3: "comandosDeUsuario"
}

# Tabela com Comandos de Usuário via UART

# Comando                                               Código
# Liga a AirFryer                                       0x01
# Desliga a AirFryer                                    0x02
# Inicia Aquecimento                                    0x03
# Cancela Processo                                      0x04
# Tempo +: Adiciona 1 minuto ao timer                   0x05
# Tempo -: Reduz 1 minuto ao timer                      0x06
# Menu: Aciona o modo de alimentos pré-programados      0x07

comandosUsuario = {
    0x01: "ligaAirFryer",
    0x02: "desligaAirFryer",
    0x03: "iniciaAquecimento",
    0x04: "cancelaProcesso",
    0x05: "adicionaTempo",
    0x06: "reduzTempo",
    0x07: "acionaMenu"
}

# Método para codificar mensagem de acordo com o protocolo
def codificarMensagem(codigo, valor=None):
    try:
        mensagem = bytes(codigosProtocoloComunicacao.get(codigo, None)) 
    except TypeError:
        return None 
    
    if valor is not None:
        if isinstance(valor, int):
            valor = struct.pack("<i", valor)
        elif isinstance(valor, float):
            valor = struct.pack("<f", round(valor, 2))
        elif isinstance(valor, str):
            valor = valor.encode('utf-8')
        else:
            raise ValueError('O tipo do valor não é um tipo válido!')
        
        mensagem += valor

    # Calcula o crc e adiciona na mensagem, a codificando
    crcMensagem = calcularCrc(mensagem)
    mensagemCodificada = mensagem + crcMensagem.to_bytes(2, "little")
    return mensagemCodificada

# Método que recebe um buffer de dados, retornando a mensagem decodificada e o valor extraído
def decodificarMensagem(buffer):
    verificarCrc(buffer)

    tamanho = len(buffer)
    if tamanho == 9:
        
        # Extrai o código, o código da mensagem e o valor do buffer
        codigo, codigoMensagem, valor = (buffer[1], buffer[2], buffer[3:7])

        # Código 0x23: código para solicitar dados
        if codigo == 0x23:
            if codigoMensagem in [0xC1, 0xC2]:
                # Retorna a chave correspondente na tabela de mensagens de retorno e o valor como um float 
                # com duas casas decimais
                return mensagensRetorno[codigoMensagem], round(struct.unpack("<f", valor)[0], 2)
            elif codigoMensagem == 0xC3:
                # Retorna a chave correspondente na tabela de mensagens de retorno e o comando do usuário 
                # correspondente ao valor
                return mensagensRetorno[codigoMensagem], comandosUsuario.get(struct.unpack("<i", valor)[0])
        # Código 0x16: código para enviar dados
        elif codigo == 0x16:
            # Retorna None para ambos os valores, pois não há dados para extrair
            return None, None
        
    # Se o tamanho do buffer não for 9, retorna None para ambos os valores
    return None, None