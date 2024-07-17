import argparse
import paho.mqtt.client as mqtt
import time

from print_with_color import print_with_color as printwc

class Fornecedor:

    def __init__(self, id_fornecedor=1):
        self.id_fornecedor = id_fornecedor

    def enviar_pecas(self, lista_pecas, id_almoxarifado, id_fabrica=None, id_linha=None, pedido_proprio=False):
        printwc("Enviando peças para o almoxarifado.", color="yellow")
        lista_pecas = self.converter_lista(lista_pecas)
        pedido_pecas = ";".join(f"{peca},{quantidade}" for peca, quantidade in enumerate(lista_pecas))

        if pedido_proprio:
            result = client.publish("almoxarifado_fornecedor",
                                    f"fornecedor/{self.id_fornecedor}/almoxarifado/{id_almoxarifado}/auto/{pedido_pecas}")
        else:
            result = client.publish("almoxarifado_fornecedor",
                                    f"fornecedor/{self.id_fornecedor}/almoxarifado/{id_almoxarifado}/fabrica/{id_fabrica}/linha/{id_linha}/{pedido_pecas}")

    def converter_lista(self, lista1):
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
        printwc("Fornecedor conectado.", color="purple")
        client.subscribe("almoxarifado_fornecedor")
    else:
        printwc(f"Não foi possível conectar o fornecedor. Return code: {return_code}", color="purple")

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    comando = msg.split("/")

    if comando[0] == "almoxarifado" and comando[3] == str(fornecedor.id_fornecedor) and comando[4] == "fabrica":
        fornecedor.enviar_pecas(comando[8], id_almoxarifado=comando[1], id_fabrica=comando[5], id_linha=comando[7])
    elif comando[0] == "almoxarifado" and comando[3] == str(fornecedor.id_fornecedor) and comando[4] == "auto":
        fornecedor.enviar_pecas(comando[5], id_almoxarifado=comando[1], pedido_proprio=True)

parser = argparse.ArgumentParser(description='Argumentos para execução do fornecedor.')
parser.add_argument('-i', '--id_fornecedor', type=str, default="1", help="Define o ID do fornecedor")
args = parser.parse_args()

broker_hostname = "mosquitto"
port = 1883

id_fornecedor = args.id_fornecedor
client = mqtt.Client(f"fornecedor{id_fornecedor}")
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_hostname, port)
client.loop_start()

fornecedor = Fornecedor(id_fornecedor=id_fornecedor)

while True:
    time.sleep(1)