# FABRICA

import argparse
import paho.mqtt.client as mqtt 
import time

from print_with_color import print_with_color as printwc

pecasNaFabrica = [5,5,5,5,5,5,5,5,5,5]

class Fabrica:

    def __init__(self, id_fabrica=2, num_linhas=8, id_almoxarifado=1):

        self.id_fabrica = id_fabrica
        self.num_linhas = num_linhas
        self.id_almoxarifado = id_almoxarifado
    
    def enviar_pedido_pecas(self, lista_pedido_pecas, id_linha):

        pedido = ""
        for peca, quantidade in enumerate(lista_pedido_pecas):
            pedido += str(peca) + "," + str(quantidade) + ";"
        pedido = pedido[:-1]

        printwc(pedido, color="cyan")

        # result = client.publish("fabrica_linha", "fabrica/" + str(self.id_fabrica) + "/linha/" + str(id_linha) + "/pedido_pecas/" + pedido)
        result = client.publish("fabrica_almoxarifado",
                                "fabrica/" + str(self.id_fabrica) +             \
                                "/almoxarifado/" + str(self.id_almoxarifado) +  \
                                "/linha/" + str(id_linha) + "/" + pedido)

    def receber_pedido_pecas(self, lista_pedido_pecas, id_linha):
        
        pedido = ""
        for peca, quantidade in enumerate(lista_pedido_pecas):
            pedido += str(peca) + "," + str(quantidade) + ";"
        pedido = pedido[:-1]

        printwc(pedido, color="cyan")

        # result = client.publish("fabrica_linha", "fabrica/" + str(self.id_fabrica) + "/linha/" + str(id_linha) + "/pedido_pecas/" + pedido)
        result = client.publish("fabrica_linha",
                                "fabrica/" + str(self.id_fabrica) +     \
                                "/linha/" + str(id_linha) +        \
                                "/pedido_pecas/" + pedido)

    def enviar_produtos_estoque(self, lista_produtos):
        pedido = ""
        for produto, quantidade in enumerate(lista_produtos):
            pedido += str(produto) + "," + str(quantidade) + ";"
        pedido = pedido[:-1]

        # printwc(pedido, color="cyan")

        result = client.publish("estoque_fabrica", "fabrica/" + str(id_fabrica) + "/estoque/1/" + pedido)

    def enviar_pedido_linha(self, lista_produtos):
        pedido = ""
        for produto, quantidade in enumerate(lista_produtos):
            pedido += str(produto) + "," + str(quantidade) + ";"
        pedido = pedido[:-1]

        # printwc(pedido, color="cyan")

        result = client.publish("fabrica_linha", "fabrica/" + str(id_fabrica) + "/linha/1/pedido_produto/" + pedido)

    
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

    def handler(self, acao, lista, id_linha=None):

        lista = self.converter_lista(lista)

        match acao:
            case "enviar pedido para linha":
                self.enviar_pedido_linha(lista)
            case "enviar pedido de peças para almoxarifado":
                self.enviar_pedido_pecas(lista, id_linha)
            case "receber pedido do almoxarifado":
                self.receber_pedido_pecas(lista, id_linha)
            case "enviar pedido de produtos para o estoque":
                self.enviar_produtos_estoque(lista)

def on_connect(client, userdata, flags, return_code):

    if return_code == 0:
        printwc("Fábrica conectada.", color="purple")
        # client.subscribe("fabrica")
        # client.subscribe("fabricas")
        client.subscribe("estoque_fabrica")
        client.subscribe("fabrica_linha")
        client.subscribe("fabrica_almoxarifado")

    else:
        printwc(f"Não foi possível conectar a fábrica. Return code: {return_code}", color="purple")

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

        case "linha" if((comando[3] == id_fabrica) & (comando[4] == "pedido_pecas")):

            # pecasPedidas = comando[5].split(",")
            # pecas = []
            # for i in range(len(pecasPedidas)):
            #     pecas.append(int(pecasPedidas[i]))
            # #printwc(pecas)
            # enviarPecas(comando[1], pecas)

            fabrica.handler(acao="enviar pedido de peças para almoxarifado", lista=comando[5], id_linha=comando[1])
        
        case "linha" if((comando[3] == id_fabrica) & (comando[4] == "pedido_produtos")):

            lista = fabrica.converter_lista(comando[5])

            # printwc(lista, color="cyan")

            # fabrica.enviar_produtos_estoque(lista)

            fabrica.handler(acao="enviar pedido de produtos para o estoque", lista=comando[5])

        case "estoque" if(comando[3] == id_fabrica):
            # printwc(comando[2], color="cyan")

            pedido = comando[4].split(";")

            # printwc(pedido, color="cyan")

            lista_produtos = []
            for pedido_produto in pedido:
                lista_produtos.append(pedido_produto.split(","))
            
            # printwc(lista_produtos, color="cyan")

            lista_produtos_int = [0] * 5
            for produto, quantidade in lista_produtos:
                lista_produtos_int[int(produto)] = int(quantidade)

            # printwc(lista_produtos_int, color="cyan")

            # enviar_produtos_estoque(lista_produtos_int)
            # enviar_pedido_linha(lista_produtos_int)

            fabrica.handler(acao="enviar pedido para linha", lista=comando[4])
        
        case "almoxarifado" if(comando[3] == fabrica.id_fabrica):

            fabrica.handler(acao="receber pedido do almoxarifado", lista=comando[6], id_linha=comando[5])
            

# def enviarPecas(linha, pecas):
#     pecas_faltantes = []
#     contador = 0
#     for i in range (len(pecas)):
#         if(pecasNaFabrica[pecas[i]] == 0):
#             contador += 1
#             pecas_faltantes.append(pecas[i])
#     if(contador == 0):
#         for i in range (len(pecas)):
#             pecasNaFabrica[pecas[i]] -= 1
#         enviar_pecas(linha, pecas)
#     else:
#         pedirPecas(pecas)

###############################################################

# def enviar_pecas(linha, pecas):
#     envio = ""
#     for i in range (len(pecas)):
#         envio = envio + str(pecas[i])
#         if(i < len(pecas) - 1):
#             envio = envio + ","
#     result = client.publish("fabrica_linha", "fabrica/" + str(id_fabrica) + "/linha/" + str(linha) + "/pedido_pecas/" + envio)
#     #printwc(envio)

# def pedirPecas(pecas):
#     pedido = ""
#     for i in range (len(pecas)):
#         pedido = pedido + str(pecas[i])
#         if(i < len(pecas) - 1):
#             pedido = pedido + ","
#     result = client.publish("fabricas", "fabrica/" + str(id_fabrica) + "/" + pedido)
#     #printwc(pedido)

# def enviar_produtos_estoque(lista_produtos):

#     pedido = ""
#     for produto, quantidade in enumerate(lista_produtos):
#         pedido += str(produto) + "," + str(quantidade) + ";"
#     pedido = pedido[:-1]

#     # printwc(pedido, color="cyan")

#     result = client.publish("estoque_fabrica", "fabrica/" + str(id_fabrica) + "/estoque/1/" + pedido)

# def enviar_pedido_linha(lista_produtos):

#     pedido = ""
#     for produto, quantidade in enumerate(lista_produtos):
#         pedido += str(produto) + "," + str(quantidade) + ";"
#     pedido = pedido[:-1]

#     # printwc(pedido, color="cyan")

#     result = client.publish("fabrica_linha", "fabrica/" + str(id_fabrica) + "/linha/1/pedido_produto/" + pedido)

parser = argparse.ArgumentParser(description='Argumentos para execução da fábrica.')

parser.add_argument('-f', '--id_fabrica', type=str, default="2",
                    help="Define o ID da fábrica")
parser.add_argument('-nl', '--num_linhas', type=int, default="8",
                    help="Define o número de linhas da fábrica")

args = parser.parse_args()

broker_hostname ="localhost"
port = 1883

# id_fabrica = input("Escreva o numero da fabrica: ")
id_fabrica = args.id_fabrica
client = mqtt.Client("fabrica" + id_fabrica)
client.username_pw_set(username="kenjiueno", password="123456") # uncomment if you use password auth
client.on_connect=on_connect
client.on_message=on_message

client.connect(broker_hostname, port) 
client.loop_start()

num_linhas = 8

do = True

fabrica = Fabrica(id_fabrica=id_fabrica, num_linhas=8)

while(True):
    if(client.is_connected()):
        time.sleep(1)