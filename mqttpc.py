#!/bin/sh
# -*- coding: latin1 -*-
#
# verso 1.0  -- em desenvolvimento
#
# documentation 
# http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-2
# interfaces graficas python
# http://www.sourcecode.net.br/2011/11/criando-interfaces-graficas-com-glade-e.html
# http://www.devmedia.com.br/tkinter-interfaces-graficas-em-python/33956
# https://medium.com/@erikdkennedy/7-rules-for-creating-gorgeous-ui-part-1-559d4e805cda

import paho.mqtt.client as mqtt
import sys
from time import sleep
from myTimerClass import IntervalRunner
#from myTimerClass import TimerClass

#definicoes: 
#Broker = "iot.eclipse.org"
#Broker = "m2m.eclipse.org"
#Broker = "mqtt.de.vix.br"
Broker = "broker.hivemq.com"
PortaBroker = 1883
KeepAliveBroker = 20
TopicoSubscribe = "topicoSubscribe" 
#TpSensor = "topicoSensor" 
TpPeriodico = "contador"
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
 
def on_disconnect(client, userdata, rc):
    global monitorPeriodico

    if rc != 0:
        print("Unexpected disconnection.")
        client = startMqttClient()
        monitorPeriodico.stop()
        monitorPeriodico = IntervalRunner(30, publicacaoPeriodica, client)
        monitorPeriodico.start()
 
def publicacaoPeriodica(client):
    global contador
    
    contador = contador + 1
    msg = 'Contador = ' + str(contador)
    print ('Publica no topico: ' + msg)
    client.publish(TpPeriodico, msg, 0, False)
    if ((contador % 2) == 0):
      print "sai do loop"
      client.loop_stop()
      #client = mqtt.Client()

def startMqttClient():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
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

    return client    


#programa principal:
try:
     
 #    interval_monitor.join() # Opcional, claro  
        print("[STATUS] Inicializando MQTT...")
        #inicializa MQTT:

        client = startMqttClient()
        '''
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
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
        '''
   #incializar timer
        monitorPeriodico = IntervalRunner(30, publicacaoPeriodica, client)
        monitorPeriodico.start()

#        client.loop_forever(1,1,True)
        client.loop_start()
except KeyboardInterrupt:
        print "\nCtrl+C pressionado, encerrando aplicacao e saindo..."
        sys.exit(0)
