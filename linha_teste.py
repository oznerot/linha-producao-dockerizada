# Linha

import argparse
import paho.mqtt.client as mqtt 
import time

from print_with_color import print_with_color as printwc

npecas = 10
produto1 = [0,1,2,3,4,5,8,9]
pecasNaLinha = [1,1,1,1,1,1,1,1,1,1]
id_linha = 0

class Linha:

    def __init__(self, id_linha, id_fabrica, tamanho_lote=48, limiar_pecas=20):

        self.id_linha = id_linha
        self.id_fabrica = id_fabrica

        self.kit_basico = 43
        self.kit_variacao = [20, 33]

        self.buffer_pecas = [1] * 100
        self.pedido_pecas = [0] * 5
        self.pedido_produtos = [0] * 5

        self.pecas_produto = [[1] * 53,
                              [1] * 53,
                              [1] * 53,
                              [1] * 53,
                              [1] * 53]
        
        self.limiar_pecas = limiar_pecas
        self.status_buffer = "VERMELHO"
    
    def enviar_pedido_pecas(self, lista_pedido_pecas):

        self.pedido_pecas = ""
        for peca, quantidade in enumerate(lista_pedido_pecas):
            self.pedido_pecas += str(peca) + "," + str(quantidade) + ";"
        self.pedido_pecas = self.pedido_pecas[:-1]

        printwc(f"Enviando pedido de peças: {self.pedido_pecas}", color="yellow")

        result = client.publish("fabrica_linha", "linha/" + str(self.id_linha) + "/fabrica/" + str(self.id_fabrica) + "/pedido_pecas/" + self.pedido_pecas)

    def enviar_pedido_produtos(self, lista_pedido_produtos):

        printwc(f"Enviando produtos: {lista_pedido_produtos}", color="green")

        pedido = ""
        for produto, quantidade in enumerate(lista_pedido_produtos):
            pedido += str(produto) + "," + str(quantidade) + ";"
        pedido = pedido[:-1]

        # printwc(pedido, color="cyan")

        result = client.publish("fabrica_linha", "linha/" + str(id_linha) + "/fabrica/" + str(id_fabrica) + "/pedido_produtos/" + pedido)

    def montar_pedido_produtos(self, lista_pedido_produtos):

        pedido_completo = True
        pecas_faltantes = [0] * len(self.buffer_pecas)
        pecas_consumidas = [0] * len(self.buffer_pecas)

        printwc(f"Montando pedido de produtos: {lista_pedido_produtos}", color="red")

        for produto, quantidade in enumerate(lista_pedido_produtos):
            # count = 0
            for peca in range(len(self.pecas_produto[produto])):
                # count += 1
                # printwc(count, color="yellow")
                if(self.buffer_pecas[peca] >= self.pecas_produto[produto][peca] * quantidade):
                    # pecas_consumidas.append(self.pecas_produto[produto][peca] * quantidade)
                    pecas_consumidas[peca] = self.pecas_produto[produto][peca] * quantidade
                    # print(".", end="")
                else:
                    pedido_completo = False
                    # pecas_faltantes.append(self.pecas_produto[produto][peca] * quantidade - self.buffer_pecas[peca])
                    pecas_faltantes[peca] = self.pecas_produto[produto][peca] * quantidade - self.buffer_pecas[peca]
                    # print("-", end="")

        # printwc(pecas_consumidas, color="yellow")
        # printwc(pecas_faltantes, color="red")

        # print(len(pecas_consumidas), len(pecas_faltantes), len(self.pecas_produto[0]))

        if(pedido_completo):
            for peca, quantidade     in enumerate(pecas_consumidas):
                self.buffer_pecas[peca] -= quantidade
            self.enviar_pedido_produtos(lista_pedido_produtos)
            # return True
        else:
            self.pedir_pecas(pecas_faltantes)
            # return False
    
    def pedir_pecas(self, lista_pedido_pecas):

        pedido = ""
        for peca, quantidade in enumerate(lista_pedido_pecas):
            pedido += str(peca) + "," + str(quantidade) + ";"
        pedido = pedido[:-1]
        result = client.publish("fabrica_linha", "linha/" + str(self.id_linha) + "/fabrica/" + str(self.id_fabrica) + "/pedido_pecas/" + pedido)
    
    def receber_pecas(self, lista_pecas_recebidas):

        printwc(f"Recebendo pecas: {lista_pecas_recebidas}", color="yellow")

        for peca, quantidade in enumerate(lista_pecas_recebidas):
            self.buffer_pecas[peca] += quantidade
    
    def checar_estoque_pecas(self):
        
        pedido = [0] * 100
        status = "VERDE"
        for peca, quantidade in enumerate(self.buffer_pecas):
            if(quantidade < self.limiar_pecas):
                status = "VERMELHO"
                pedido[peca] = self.limiar_pecas + self.limiar_pecas//2
            elif(quantidade < self.limiar_pecas + self.limiar_pecas//2):
                status = "AMARELO"

        self.status_buffer = status

        if(sum(pedido) != 0):
            self.pedir_pecas(pedido)

        match self.status_buffer:
            case "VERDE":
                printwc("Estoque com nível bom [VERDE].", color="green")
                # printwc(self.buffer_pecas, color="green")
            case "AMARELO":
                printwc("Estoque com nível baixo [AMARELO].", color="yellow")
                # printwc(self.buffer_pecas, color="yellow")
            case "VERMELHO":
                printwc("Estoque com nível crítico [VERMELHO].", color="red")
                # printwc(self.buffer_pecas, color="red")

    def converter_lista(self, lista1):
        
        lista2 = lista1.split(";")

        # printwc(lista2, color="cyan")

        lista3 = []
        for pedido_produto in lista2:
            lista3.append(pedido_produto.split(","))
        
        # printwc(lista3, color="cyan")
        
        lista4 = [0] * len(lista3)
        for indice, quantidade in lista3:
            lista4[int(indice)] = int(quantidade)

        # printwc(lista4, color="cyan")
        
        return lista4
    
    def handler(self, acao, lista):

        lista = self.converter_lista(lista)

        # printwc(lista, color="cyan")

        match acao:
            case "enviar produtos":
                self.enviar_pedido_produtos(lista)
            case "montar pedido":
                self.montar_pedido_produtos(lista)
            case "receber peças":
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
    printwc(f"Menssagem recebida: {msg}", color="blue")

    comando = msg.split("/")

    # if(comando[0] == "fabrica" and comando[1] == str(id_linha)):
    #     pecas = comando[2].split(",")
    #     #pecasRecebidas = []
    #     for i in range(len(pecas)):
    #         peca = int(pecas[i])
    #         pecasNaLinha[peca] += 1
    
    # elif(comando[0] == "estoque"):
    #     print(comando[2])

    # Caso a mensagem não seja da fábrica da linha
    # if((comando[1] != linha.id_fabrica) | (comando[3] != linha.id_linha)):
    #     return
    
    match comando[4]:
        case "pedido_pecas" if((comando[0] == "fabrica") & (comando[1] == linha.id_fabrica) & (comando[3] == linha.id_linha)):
            # pecas = comando[5].split(",")
            # #pecasRecebidas = []
            # for i in range(len(pecas)):
            #     peca = int(pecas[i])
            #     pecasNaLinha[peca] += 1
            linha.handler(acao="receber peças", lista=comando[5])
            
        case "pedido_produto" if((comando[0] == "fabrica") & (comando[1] == linha.id_fabrica) & (comando[3] == linha.id_linha)):
            # print(comando[5])
            # linha.handler(acao="enviar produtos", lista=comando[5])
            linha.handler(acao="montar pedido", lista=comando[5])


# def pedirpecas(pecas):

#     pedido = ""
#     for i in range (len(pecas)):
#         pedido = pedido + str(pecas[i]) + ","
#         # if(i < len(pecas) - 1):
#         #     pedido = pedido 
#     pedido = pedido[:-1]
#     result = client.publish("fabrica_linha", "linha/" + str(id_linha) + "/fabrica/" + str(id_fabrica) + "/pedido_pecas/" + pedido)
#     #printwc(pedido)

# def montarproduto(produto):
#     contador = 0
#     pecas_faltantes = []
#     pecas_consumidas = []
#     if(produto == 1):
#         numero_pecas_produto = len(produto1)
#         for i in range (numero_pecas_produto):
#             if(pecasNaLinha[produto1[i]] > 0):
#                 pecas_consumidas.append(produto1[i])
#             else:
#                 contador+= 1
#                 pecas_faltantes.append(produto1[i])
#     if(contador == 0):
#         for i in range (len(pecas_consumidas)):
#             pecasNaLinha[pecas_consumidas[i]] -= 1
#         return True
#     else:
#         #printwc(pecas_faltantes)
#         #printwc(pecasNaLinha)
#         pedirpecas(pecas_faltantes)
#         return False    


# def montarpedido(pedido):
#     montou = montarproduto(pedido)
#     return montou

parser = argparse.ArgumentParser(description='Argumentos para execução da linha.')

parser.add_argument('-i', '--id_linha', type=str, default="0",
                    help="Define o ID da linha")
parser.add_argument('-f', '--id_fabrica', type=str, default="2",
                    help="Define o ID da fábrica que a linha pertence")
parser.add_argument('-l', '--limiar_pecas', type=int, default="20",
                    help="Define o limiar de peças do nível vermelho")

args = parser.parse_args()

broker_hostname ="localhost"
port = 1883 
# id_linha = input("Escreva o numero da linha: ")
# id_fabrica = input("Escreva o numero da fábrica: ")
id_linha = args.id_linha
id_fabrica = args.id_fabrica
client = mqtt.Client("linha" + id_linha)
client.username_pw_set(username="kenjiueno", password="123456") # uncomment if you use password auth
client.on_connect=on_connect
client.on_message=on_message

client.connect(broker_hostname, port) 
client.loop_start()

# pedidos = [1,1,1,1]
# npedidos = 4
# pedidoatual = 0
# do = True

linha = Linha(id_linha=id_linha, id_fabrica=id_fabrica, limiar_pecas=args.limiar_pecas)

# while(do):
#     if(client.is_connected()):
#         if(npedidos - pedidoatual > 0):
#             #printwc(pedidos[pedidoatual])
#             printwc("Montando pedido: " + str(pedidoatual), color="red")
#             if(montarpedido(pedidos[pedidoatual])):
#                 pedidoatual += 1
#                 printwc("Pedido montado!", color="green")

#             time.sleep(1)

while(True):
    if(client.is_connected()):
        linha.checar_estoque_pecas()
        time.sleep(1)