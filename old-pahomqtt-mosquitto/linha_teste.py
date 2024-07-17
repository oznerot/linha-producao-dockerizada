import argparse
import paho.mqtt.client as mqtt
import time

from print_with_color import print_with_color as printwc

class Linha:

    def __init__(self, id_linha, id_fabrica, limiar_pecas=20):
        self.id_linha = id_linha
        self.id_fabrica = id_fabrica
        self.limiar_pecas = limiar_pecas
        self.buffer_pecas = [1] * 100
        self.status_buffer = "VERMELHO"

    def enviar_pedido_pecas(self, lista_pedido_pecas):
        pedido_pecas = ";".join(f"{peca},{quantidade}" for peca, quantidade in enumerate(lista_pedido_pecas))
        printwc(f"Enviando pedido de peças: {pedido_pecas}", color="yellow")
        result = client.publish("fabrica_linha", f"linha/{self.id_linha}/fabrica/{self.id_fabrica}/pedido_pecas/{pedido_pecas}")

    def enviar_pedido_produtos(self, lista_pedido_produtos):
        pedido_produtos = ";".join(f"{produto},{quantidade}" for produto, quantidade in enumerate(lista_pedido_produtos))
        printwc(f"Enviando produtos: {pedido_produtos}", color="green")
        result = client.publish("fabrica_linha", f"linha/{self.id_linha}/fabrica/{self.id_fabrica}/pedido_produtos/{pedido_produtos}")

    def montar_pedido_produtos(self, lista_pedido_produtos):
        pedido_completo = True
        pecas_faltantes = [0] * len(self.buffer_pecas)

        printwc(f"Montando pedido de produtos: {lista_pedido_produtos}", color="red")

        for produto, quantidade in enumerate(lista_pedido_produtos):
            for peca, qtd_necessaria in enumerate(self.pecas_produto[produto]):
                if self.buffer_pecas[peca] < qtd_necessaria * quantidade:
                    pedido_completo = False
                    pecas_faltantes[peca] += qtd_necessaria * quantidade - self.buffer_pecas[peca]

        if pedido_completo:
            for produto, quantidade in enumerate(lista_pedido_produtos):
                for peca, qtd_necessaria in enumerate(self.pecas_produto[produto]):
                    self.buffer_pecas[peca] -= qtd_necessaria * quantidade
            self.enviar_pedido_produtos(lista_pedido_produtos)
        else:
            self.pedir_pecas(pecas_faltantes)

    def pedir_pecas(self, lista_pedido_pecas):
        pedido_pecas = ";".join(f"{peca},{quantidade}" for peca, quantidade in enumerate(lista_pedido_pecas))
        printwc(f"Pedindo peças ao almoxarifado: {pedido_pecas}", color="yellow")
        result = client.publish("fabrica_linha", f"linha/{self.id_linha}/fabrica/{self.id_fabrica}/pedido_pecas/{pedido_pecas}")

    def receber_pecas(self, lista_pecas_recebidas):
        printwc(f"Recebendo peças: {lista_pecas_recebidas}", color="yellow")
        for peca, quantidade in enumerate(lista_pecas_recebidas):
            self.buffer_pecas[peca] += quantidade

    def checar_estoque_pecas(self):
        status = "VERDE"
        for peca, quantidade in enumerate(self.buffer_pecas):
            if quantidade < self.limiar_pecas:
                status = "VERMELHO"
                break
            elif quantidade < self.limiar_pecas + self.limiar_pecas // 2:
                status = "AMARELO"

        self.status_buffer = status

        if self.status_buffer == "VERMELHO":
            printwc("Estoque com nível crítico [VERMELHO].", color="red")
            self.pedir_pecas([self.limiar_pecas] * len(self.buffer_pecas))
        elif self.status_buffer == "AMARELO":
            printwc("Estoque com nível baixo [AMARELO].", color="yellow")
        else:
            printwc("Estoque com nível bom [VERDE].", color="green")

    def converter_lista(self, lista1):
        lista2 = lista1.split(";")
        lista3 = []
        for pedido_produto in lista2:
            lista3.append(pedido_produto.split(","))
        lista4 = [0] * len(lista3)
        for indice, quantidade in lista3:
            lista4[int(indice)] = int(quantidade)
        return lista4

    def handler(self, acao, lista):
        lista = self.converter_lista(lista)
        if acao == "enviar_produtos":
            self.enviar_pedido_produtos(lista)
        elif acao == "montar_pedido":
            self.montar_pedido_produtos(lista)
        elif acao == "receber_pecas":
            self.receber_pecas(lista)

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        printwc("Linha conectada.", color="purple")
        client.subscribe("fabrica")
        client.subscribe("fabrica_linha")
    else:
        printwc(f"Não foi possível conectar a linha. Return code: {return_code}", color="purple")

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    comando = msg.split("/")

    if comando[0] == "fabrica" and comando[1] == linha.id_fabrica and comando[3] == linha.id_linha and comando[4] == "pedido_pecas":
        linha.handler("receber_pecas", comando[5])
    elif comando[0] == "fabrica" and comando[1] == linha.id_fabrica and comando[3] == linha.id_linha and comando[4] == "pedido_produto":
        linha.handler("montar_pedido", comando[5])

# Argumentos para execução da linha
parser = argparse.ArgumentParser(description='Argumentos para execução da linha.')

parser.add_argument('-i', '--id_linha', type=str, default="0", help="Define o ID da linha")
parser.add_argument('-f', '--id_fabrica', type=str, default="2", help="Define o ID da fábrica que a linha pertence")
parser.add_argument('-l', '--limiar_pecas', type=int, default="20", help="Define o limiar de peças do nível vermelho")

args = parser.parse_args()

broker_hostname = "mosquitto"
port = 1883
id_linha = args.id_linha
id_fabrica = args.id_fabrica

client = mqtt.Client("linha" + id_linha)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_hostname, port)
client.loop_start()

linha = Linha(id_linha=id_linha, id_fabrica=id_fabrica, limiar_pecas=args.limiar_pecas)

while True:
    if client.is_connected():
        linha.checar_estoque_pecas()
        time.sleep(1)