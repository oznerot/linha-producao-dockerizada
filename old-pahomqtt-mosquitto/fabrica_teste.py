import argparse
import paho.mqtt.client as mqtt
import random
import time

from print_with_color import print_with_color as printwc

class Fabrica:

    def __init__(self, id_fabrica=2, tipo_fabrica="puxada", tamanho_lote=48, num_linhas=8, id_almoxarifado=1):
        self.id_fabrica = id_fabrica
        self.tipo_fabrica = tipo_fabrica
        self.tamanho_lote = tamanho_lote
        self.num_linhas = num_linhas
        self.id_almoxarifado = id_almoxarifado

    def enviar_pedido_pecas(self, lista_pedido_pecas, id_linha):
        pedido = ";".join(f"{peca},{quantidade}" for peca, quantidade in enumerate(lista_pedido_pecas))
        result = client.publish("fabrica_almoxarifado", f"fabrica/{self.id_fabrica}/almoxarifado/{self.id_almoxarifado}/linha/{id_linha}/{pedido}")

    def receber_pedido_pecas(self, lista_pedido_pecas, id_linha):
        pedido = ";".join(f"{peca},{quantidade}" for peca, quantidade in enumerate(lista_pedido_pecas))
        result = client.publish("fabrica_linha", f"fabrica/{self.id_fabrica}/linha/{id_linha}/pedido_pecas/{pedido}")

    def enviar_produtos_estoque(self, lista_produtos):
        pedido = ";".join(f"{produto},{quantidade}" for produto, quantidade in enumerate(lista_produtos))
        result = client.publish("estoque_fabrica", f"fabrica/{self.id_fabrica}/estoque/1/{pedido}")

    def enviar_pedido_linha(self, lista_produtos, id_linha=0):
        pedido = ";".join(f"{produto},{quantidade}" for produto, quantidade in enumerate(lista_produtos))
        result = client.publish("fabrica_linha", f"fabrica/{self.id_fabrica}/linha/{id_linha}/pedido_produto/{pedido}")

    def enviar_pedido_linha_distribuido(self, lista_produtos):
        parte_lista_produto = [quantidade // self.num_linhas for quantidade in lista_produtos]

        for linha in range(self.num_linhas - 1):
            self.enviar_pedido_linha(parte_lista_produto, id_linha=linha)

        parte_lista_produto = [quantidade % self.num_linhas + parte_lista_produto[indice] for indice, quantidade in enumerate(lista_produtos)]
        self.enviar_pedido_linha(parte_lista_produto, id_linha=self.num_linhas - 1)

    def converter_lista(self, lista1):
        lista2 = lista1.split(";")
        lista3 = []
        for pedido_produto in lista2:
            lista3.append(pedido_produto.split(","))
        lista4 = [0] * len(lista3)
        for indice, quantidade in lista3:
            lista4[int(indice)] = int(quantidade)
        return lista4

    def handler(self, acao, lista=None, id_linha=None):
        if lista:
            lista = self.converter_lista(lista)

        if acao == "enviar_pedido_para_linha":
            self.enviar_pedido_linha_distribuido(lista)
        elif acao == "enviar_pedido_de_pecas_para_almoxarifado":
            self.enviar_pedido_pecas(lista, id_linha)
        elif acao == "receber_pedido_do_almoxarifado":
            self.receber_pedido_pecas(lista, id_linha)
        elif acao == "enviar_pedido_de_produtos_para_o_estoque":
            self.enviar_produtos_estoque(lista)
        elif acao == "enviar_lote_para_linha":
            lista = [10, 10, 10, 9, 9]
            self.enviar_pedido_linha_distribuido(lista)

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        printwc("Fábrica conectada.", color="purple")
        client.subscribe("estoque_fabrica")
        client.subscribe("fabrica_linha")
        client.subscribe("fabrica_almoxarifado")
    else:
        printwc(f"Não foi possível conectar a fábrica. Return code: {return_code}", color="purple")

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    comando = msg.split("/")

    if comando[0] == "linha" and comando[3] == str(fabrica.id_fabrica) and comando[4] == "pedido_pecas":
        fabrica.handler("enviar_pedido_de_pecas_para_almoxarifado", lista=comando[5], id_linha=comando[1])

    elif comando[0] == "linha" and comando[3] == str(fabrica.id_fabrica) and comando[4] == "pedido_produto":
        lista = fabrica.converter_lista(comando[5])
        fabrica.handler("enviar_pedido_de_produtos_para_o_estoque", lista=comando[5])

    elif comando[0] == "estoque" and comando[3] == str(fabrica.id_fabrica) and fabrica.tipo_fabrica == "puxada":
        fabrica.handler("enviar_pedido_para_linha", lista=comando[4])

    elif comando[0] == "almoxarifado" and comando[3] == str(fabrica.id_fabrica):
        fabrica.handler("receber_pedido_do_almoxarifado", lista=comando[6], id_linha=comando[5])

parser = argparse.ArgumentParser(description='Argumentos para execução da fábrica.')
parser.add_argument('-i', '--id_fabrica', type=str, default="2", help="Define o ID da fábrica")
parser.add_argument('-n', '--num_linhas', type=int, default=8, help="Define o número de linhas da fábrica")
parser.add_argument('-t', '--tipo_fabrica', type=str, default="puxada", help="Define o tipo de fábrica (puxada ou empurrada)")
args = parser.parse_args()

broker_hostname = "mosquitto"
port = 1883

id_fabrica = args.id_fabrica
client = mqtt.Client("fabrica" + id_fabrica)
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_hostname, port)
client.loop_start()

fabrica = Fabrica(id_fabrica=args.id_fabrica, num_linhas=args.num_linhas, tipo_fabrica=args.tipo_fabrica)

while True:
    if client.is_connected():
        if fabrica.tipo_fabrica == 'empurrada':
            fabrica.handler("enviar_lote_para_linha")
    time.sleep(1)