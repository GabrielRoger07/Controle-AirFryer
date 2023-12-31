# Trabalho 2 - 2023/1

Trabalho 2 da disciplina de Fundamentos de Sistemas Embarcados (2023/1)

## 1. Objetivos


AirFryer Eletrolux | AirFryer Philips-Walita  |  AirFryer Philco
:-------------------------:|:-------------------------:|:-------------------------:
<img src="https://electrolux.vtexassets.com/arquivos/ids/219311-1200-1200?v=637849516015500000&width=1200&height=1200&aspect=true" data-canonical-src="https://electrolux.vtexassets.com/arquivos/ids/219311-1200-1200?v=637849516015500000&width=1200&height=1200&aspect=true" width="200"/> | <img src="https://polishop.vtexassets.com/arquivos/ids/680556-1200-1200?v=637799494321430000&width=1200&height=1200&aspect=true" data-canonical-src="https://polishop.vtexassets.com/arquivos/ids/680556-1200-1200?v=637799494321430000&width=1200&height=1200&aspect=true" width="200"/> | <img src="https://i.zst.com.br/thumbs/12/c/39/1942768547.jpg" data-canonical-src="https://i.zst.com.br/thumbs/12/c/39/1942768547.jpg" width="200"/>

O trabalho envolve o desenovlimento do software que efetua o controle completo de um forno AirFyer incluindo ligar/desligar o equipamento, controlar a temperatura, temporização e diferentes modos de alimentos. Especificamente a temperatura do forno é controlada à partir de dois elementos *atuadores*: um resistor de potência de 15 Watts utilizado para aquecer o forno e uma ventoinha que puxa o ar externo (temperatura ambiente) para reduzir a temperatura do sistema. 

Os comandos do usuário do sistema para definir a temperatura desejada serão controlados de três maneiras:
1. Através de botões físicos (encoder rotatório);
2. Botões digitais via Dashboard (UART);
3. Seguindo os tempo e temperaturas pré-definidas para cada tipo de alimento.

**Botões de Entrada**
- Liga/Desliga  
- Inicia/Cancela
- Temperatura +/- (A cada 5 ˚C)  
- Tempo +/- (Minutos)  
- Dial (Para Temperatura/Tempo)

## 2. Componentes do Sistema

O sistema como um todo é composto por:
1. Forno (AirFryer) controlado com o resistor de potência e ventoinha;
2. 01 Sensor DS18B20 (1-Wire) para a medição da temperatura interna (TI) do sistema;
3. 01 Sensor BMP280 (I2C) para a medição da temperatura externa (TE);
4. 01 módulo Display LCD 16x2 com circuito I2C integrado (Controlador HD44780);
5. 01 Conversor lógico bidirecional (3.3V / 5V);
6. 01 Driver de potência para acionamento de duas cargas;
6. 01 ESP32;
7. 01 Painel de Botões (Liga/Desliga, Inicia/Cancela, Temperatura +, Temperatura -, Tempo +, Tempo -);
8. 01 Raspberry Pi 4;

![Figura](/figuras/Figura_1_Trabalho_2_AirFryer.png)

## 3. Conexões entre os módulos do sistema

1. O sensor de temperatura BMP280 está ligado ao barramento I2C e utiliza o endereço `0x76`;
2. O módulo de display LCD está conectado ao barramento I2C utilizando o endereço `0x27`;
3. O Encoder Digital possui 3 pinos (`clk` GPIO 16, `dt` GPIO 20 e `sw` GPIO 21). O pino `sw` corresponde ao botão que será usado para selecionar a variável a ser ajustada no **modo manual** sendo ela a **temperatura** ou o **tempo**. Os pinos `clk` e `dt` indicam a rotação do encoder. 
4. O resistor de potência e a ventoinha estão ambos ligados às portas GPIO e são acionados através do circuito de potência;  
    3.1. Resistor: GPIO 23 ou Pino 16 (Board)  
    3.2. Ventoinha: GPIO 24 ou Pino 18 (Board)  
5. A ESP32 está conectada à placa Raspberry Pi via UART (Protocolo MODBUS-RTU);
6. Os botões estão ligados à GPIO da ESP32 e os comandos são transmitidos à Raspberry Pi via UART;
7. Os comandos de acionamento (alternativamente) virão do Dashboard (Thingsboard) via UART através da ESP32;
8. O sensor de temperatura DS18B20 para medição do ambiente controlado está ligado à ESP32 na porta GPIO 4 via protocolo 1-Wire;

## 4. Controle PID

A abordagem de controle de temperatura a ser utilizado é o controle PID (Proporcional Integral Derivativo). O PID é um dos tipos mais simples de algoritmos de controle que proporciona um bom desempenho para uma grande variedade de aplicações.

O conceito fundamental desse tipo de controlador se baseia em monitorar uma variável de um processo (neste caso a temperatura interna) e medir a diferença entre seu valor atual (TI - Temperatura Interna) a uma valor de referência (TR - Temperatura de Referência) desejado. A partir dessa medida de **Erro = TR - TI**, toma-se uma ação de correção para que o sistema alcançe o valor desejado. A figura abaixo demonstra uma visão geral da estratégia de controle.

![Sistema de Controle](https://upload.wikimedia.org/wikipedia/commons/2/24/Feedback_loop_with_descriptions.svg)

O controle PID une três tipos de ações sobre a variável de controle para minimizar o erro do sistema até que o mesmo alcançe a referência desejada. No caso deste sistema, nossa variável monitorada é a TI - Temparatura Interna e o seu controle é efetuado através do acionamento da **Resistência (R)** ou da **Ventoinha (V)** e nosso **Erro** é a diferença entre a temperatura de referência e a temperatura interna do sistema (Erro = TR - TI).

Detalhando as 3 ações do PID temos:
- **Controle Proporcional (P)**: ajusta a variável de controle de forma proporcional ao erro, ou seja, quanto maior o erro, maior a intensidade de acionamento do resistor (0 a 100%). Esse ajuste é feito pela variável ***Kp***.
- **Controle Integral (PI)**: ajusta a variável de controle baseando-se no tempo em que o erro acontece, acumulando este erro (integral). Esse ajuste é feito pela variável ***Ki***.
- **Controle Derivativo (PD)**: ajusta a variável de controle tendo como base a taxa de variação do erro ou a velocidade com a qual o sistema está variando o erro. Esse ajuste é feito pela variável ***Kd***.

A figura abaixo mostra as equações envolvidas no cálculo do PID.

![PID](https://upload.wikimedia.org/wikipedia/commons/4/43/PID_en.svg)

O ajustes de cada constante do PID (Kp, Ki e Kd) tem efeitos distintos no controle do sistema conforme pode ser visto na figura  abaixo.

![PID - Variáveis Kp, Ki, Kd](https://upload.wikimedia.org/wikipedia/commons/3/33/PID_Compensation_Animated.gif)

## 5. Requisitos

Os sistema de controle possui os seguintes requisitos:
1. O código deve ser desenvolvido em C/C++ ou Python;
2. Na implementação do software, não podem haver loops infinitos que ocupem 100% da CPU;
3. O sistema deve implementar o controle de temperatura utilizando o controle PID atuando sobre o Resistor e a Ventoinha;
4. Ao ser acionado, o aquecimento deve primeiro atingir a temperatura desejada para depois ligar o timer (tempo programado) com a contagem regressiva até finalizar e depois retornar o sistema à temperatura ambiente;
5. Haverão dois modos de controle da temperatura:  
   1. **Manual**: onde a temperatura e o tempo serão inseridos pelo usuário (Via Dashboard ou pelo Encoder Digital);
   2. **Pré-programado**: onde o usuário pressiona o botão de menu e escolhe uma pré-programação correspondendo a um tipo de alimento.  
6. No modo manual, o programa deve consultar o valor de temperatura através da comunicação UART com a ESP32 a cada 500 ms e efetuar a leitura constante do Encoder Digital para permitir ao usuário um ajuste de temperatura durante a operação;
7.  **Display LCD (16x2)**: O sistema deve apresentar na tela LCD seu estado atual. Os estados são:
   1. **Desligado**: apagar o Display;
   2. **Ligado**: Mostrar a configuração atual (Menu pré-definido ou acionamento manual);  
   3. **Funcionando**: mostrar a temperatura atual, a desejada e o tempo restante.  
   4. O display deve ser atualizado a cada 1 segundo;  
8.  O programa deve tratar a interrupção do teclado (Ctrl + C = sinal **SIGINT**) encerrando todas as comunicações com periféricos (UART / I2C / GPIO) e desligar os atuadores (Resistor e Ventoinha);
9. O código em C/C++ deve possuir Makefile para compilação. Em Python deverão haver instruções de como executar;
10. O sistema deve conter em seu README as instruções de compilação/execução e uso, bem como gráficos* com o resultado de pelo menos 3 testes realizados no equipamento.
11. O programa deve gerar um log em arquivo CSV das seguintes informações a cada 1 segundo com os seguintes valores: (Data e hora, temperatura interna, temperatura ambiente, temperatura definida pelo usuário, valor de acionamento dos atuadores (Resistor e Venoinha em valor percentual).

\* Serão necessários dois gráficos para cada experimento. Um deles plotando as temperaturas (Ambiente, Interna e Referência (Potenciômetro)) e outro gráfico com o valor do acionamento dos atuadores (Resistor / Ventoinha) em valor percentual entre -100% e 100%.

## 6. Comunicação UART com a ESP32

A comunicação com a ESP32 deve seguir o mesmo protocolo MODBUS utilizado no [Exercício UART-MODBUS](https://gitlab.com/fse_fga/exercicios/exercicio-2-uart-modbus).
 
A ESP32 será responsável por:
1. Efetuar a medição da temperatura interna (Sensor DS18B20);
2. Realizar a leitura dos botões de acionamento para controle da AirFryer;
3. Iniciar e Desligar o sistema de controle;
4. Atualizar informações sobre as temperaturas e tempo;
5. Enviar o sinal de controle no dashboard (ThingsBoard).

Para acessar as informações via UART envie mensagens em formato MODBUS com o seguinte conteúdo:

1. Código do Dispositivo no barramento: 0x01 (Endereço da ESP32);  
2. Leitura do Valor de Temperatura Interna (TI): Código 0x23, Sub-código: 0xC1 + 4 últimos dígitos da matrícula. O retorno será o valor em Float (4 bytes) da temperatura interna do sistema com o pacote no formato MODBUS;
3. Leitura da temperatura de referência - TR (Potenciômetro): Código 0x23, Sub-código: 0xC2 + 4 últimos dígitos da matrícula. O retorno será o valor em Float (4 bytes) da temperatura de referência definida pelo usuário com o pacote no formato MODBUS;
4. Envio do sinal de controle (Resistor / Ventoinha): Código 0x16,  Sub-código: 0xD1 + 4 últimos dígitos da matrícula, Valor em Int (4 bytes).
5. Envio do sinal de referência nos casos em que o sistema esteja sendo controlado ou pelo terminal ou pela curva de referência: Código 0x16,  Sub-código: 0xD2 + 4 últimos dígitos da matrícula, Valor em Float (4 bytes).
6. Leitura dos Comandos de usuário: Código 0x23,  Sub-código: 0xC3;
7. Envio do estado interno do sistema em resposta aos comandos de usuário:
   1. Estado (Ligado / Desligado): Código 0x16,  Sub-código: 0xD3 + byte;
   2. Modo de Controle (Potenciômetro = 0 / Referência = 1): Código 0x16,  Sub-código: 0xD4 + byte;

<p style="text-align: center;">Tabela 1 - Códigos do Protocolo de Comunicação</p>

| Endereço da ESP32 | Código |	Sub-código + Matricula | Comando de Solicitação de Dados |	Mensagem de Retorno |
|:-:|:-:|:-:|:--|:--|
| **0x01** | **0x23** | **0xC1** N N N N |	Solicita Temperatura Interna  | 0x00 0x23 0xC1 + float (4 bytes) |
| **0x01** | **0x23** | **0xC2** N N N N |	Solicita Temperatura de Referência	| 0x00 0x23 0xC2 + float (4 bytes) |
| **0x01** | **0x23** | **0xC3** N N N N |	Lê comandos do usuário  | 0x00 0x23 0xC3 + int (4 bytes de comando) | 
| **0x01** | **0x16** | **0xD1** N N N N |	Envia sinal de controle Int (4 bytes) |  |
| **0x01** | **0x16** | **0xD2** N N N N |	Envia sinal de Referência Float (4 bytes) |  |
| **0x01** | **0x16** | **0xD3** N N N N |	Envia Estado do Sistema (Ligado = 1 / Desligado = 0) uint_8 (1  byte) | 0x00 0x16 0xD3 + int (4  bytes) + CRC | 
| **0x01** | **0x16** | **0xD4** N N N N |	Modo de Controle da Temperatura de referência (Dashboard (Manual) = 0 / Automático = 1) uint_8 (1  byte) | 0x00 0x16 0xD4 + int (4  bytes) + CRC | 
| **0x01** | **0x16** | **0xD5** N N N N |	Envia Estado de Funcionamento (Funcionando = 1 / Parado = 0) uint_8 (1  byte) | 0x00 0x16 0xD5 + int (4  bytes) + CRC | 
| **0x01** | **0x16** | **0xD6** N N N N |	Envia Temperatura Ambiente (Float)) (4 bytes) |  |  
| **0x01** | **0x16** | **0xD7** N N N N |	Envia Contador de Tempo (usado no modo de pré-programação) (4 bytes) |  |  
| **0x01** | **0x16** | **0xD8** N N N N |	Envia String do Display LCD para o Dashboard (1 byte: tamanho da string + N bytes da String) |  |  

Obs: todas as mensagens devem ser enviadas com o CRC e também recebidas verificando o CRC. Caso esta verificação não seja válida, a mensagem deverá ser descartada e uma nova solicitação deverá ser realizada.

<p style="text-align: left;">Tabela 2 - Comandos de Usuário via UART</p>

| Comando | Código |
|:--|:-:|
| **Liga** a AirFryer | 0x01 |
| **Desliga** a AirFryer | 0x02 |
| **Inicia** aquecimento | 0x03 |
| **Cancela** processo | 0x04 |
| **Tempo +** : adiciona 1 minuto ao timer | 0x05 |  
| **Tempo -** : adiciona 1 minuto ao timer | 0x06 |  
| **Menu** : aciona o modo de alimentos pré-programados | 0x07 |  

## 7. Parâmetros de PID

Para o uso do controle do PID, estão sendo sugeridos os seguintes valores para as constantes:
- **Kp** = 30.0
- **Ki** = 0.2
- **Kd** = 400.0

Porém, vocês estão livres para testar outros valores que sejam mais adequados.

### Acionamento do Resistor 

O **resistor** deve ser acionado utilizando a técnica de PWM (sugestão de uso da biblioteca WiringPi / SoftPWM). A intensidade de acionamento do resistor por variar entre 0 e 100%.

### Acionamento da Ventoinha

A **venotinha** também deve ser acionada utilizando a técnica de PWM. Porém, há um limite inferior de 40% de intensidade para seu acionamento pelas características do motor elétrico. Ou seja, caso o valor de saída do PID esteja entre 0 e -40%, a ventoinha deverá ser acionada com 40% de sua capacidade.

Observa-se ainda que a saída negativa só indica que o atuador a ser acionado deve ser a ventoinha e não o resistor e o valor de PWM a ser definido deve ser positivo, invertendo o sinal.

## 8. Referências

[Controle Liga/Desliga - Wikipedia](https://pt.wikipedia.org/wiki/Controle_liga-desliga)  
[Controle PID - Wikipedia](https://pt.wikipedia.org/wiki/Controlador_proporcional_integral_derivativo)  
[Driver da Bosh para o sensor BMP280](https://github.com/BoschSensortec/BMP2-Sensor-API/)  
[Biblioteca BCM2835 - GPIO](http://www.airspayce.com/mikem/bcm2835/)  
[Controle do LCD 16x2 em C](http://www.bristolwatch.com/rpi/i2clcd.htm)  
[Biblioteca WiringPi GPIO](http://wiringpi.com)  
[PWM via WiringPi](https://www.electronicwings.com/raspberry-pi/raspberry-pi-pwm-generation-using-python-and-c)

## 9. Gráficos
    
### 9.1. Modo Dashboard: Gráfico com as 3 temperaturas (interna, referência e ambiente) e gráfico com valor do acionamento dos atuadores    
<img src="/figuras/graficosModoDashboard.jpeg"
width=700px>
    
### 9.2. Modo Terminal Manual: Gráfico com as 3 temperaturas (interna, referência e ambiente) e gráfico com valor do acionamento dos atuadores  
![Gráficos Modo Terminal Manual](/figuras/graficosModoTerminalManual.jpeg)
    
### 9.3. Modo Terminal Automático: Gráfico com as 3 temperaturas (interna, referência e ambiente) e gráfico com valor do acionamento dos atuadores  
![Gráficos Modo Terminal Automático](/figuras/graficosModoTerminalAutomatico.png)
