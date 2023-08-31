# FABRICA

import paho.mqtt.client as mqtt 
import time

from print_with_color import print_with_color as printwc

pecasNaFabrica = [5,5,5,5,5,5,5,5,5,5]

def on_connect(client, userdata, flags, return_code):

    if return_code == 0:
        printwc("Conectado.", color="purple")
        client.subscribe("fabrica")
        client.subscribe("fabricas")
        client.subscribe("estoque_fabrica")
        client.subscribe("fabrica_linha")
    else:
        printwc(f"Não foi possível conectar. Return code: {return_code}", color="purple")

def on_message(client, userdata, message):

    msg = str(message.payload.decode("utf-8"))
    printwc(f"Menssagem recebida: {msg}", color="blue")
    
    comando = msg.split("/")
    #printwc(comando)
    # if(comando[0] == "linha"):
    #     pecasPedidas = comando[2].split(",")
    #     pecas = []
    #     for i in range(len(pecasPedidas)):
    #         pecas.append(int(pecasPedidas[i]))
    #     #printwc(pecas)
    #     enviarPecas(comando[1], pecas)
    
    match comando[0]:

        case "linha":

            pecasPedidas = comando[2].split(",")
            pecas = []
            for i in range(len(pecasPedidas)):
                pecas.append(int(pecasPedidas[i]))
            #printwc(pecas)
            enviarPecas(comando[1], pecas)

        case "estoque":
            # printwc(comando[2], color="cyan")

            pedido = comando[4].split(";")

            # printwc(pedido, color="cyan")

            lista_produtos = []
            for pedido_produto in pedido:
                lista_produtos.append(pedido_produto.split(","))
            
            # printwc(lista_produtos, color="cyan")

            lista_produtos_int = []
            for pedido_produto in lista_produtos:
                lista_produtos_int.append([int(pedido_produto[0]), int(pedido_produto[1])])

            # printwc(lista_produtos_int, color="cyan")

            enviar_produtos_estoque(lista_produtos_int)
            enviar_pedido_linha(lista_produtos_int)
            

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
    #printwc(envio)

def pedirPecas(pecas):
    pedido = ""
    for i in range (len(pecas)):
        pedido = pedido + str(pecas[i])
        if(i < len(pecas) - 1):
            pedido = pedido + ","
    result = client.publish("fabricas", "fabrica/" + str(nfab) + "/" + pedido)
    #printwc(pedido)

def enviar_produtos_estoque(lista_produtos):

    pedido = ""
    for produto, quantidade in lista_produtos:
        pedido += str(produto) + "," + str(quantidade) + ";"
    pedido = pedido[:-1]

    printwc(pedido, color="cyan")

    result = client.publish("estoque_fabrica", "fabrica/" + str(nfab) + "/estoque/1/" + pedido)

def enviar_pedido_linha(lista_produtos):

    pedido = ""
    for produto, quantidade in lista_produtos:
        pedido += str(produto) + "," + str(quantidade) + ";"
    pedido = pedido[:-1]

    printwc(pedido, color="cyan")

    result = client.publish("fabrica_linha", "fabrica/" + str(nfab) + "/linha/1/pedido_produto" + pedido)

broker_hostname ="localhost"
port = 1883

nfab = input("Escreva o numero da fabrica")
client = mqtt.Client("fabrica" + nfab)
client.username_pw_set(username="kenjiueno", password="123456") # uncomment if you use password auth
client.on_connect=on_connect
client.on_message=on_message

client.connect(broker_hostname, port) 
client.loop_start()

num_linhas = 8

do = True

while(do):
    time.sleep(1)