# ALMOXARIFADO DE PEÇAS

import argparse
import random
import paho.mqtt.client as mqtt 
import time

from print_with_color import print_with_color as printwc

class Almoxarifado:

    def __init__(self, id_almoxarifado, id_fornecedor=1, limiar_estoque_pecas=20):

        self.id_almoxarifado = id_almoxarifado
        self.estoque_pecas = [1] * 100
        self.id_fornecedor = id_fornecedor
        self.limiar_estoque_pecas = limiar_estoque_pecas
        self.status_estoque_pecas = "VERMELHO"

    def montar_pedido_pecas(self, lista_pedido_pecas, id_fabrica, id_linha):
        
        # lista_pedido_pecas = self.converter_lista(lista_pedido_pecas)

        pedido_completo = True
        pecas_consumidas = [0] * 100
        pecas_faltantes = [0] * 100

        for peca, quantidade in enumerate(lista_pedido_pecas):
            if(self.estoque_pecas[peca] >= quantidade):
                pecas_consumidas[peca] = quantidade
            else:
                pedido_completo = False
                pecas_faltantes[peca] = quantidade - self.estoque_pecas[peca]
    
        if(pedido_completo):
            for peca, quantidade in enumerate(pecas_consumidas):
                self.estoque_pecas[peca] -= quantidade
            self.enviar_pedido_pecas(lista_pedido_pecas, id_fabrica, id_linha)
        else:
            self.pedir_pecas(pecas_faltantes, id_fabrica, id_linha)
    
    def enviar_pedido_pecas(self, lista_pecas, id_fabrica, id_linha):

        printwc(f"Enviando peças para a fábrica {id_fabrica} (linha {id_linha}):", color="yellow")
        # printwc(lista_pecas, color="yellow")

        pedido_pecas = ""
        for peca, quantidade in enumerate(lista_pecas):
            pedido_pecas += str(peca) + "," + str(quantidade) + ";"
        
        pedido_pecas = pedido_pecas[:-1]
        # print(pedido_pecas)

        result = client.publish("fabrica_almoxarifado",
                                "almoxarifado/" + str(self.id_almoxarifado) +   \
                                "/fabrica/" + str(id_fabrica) +                 \
                                "/linha/" + str(id_linha) + "/" + pedido_pecas)

    def pedir_pecas(self, lista_pecas, id_fabrica=None, id_linha=None, pedido_proprio=False):

        printwc("Enviando pedido de peças ao fornecedor", color="red")
        # printwc(lista_pecas, color="red")
        
        pedido_pecas = ""
        for peca, quantidade in enumerate(lista_pecas):
            pedido_pecas += str(peca) + "," + str(quantidade) + ";"
        
        pedido_pecas = pedido_pecas[:-1]

        if(pedido_proprio):
            result = client.publish("almoxarifado_fornecedor",
                                    "almoxarifado/" + str(self.id_almoxarifado) +   \
                                    "/fornecedor/" + str(self.id_fornecedor) +      \
                                    "/auto/" + pedido_pecas)
        else:
            result = client.publish("almoxarifado_fornecedor",
                                    "almoxarifado/" + str(self.id_almoxarifado) +   \
                                    "/fornecedor/" + str(self.id_fornecedor) +      \
                                    "/fabrica/" + str(id_fabrica) +                 \
                                    "/linha/" + str(id_linha) +                     \
                                    "/" + pedido_pecas)

    def receber_pecas(self, lista_pecas, id_fabrica, id_linha):

        for peca, quantidade in enumerate(lista_pecas):
            self.estoque_pecas[peca] += quantidade
    
    def checar_estoque_pecas(self):
        
        pedido = [0] * 100
        status = "VERDE"
        for peca, quantidade in enumerate(self.estoque_pecas):
            if(quantidade < self.limiar_estoque_pecas):
                status = "VERMELHO"
                pedido[peca] = self.limiar_estoque_pecas + self.limiar_estoque_pecas//2
            elif(quantidade < self.limiar_estoque_pecas + self.limiar_estoque_pecas//2):
                status = "AMARELO"

        self.status_estoque_pecas = status

        if(sum(pedido) != 0):
            self.pedir_pecas(pedido, pedido_proprio=True)

        match self.status_estoque_pecas:
            case "VERDE":
                printwc("Estoque com nível bom [VERDE].", color="green")
                # printwc(self.estoque_pecas, color="green")
            case "AMARELO":
                printwc("Estoque com nível baixo [AMARELO].", color="yellow")
                # printwc(self.estoque_pecas, color="yellow")
            case "VERMELHO":
                printwc("Estoque com nível crítico [VERMELHO].", color="red")
                # printwc(self.estoque_pecas, color="red")

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

    def handler(self, acao, lista, id_fabrica=None, id_linha=None, pedido_proprio=False):

        lista = self.converter_lista(lista)

        match acao:
            case "montar pedido de peças da fábrica":
                self.montar_pedido_pecas(lista_pedido_pecas=lista, id_fabrica=id_fabrica, id_linha=id_linha)
            case "receber peças do fornecedor":
                self.receber_pecas(lista_pecas=lista, id_fabrica=id_fabrica, id_linha=id_linha)
            case "receber peças do fornecedor (abastecimento prórpio)":
                self.receber_pecas(lista_pecas=lista)


def on_connect(client, userdata, flags, return_code):

    if return_code == 0:
        printwc("Almoxarifado conectado.", color="purple")
        client.subscribe("fabrica_almoxarifado")
        client.subscribe("almoxarifado_fornecedor")
    else:
        printwc(f"Não foi possível conectar o almoxarifado. Return code: {return_code}", color="purple")

def on_message(client, userdata, message):

    msg = str(message.payload.decode("utf-8"))
    # printwc(f"Menssagem recebida: {msg}", color="blue")

    comando = msg.split("/")

    # estoque/0a,1b,2c,3d,4e
    # letras indicam a quantidade do produto

    match comando[0]:
        case "fabrica":
            almoxarifado.handler(acao="montar pedido de peças da fábrica", lista=comando[6], id_fabrica=comando[1], id_linha=comando[5])
        case "fornecedor" if(comando[4] == "fabrica"):
            almoxarifado.handler(acao="receber peças do fornecedor", lista=comando[8], id_fabrica=comando[5], id_linha=comando[7])
        case "fornecedor" if(comando[4] == "auto"):
            almoxarifado.handler(acao="receber peças do fornecedor (abastecimento prórpio)", lista=comando[8], pedido_proprio=True)

parser = argparse.ArgumentParser(description='Argumentos para execução do almoxarifado.')

parser.add_argument('-i', '--id_almoxarifado', type=str, default="1",
                    help="Define o ID do almoxarifado")
parser.add_argument('-l', '--limiar_estoque_pecas', type=int, default="20",
                    help="Define o limiar de peças do nível vermelho")

args = parser.parse_args()

broker_hostname ="localhost"
port = 1883

# id_almoxarifado = input("Escreva o numero do almoxarifado: ")
id_almoxarifado = args.id_almoxarifado
client = mqtt.Client("almoxarifado" + id_almoxarifado)
client.username_pw_set(username="kenjiueno", password="123456") # uncomment if you use password auth
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_hostname, port) 
client.loop_start()

almoxarifado = Almoxarifado(id_almoxarifado=id_almoxarifado)

while(True):
    if(client.is_connected()):
        almoxarifado.checar_estoque_pecas()
        time.sleep(1)