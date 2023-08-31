# FORNECEDOR DE PEÇAS

import argparse
import random
import paho.mqtt.client as mqtt 
import time

from print_with_color import print_with_color as printwc

class Fornecedor:

    def __init__(self, id_fornecedor=1):

        self.id_fornecedor = id_fornecedor
        # self.estoque_pecas = infinito

    def enviar_pecas(self, lista_pecas, id_almoxarifado, id_fabrica=None, id_linha=None, pedido_proprio=False):
        
        # printwc(lista_pecas, color="cyan")
        printwc("Enviando peças para o almoxarifado.", color="yellow")

        lista_pecas = self.converter_lista(lista_pecas)

        pedido_pecas = ""
        for peca, quantidade in enumerate(lista_pecas):
            pedido_pecas += str(peca) + "," + str(quantidade) + ";"
        
        pedido_pecas = pedido_pecas[:-1]
        # printwc(pedido_pecas, color="cyan")

        if(pedido_proprio):            
            result = client.publish("almoxarifado_fornecedor",
                                    "fornecedor/" + str(self.id_fornecedor) +   \
                                    "/almoxarifado/" + str(id_almoxarifado) +   \
                                    "/auto/" + pedido_pecas)
        else:
            result = client.publish("almoxarifado_fornecedor",
                                    "fornecedor/" + str(self.id_fornecedor) +   \
                                    "/almoxarifado/" + str(id_almoxarifado) +   \
                                    "/fabrica/" + str(id_fabrica) +   \
                                    "/linha/" + str(id_linha) +   \
                                    "/" + pedido_pecas)


    def converter_lista(self, lista1):

        # printwc(lista1, color="cyan")
        
        lista2 = lista1.split(";")

        lista3 = []
        for pedido_produto in lista2:
            lista3.append(pedido_produto.split(","))
        
        lista4 = [0] * len(lista3)
        for indice, quantidade in lista3:
            lista4[int(indice)] = int(quantidade)
        
        return lista4

def on_connect(client, userdata, flags, return_code):

    if return_code == 0:
        printwc("Fornecdor conectado.", color="purple")
        client.subscribe("almoxarifado_fornecedor")
    else:
        printwc(f"Não foi possível conectar o fornecedor. Return code: {return_code}", color="purple")

def on_message(client, userdata, message):

    msg = str(message.payload.decode("utf-8"))
    # printwc(f"Menssagem recebida: {msg}", color="blue")

    comando = msg.split("/")

    match comando[0]:
        case "almoxarifado" if((comando[3] == fornecedor.id_fornecedor) & (comando[4] == "fabrica")):
            fornecedor.enviar_pecas(lista_pecas=comando[8], id_almoxarifado=comando[1],
                                    id_fabrica=comando[5], id_linha=comando[7])
        case "almoxarifado" if((comando[3] == fornecedor.id_fornecedor) & (comando[4] == "auto")):
            fornecedor.enviar_pecas(lista_pecas=comando[5], id_almoxarifado=comando[1])
            
parser = argparse.ArgumentParser(description='Argumentos para execução do fornecedor.')

parser.add_argument('-i', '--id_fornecedor', type=str, default="1",
                    help="Define o ID do fornecedor")

args = parser.parse_args()

broker_hostname ="localhost"
port = 1883

# id_fornecedor = input("Escreva o numero do fornecedor: ")
id_fornecedor = args.id_fornecedor
client = mqtt.Client("fornecedor" + id_fornecedor)
client.username_pw_set(username="kenjiueno", password="123456") # uncomment if you use password auth
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_hostname, port) 
client.loop_start()

fornecedor = Fornecedor(id_fornecedor=id_fornecedor)

while(True):
    time.sleep(1)