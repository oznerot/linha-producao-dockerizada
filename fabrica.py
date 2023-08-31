#FABRICA

import paho.mqtt.client as mqtt 
import time
import sys  

pecasNaFabrica = [5,5,5,5,5,5,5,5,5,5]

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
        client.subscribe("fabrica")
        client.subscribe("fabricas")
    else:
        print("could not connect, return code:", return_code)

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    print("Received message: " , msg)
    comando = msg.split("/")
    #print(comando)
    if(comando[0] == "linha"):
        pecasPedidas = comando[2].split(",")
        pecas = []
        for i in range(len(pecasPedidas)):
            pecas.append(int(pecasPedidas[i]))
        #print(pecas)
        enviarPecas(comando[1], pecas)

def enviarPecas(linha, pecas):
    pecas_faltantes = []
    contador = 0
    for i in range (len(pecas)):
        if(pecasNaFabrica[pecas[i]] == 0):
            contador += 1
            pecas_faltantes.append(pecas[i])
    if(contador == 0):
        for i in range (len(pecas)):
            pecasNaFabrica[pecas[i]] -= 1
        enviaPecas(linha, pecas)
    else:
        pedirPecas(pecas)

def enviaPecas(linha, pecas):
    envio = ""
    for i in range (len(pecas)):
        envio = envio + str(pecas[i])
        if(i < len(pecas) - 1):
            envio = envio + ","
    result = client.publish("fabrica", "fabrica/" + str(linha) + "/" + envio)
    #print(envio)

def pedirPecas(pecas):
    pedido = ""
    for i in range (len(pecas)):
        pedido = pedido + str(pecas[i])
        if(i < len(pecas) - 1):
            pedido = pedido + ","
    result = client.publish("fabricas", "fabrica/" + str(nfab) + "/" + pedido)
    #print(pedido)

broker_hostname ="localhost"
port = 1883 
if len(sys.argv) != 2:
    print("Usage: python3 fabrica.py <fabrica_number>")
    sys.exit()
nfab = sys.argv[1]
client = mqtt.Client("fabrica" + nfab)
# client.username_pw_set(username="user_name", password="password") # uncomment if you use password auth
client.on_connect=on_connect
client.on_message=on_message

client.connect(broker_hostname, port) 
client.loop_start()

do = True

while(do):
    time.sleep(1)