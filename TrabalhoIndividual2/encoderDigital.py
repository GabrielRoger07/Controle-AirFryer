"""
import RPi.GPIO as GPIO
import time

Setup PINS
SW = 23
DT = 24
CLOCK = 25

Setup GPIO
GPIO.setmode(GPIO.BCM)

GPIO.setup(CLOCK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

Estados iniciais
estadoClockInit = GPIO.input(CLOCK)
estadoDTInit = GPIO.input(DT)
estadoSWInit = GPIO.input(SW)

contador = 0

def treatSW(pin):
    print('Botao Clicado!!')

def treatCLOCK(pin):
    global contador
    estadoClock = GPIO.input(CLOCK)
    estadoDT = GPIO.input(DT)

    if estadoClock == 0 and estadoDT == 1:
        contador += 1
        print ("Sentido Anti-horario: " + str(contador))

def treatDT(pin):
    global contador

    estadoClock = GPIO.input(CLOCK)
    estadoDT = GPIO.input(DT)

    if estadoClock == 1 and estadoDT == 0:
        contador -= 1
        print ("Sentido horario: " + str(contador))


print ("CLOCK INICIAL:", estadoClockInit)
print ("DT INICIAL:", estadoDTInit)
print ("SW INICIAL:", estadoSWInit)
print ("=========================================")
 
#set up the interrupts
GPIO.add_event_detect(CLOCK, GPIO.FALLING, callback=treatCLOCK, bouncetime=300)
GPIO.add_event_detect(DT, GPIO.FALLING, callback=treatDT, bouncetime=300)
GPIO.add_event_detect(SW, GPIO.FALLING, callback=treatSW, bouncetime=300)
 
while True:
    time.sleep(1)

GPIO.cleanup()
"""