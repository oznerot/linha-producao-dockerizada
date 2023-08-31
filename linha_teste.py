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


        result = client.publish("fabrica_linha", "linha/" + str(id_linha) + "/fabrica/" + str(id_fabrica) + "/pedido_produtos/" + pedido)

    def montar_pedido_produtos(self, lista_pedido_produtos):

        pedido_completo = True
        pecas_faltantes = [0] * len(self.buffer_pecas)
        pecas_consumidas = [0] * len(self.buffer_pecas)

        printwc(f"Montando pedido de produtos: {lista_pedido_produtos}", color="red")

        for produto, quantidade in enumerate(lista_pedido_produtos):
            for peca in range(len(self.pecas_produto[produto])):
                if(self.buffer_pecas[peca] >= self.pecas_produto[produto][peca] * quantidade):
                    pecas_consumidas[peca] = self.pecas_produto[produto][peca] * quantidade
                else:
                    pedido_completo = False
                    pecas_faltantes[peca] = self.pecas_produto[produto][peca] * quantidade - self.buffer_pecas[peca]

        if(pedido_completo):
            for peca, quantidade     in enumerate(pecas_consumidas):
                self.buffer_pecas[peca] -= quantidade
            self.enviar_pedido_produtos(lista_pedido_produtos)
        else:
            self.pedir_pecas(pecas_faltantes)
    
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
            case "AMARELO":
                printwc("Estoque com nível baixo [AMARELO].", color="yellow")
            case "VERMELHO":
                printwc("Estoque com nível crítico [VERMELHO].", color="red")

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
    
    match comando[4]:
        case "pedido_pecas" if((comando[0] == "fabrica") & (comando[1] == linha.id_fabrica) & (comando[3] == linha.id_linha)):
            linha.handler(acao="receber peças", lista=comando[5])
            
        case "pedido_produto" if((comando[0] == "fabrica") & (comando[1] == linha.id_fabrica) & (comando[3] == linha.id_linha)):
            linha.handler(acao="montar pedido", lista=comando[5])

parser = argparse.ArgumentParser(description='Argumentos para execução da linha.')

parser.add_argument('-i', '--id_linha', type=str, default="0",
                    help="Define o ID da linha")
parser.add_argument('-f', '--id_fabrica', type=str, default="2",
                    help="Define o ID da fábrica que a linha pertence")
parser.add_argument('-l', '--limiar_pecas', type=int, default="20",
                    help="Define o limiar de peças do nível vermelho")

args = parser.parse_args()

broker_hostname ="mosquitto"
port = 1883 
id_linha = args.id_linha
id_fabrica = args.id_fabrica
client = mqtt.Client("linha" + id_linha)
client.on_connect=on_connect
client.on_message=on_message

client.connect(broker_hostname, port) 
client.loop_start()

linha = Linha(id_linha=id_linha, id_fabrica=id_fabrica, limiar_pecas=args.limiar_pecas)

while(True):
    if(client.is_connected()):
        linha.checar_estoque_pecas()
        time.sleep(1)