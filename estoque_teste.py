# ESTOQUE DE PRODUTOS

import argparse
import random
import paho.mqtt.client as mqtt 
import time

from print_with_color import print_with_color as printwc

pedido_foi_feito = False

class Estoque:

    def __init__(self, id_estoque, num_pedidos=5, min_produto=0, max_produto=10, id_fabricas_empurradas=1, id_fabricas_puxadas=2):

        self.id_estoque = id_estoque
        self.produtos_em_estoque = [0, 0, 0, 0, 0]

        self.id_fabricas_empurradas = id_fabricas_empurradas if type(id_fabricas_empurradas) == "list" else [id_fabricas_empurradas]
        self.id_fabricas_puxadas = id_fabricas_puxadas if type(id_fabricas_puxadas) == "list" else [id_fabricas_puxadas]

        self.pedidos_fabricas_puxadas = dict()
        for id in self.id_fabricas_puxadas:
            self.pedidos_fabricas_puxadas[id] = []

        for id in self.id_fabricas_puxadas:
            self.pedidos_fabricas_puxadas[id].append(0)
        
        self.num_pedidos = num_pedidos
        for id in self.id_fabricas_puxadas:
            for i in range(num_pedidos):
                self.pedidos_fabricas_puxadas[id].append(random.sample(range(min_produto, max_produto), 5))

        self.pedidos_atuais = dict()
        for id in self.id_fabricas_puxadas:
            self.pedidos_atuais[id] = self.pedidos_fabricas_puxadas[id][1]

        self.tem_pedidos_pendentes = True
    
    def esperar_pedido(self):

        printwc(self.pedidos_atuais, color="yellow")

        pedidos_concluidos = []
        pedidos_pendentes = []
        for id in self.pedidos_atuais:
            if(sum(self.pedidos_atuais[id]) == 0):
                pedidos_concluidos.append(id)
            else:
                self.mandar_pedido(self.pedidos_atuais[=id])
        
        return pedidos_concluidos
    
    def mandar_pedido(self, lista_pedido):

        mensagem_pedido = ""

        for produto, quantidade in enumerate(lista_pedido):
            mensagem_pedido += str(produto) + "," + str(quantidade) + ";"
        
        mensagem_pedido = mensagem_pedido[:-1]

        result = client.publish("estoque_fabrica", "estoque/" + str(self.id_estoque) + "/fabrica/2/" + mensagem_pedido)

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
        printwc("Estoque conectado.", color="purple")
        client.subscribe("estoque_fabrica")
        client.subscribe("monitor")
    else:
        printwc(f"Não foi possível conectar o estoque. Return code: {return_code}", color="purple")

def on_message(client, userdata, message):

    msg = str(message.payload.decode("utf-8"))
    #printwc(f"Menssagem recebida: {msg}", color="blue")

    comando = msg.split("/")

    match comando[0]:
        case "fabrica" if(int(comando[1]) in estoque.id_fabricas_puxadas):
            lista_produtos = estoque.converter_lista(comando[4])

            for produto, quantidade in enumerate(lista_produtos):
                estoque.pedidos_atuais[int(comando[1])][produto] -= quantidade
                estoque.produtos_em_estoque[produto] += quantidade
        
        case "fabrica" if(int(comando[1]) in estoque.id_fabricas_empurradas):
            lista_produtos = estoque.converter_lista(comando[4])

            printwc(lista_produtos, color="yellow")

            for produto, quantidade in enumerate(lista_produtos):
                estoque.produtos_em_estoque[produto] += quantidade

# Argumentos
parser = argparse.ArgumentParser(description='Argumentos para execução do estoque.')

parser.add_argument('-i', '--id_estoque', type=str, default="1",
                    help="Define o ID do estoque")
parser.add_argument('-n', '--num_pedidos', type=int, default="5",
                    help="Define o número de pedidos que serão feitos")
parser.add_argument('-fe', '--id_fabricas_empurradas', nargs="+", type=int, default="1",
                    help="Define o ID do estoque")
parser.add_argument('-fp', '--id_fabricas_puxadas', nargs="+", type=int, default="2",
                    help="Define o número de pedidos que serão feitos")

args = parser.parse_args()

broker_hostname ="mosquitto"
port = 1883

id_estoque = args.id_estoque
client = mqtt.Client("estoque" + id_estoque)
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_hostname, port) 
client.loop_start()

estoque = Estoque(id_estoque, num_pedidos=args.num_pedidos, min_produto=0, max_produto=5, id_fabricas_empurradas=args.id_fabricas_empurradas, id_fabricas_puxadas=args.id_fabricas_puxadas)

while(True):
    if(not client.is_connected()):
        pass
    
    elif(estoque.tem_pedidos_pendentes):
        for id in estoque.pedidos_fabricas_puxadas:
            printwc(f"Pedido {estoque.pedidos_fabricas_puxadas[id][0]}: {estoque.pedidos_atuais[id]}", color="red")
        
        pedidos_concluidos = estoque.esperar_pedido()
        if(pedidos_concluidos):
            for id in pedidos_concluidos:
                estoque.pedidos_fabricas_puxadas[id][0] += 1
                if estoque.pedidos_fabricas_puxadas[id][0] <= estoque.num_pedidos:
                    estoque.pedidos_atuais[id] = estoque.pedidos_fabricas_puxadas[id][estoque.pedidos_fabricas_puxadas[id][0]]
            printwc("Pedido chegou!", color="green")
        else:
            estoque.tem_pedidos_pendentes = False
        
        printwc(f"Produtos em estoque: {estoque.produtos_em_estoque}", color="purple")
        produtosEmEstoque = ""
        for i in range(0, 5):
            produtosEmEstoque = produtosEmEstoque
            if(i < 4):
                produtosEmEstoque = produtosEmEstoque + ","
        result = client.publish("monitor", "estoque/" + str(estoque.id_estoque) + "/" + produtosEmEstoque)
    time.sleep(1)