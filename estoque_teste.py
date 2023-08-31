# ESTOQUE DE PRODUTOS

import argparse
import random
import paho.mqtt.client as mqtt 
import time

from print_with_color import print_with_color as printwc

pedido_foi_feito = False

class Estoque:

    def __init__(self, id_estoque, num_pedidos=5, min_produto=0, max_produto=10):

        self.id_estoque = id_estoque
        self.produtos_em_estoque = [0, 0, 0, 0, 0]
        self.num_pedido_atual = 0
        self.num_pedidos = num_pedidos
        self.lista_pedidos = []
        for i in range(num_pedidos):
            self.lista_pedidos.append(random.sample(range(min_produto, max_produto), 5))
        self.pedido_atual = self.lista_pedidos[0]
        self.pedido_foi_feito = False
    
    def esperar_pedido(self):

        if(sum(self.pedido_atual) == 0):
            return True
        
        else:
            self.mandar_pedido()
            return False
    
    def mandar_pedido(self):

        mensagem_pedido = ""

        for produto, quantidade in enumerate(self.pedido_atual):
            mensagem_pedido += str(produto) + "," + str(quantidade) + ";"
        
        mensagem_pedido = mensagem_pedido[:-1]
        # print(mensagem_pedido)

        result = client.publish("estoque_fabrica", "estoque/" + str(self.id_estoque) + "/fabrica/2/" + mensagem_pedido)

def on_connect(client, userdata, flags, return_code):

    if return_code == 0:
        printwc("Estoque conectado.", color="purple")
        client.subscribe("estoque_fabrica")
    else:
        printwc(f"Não foi possível conectar o estoque. Return code: {return_code}", color="purple")

def on_message(client, userdata, message):

    msg = str(message.payload.decode("utf-8"))
    printwc(f"Menssagem recebida: {msg}", color="blue")

    comando = msg.split("/")

    # estoque/0a,1b,2c,3d,4e
    # letras indicam a quantidade do produto
    if(comando[0] == "fabrica"):

        # printwc(comando[2], color="cyan")

        pedido = comando[4].split(";")

        lista_produtos = []
        for pedido_produto in pedido:
            lista_produtos.append(pedido_produto.split(","))
        
        # printwc(lista_produtos, color="cyan")

        lista_produtos_int = []
        for pedido_produto in lista_produtos:
            lista_produtos_int.append([int(pedido_produto[0]), int(pedido_produto[1])])

        # printwc(lista_produtos_int, color="cyan")

        for produto, quantidade in lista_produtos_int:
            estoque.pedido_atual[produto] -= quantidade
            estoque.produtos_em_estoque[produto] += quantidade

# def mandar_pedido(pedido):

#     mensagem_pedido = ""

#     for produto, quantidade in enumerate(pedido):
#         mensagem_pedido += str(produto) + "," + str(quantidade) + ";"
    
#     mensagem_pedido = mensagem_pedido[:-1]
#     print(mensagem_pedido)

#     result = client.publish("estoque_fabrica", "estoque/" + str(id_estoque) + "/" + mensagem_pedido)

# def esperar_pedido(pedido_atual):

#     if(sum(pedido_atual) == 0):
#         pedido_foi_feito = False
#         return True
    
#     elif(pedido_foi_feito == False):
#         mandar_pedido(pedido_atual)
#         pedido_foi_feito = True
#         return False
    
#     else:
#         return False

parser = argparse.ArgumentParser(description='Argumentos para execução do estoque.')

parser.add_argument('-e', '--id_estoque', type=str, default="1",
                    help="Define o ID do estoque")
parser.add_argument('-np', '--num_pedidos', type=int, default="5",
                    help="Define o número de pedidos que serão feitos")

args = parser.parse_args()

broker_hostname ="localhost"
port = 1883

# id_estoque = input("Escreva o numero do estoque: ")
id_estoque = args.id_estoque
client = mqtt.Client("estoque" + id_estoque)
client.username_pw_set(username="kenjiueno", password="123456") # uncomment if you use password auth
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_hostname, port) 
client.loop_start()

num_pedidos = args.num_pedidos
estoque = Estoque(id_estoque, num_pedidos=num_pedidos, min_produto=0, max_produto=5)


while(True):
    if(not client.is_connected()):
        pass
    
    elif(estoque.num_pedido_atual < estoque.num_pedidos):
        printwc(f"Pedido {estoque.num_pedido_atual}: {estoque.pedido_atual}", color="red")
        
        if(estoque.esperar_pedido()):
            # num_pedido_atual += 1
            estoque.num_pedido_atual += 1
            if estoque.num_pedido_atual < estoque.num_pedidos:
                estoque.pedido_atual = estoque.lista_pedidos[estoque.num_pedido_atual]
            printwc("Pedido chegou!", color="green")
        

        printwc(f"Produtos em estoque: {estoque.produtos_em_estoque}", color="purple")

        time.sleep(1)