#!/bin/sh
# -*- coding: latin1 -*-
#
# verso 1.0  -- em desenvolvimento
#
# documentation 
# https://www.embarcados.com.br/raspberry-pi-3-na-iot-mqtt-e-python/
# https://www.eclipse.org/paho/clients/python/docs/ 
# http://www.steves-internet-guide.com/into-mqtt-python-client/
# https://www.eclipse.org/paho/clients/python/docs/#publishing
# https://www.eclipse.org/paho/clients/python/
# http://raspberry.io/projects/view/reading-and-writing-from-gpio-ports-from-python/
# https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/
# https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
# https://wiki.python.org.br/ExecutandoEmIntervalos
# https://www.infoq.com/articles/practical-mqtt-with-paho
# https://www.raspberrypi.org/documentation/hardware/raspberrypi/schematics/Raspberry-Pi-B-Plus-V1.2-Schematics.pdf
# https://www.raspberrypi.org/documentation/hardware/raspberrypi/schematics/README.md
# https://www.vivaolinux.com.br/dica/Colocando-script-na-inicializacao-do-Linux-(Ubuntu-Debian)
# http://www.hardware.com.br/comunidade/v-t/1417634/
# http://cadernodelaboratorio.com.br/2015/06/10/inicializando-um-programa-automaticamente-no-raspberrypi/
# http://www.newtoncbraga.com.br/index.php/como-funciona/1796-art265
# http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-2
# interfaces grÃÂÃÂÃÂÃÂ¡ficas python
# http://www.sourcecode.net.br/2011/11/criando-interfaces-graficas-com-glade-e.html
# http://www.devmedia.com.br/tkinter-interfaces-graficas-em-python/33956
# https://medium.com/@erikdkennedy/7-rules-for-creating-gorgeous-ui-part-1-559d4e805cda

import paho.mqtt.client as mqtt
import sys
from time import sleep
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.")


from myTimerClass import IntervalRunner
from myTimerClass import TimerClass

#definicoes: 
#Broker = "iot.eclipse.org"
Broker = "m2m.eclipse.org"
PortaBroker = 1883
KeepAliveBroker = 60
TopicoSubscribe = "MoxuaraEstoque" 
TpSensor = "sensorPortaEstoque" 
TpPeriodico = "tpPeriodico"
contador = 0  # contador a ser acessado globalmente
client = None
sirene = None
 
#Callback - conexao ao broker realizada
def on_connect(client, userdata, flags, rc):
    print("[STATUS] Conectado ao Broker. Resultado de conexao: "+str(rc))
    client.subscribe(TopicoSubscribe)    #faz subscribe automatico no topico
 
#Callback - mensagem recebida do broker
def on_message(client, userdata, msg):
    MensagemRecebida = str(msg.payload)
    print("[MSG RECEBIDA] Topico: "+msg.topic+" / Mensagem: "+MensagemRecebida)
 
 
def sensorPorta(channel):
    print 'Sensor da Porta Indica:'
    if GPIO.input(4) == False: 
        msg = '--> Porta Aberta'
        sirene = TimerClass(5,sireneMetodo, client)
        sirene.start()
    else:
        msg = '--> Porta Fechada'
        sireneMetodo(client)
        
    print msg
    client.publish(TpSensor, msg, 0, False)  
   
 
def publicacaoPeriodica(client):
    global contador
    
    print 'Publica no topico: tpPeriodico'
    contador = contador + 1
    msg = 'Contador = ' + str(contador)
    client.publish(TpPeriodico, msg, 0, False)
    if ((contador % 2) == 0):
      print "sai do loop"
      client.loop_stop()

def sireneMetodo(client):
    if GPIO.input(4) == False:  #porta aberta
        msg = 'Sirene Acionada' 
      # adaptacao notebook
      #  GPIO.output(25, GPIO.HIGH)         # ligar set GPIO24 to 1/GPIO.HIGH/True
    else:
        msg = 'Sirene Desacionada'
     # adaptacao notebook
     #   GPIO.output(25, GPIO.LOW)         # desligar set GPIO24 to 1/GPIO.HIGH/True  
   
    print msg
    client.publish(TpSensor, msg, 0, False)  
##   if GPIO.input(25):
##        print 'baixo'
##        GPIO.output(25, GPIO.LOW)         # set GPIO24 to 1/GPIO.HIGH/True  
##        
##    else:
##        print 'alto'
##        GPIO.output(25, GPIO.HIGH)         # set GPIO24 to 1/GPIO.HIGH/True  
##        
## publish(topic, payload=None, qos=0, retain=False)

#programa principal:
try:
     
 #    interval_monitor.join() # Opcional, claro  
        print("[STATUS] Inicializando MQTT...")
        #inicializa MQTT:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        rc = -1
        while rc == -1: 
          try:    
            print "conectando: " 
            client.connect(Broker, PortaBroker, KeepAliveBroker)
            rc = 0
            print "retorno: "
            print rc
          except:
            print "falha de conexao: "
            print rc
            sleep (10)

   #incializar timer
        monitorPeriodico = IntervalRunner(30, publicacaoPeriodica, client)
        monitorPeriodico.start()

#iniciar gpio do raspiberry
        GPIO.setmode(GPIO.BCM) #ou BOARD
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(25, GPIO.OUT, initial=GPIO.LOW)
        GPIO.add_event_detect(4, GPIO.BOTH, callback=sensorPorta, bouncetime=500)
        #GPIO.add_event_callback(4, sensorPorta)
        #GPIO.add_event_detect(channel, GPIO.RISING, callback=my_callback, bouncetime=200)
   
#        client.loop_forever(1,1,True)
        client.loop_start()
except KeyboardInterrupt:
        print "\nCtrl+C pressionado, encerrando aplicacao e saindo..."
        sys.exit(0)
