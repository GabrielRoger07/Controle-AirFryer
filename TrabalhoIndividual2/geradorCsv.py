import csv
from datetime import datetime
import os

def gerarLog(temperaturaInterna, temperaturaAmbiente, temperaturaReferencia, sinalControle):
    arquivoGerado = "./tabelaCsv.csv"

    # Remove o arquivo caso já exista, sendo assim, sempre atualizando para a última execução
    if not os.path.exists(arquivoGerado):
        with open(arquivoGerado, "w") as arquivoCsv:
            arquivoCsv.write("Data e hora, Valor da temperatura interna, Valor da temperatura ambiente, Valor da temperatura referência, Resistor/Ventoinha(%)\n")

    tabelaCsv = [datetime.now().strftime("%d-%m-%Y %H:%M:%S"), temperaturaInterna, temperaturaAmbiente, temperaturaReferencia, sinalControle]

    # O modo "a" permite adicionar conteúdo no final do arquivo, sem sobrescrever o conteúdo existente
    with open(arquivoGerado, mode="a") as arquivoCsv:
        escreverNoArquivo = csv.writer(arquivoCsv)
        escreverNoArquivo.writerow(tabelaCsv)