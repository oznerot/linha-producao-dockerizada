import argparse
import random
import paho.mqtt.client as mqtt
import time

from print_with_color import print_with_color as printwc

class Estoque:

    def __init__(self, id_estoque, num_pedidos=5, min_produto=0, max_produto=10, id_fabricas_empurradas=[1], id_fabricas_puxadas=[2]):
        self.id_estoque = id_estoque
        self.produtos_em_estoque = [0] * 5
        self.id_fabricas_empurradas = id_fabricas_empurradas
        self.id_fabricas_puxadas = id_fabricas_puxadas
        self.num_pedidos = num_pedidos
        self.pedidos_fabricas_puxadas = {id: [[random.randint(min_produto, max_produto) for _ in range(5)] for _ in range(num_pedidos + 1)] for id in id_fabricas_puxadas}
        self.pedidos_atuais = {id: self.pedidos_fabricas_puxadas[id][1] for id in id_fabricas_puxadas}
        self.tem_pedidos_pendentes = True

    def esperar_pedido(self):
        pedidos_concluidos = []
        for id, pedido_atual in self.pedidos_atuais.items():
            if sum(pedido_atual) == 0:
                pedidos_concluidos.append(id)
            else:
                self.mandar_pedido(pedido_atual)
        return pedidos_concluidos

    def mandar_pedido(self, lista_pedido):
        mensagem_pedido = ";".join(f"{produto},{quantidade}" for produto, quantidade in enumerate(lista_pedido))
        result = client.publish("estoque_fabrica", f"estoque/{self.id_estoque}/fabrica/2/{mensagem_pedido}")

    def converter_lista(self, lista1):
        lista_pedido = [0] * 5
        for pedido_produto in lista1.split(";"):
            produto, quantidade = map(int, pedido_produto.split(","))
            lista_pedido[produto] = quantidade
        return lista_pedido

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        printwc("Estoque conectado.", color="purple")
        client.subscribe("estoque_fabrica")
        client.subscribe("monitor")
    else:
        printwc(f"Não foi possível conectar o estoque. Return code: {return_code}", color="purple")

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    comando = msg.split("/")

    if comando[0] == "fabrica":
        id_fabrica = int(comando[1])
        if id_fabrica in estoque.id_fabricas_puxadas:
            lista_produtos = estoque.converter_lista(comando[4])
            for produto, quantidade in enumerate(lista_produtos):
                estoque.pedidos_atuais[id_fabrica][produto] -= quantidade
                estoque.produtos_em_estoque[produto] += quantidade
        elif id_fabrica in estoque.id_fabricas_empurradas:
            lista_produtos = estoque.converter_lista(comando[4])
            for produto, quantidade in enumerate(lista_produtos):
                estoque.produtos_em_estoque[produto] += quantidade

parser = argparse.ArgumentParser(description='Argumentos para execução do estoque.')
parser.add_argument('-i', '--id_estoque', type=str, default="1", help="Define o ID do estoque")
parser.add_argument('-n', '--num_pedidos', type=int, default="5", help="Define o número de pedidos que serão feitos")
parser.add_argument('-fe', '--id_fabricas_empurradas', nargs="+", type=int, default=[1], help="Lista de IDs de fábricas empurradas")
parser.add_argument('-fp', '--id_fabricas_puxadas', nargs="+", type=int, default=[2], help="Lista de IDs de fábricas puxadas")
args = parser.parse_args()

broker_hostname = "mosquitto"
port = 1883

id_estoque = args.id_estoque
client = mqtt.Client("estoque" + id_estoque)
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_hostname, port)
client.loop_start()

estoque = Estoque(id_estoque, num_pedidos=args.num_pedidos, min_produto=0, max_produto=5, id_fabricas_empurradas=args.id_fabricas_empurradas, id_fabricas_puxadas=args.id_fabricas_puxadas)

while True:
    if client.is_connected():
        if estoque.tem_pedidos_pendentes:
            for id, pedidos in estoque.pedidos_fabricas_puxadas.items():
                printwc(f"Pedido {pedidos[0]}: {estoque.pedidos_atuais[id]}", color="red")

            pedidos_concluidos = estoque.esperar_pedido()
            if pedidos_concluidos:
                for id in pedidos_concluidos:
                    estoque.pedidos_fabricas_puxadas[id][0] += 1
                    if estoque.pedidos_fabricas_puxadas[id][0] <= estoque.num_pedidos:
                        estoque.pedidos_atuais[id] = estoque.pedidos_fabricas_puxadas[id][estoque.pedidos_fabricas_puxadas[id][0]]
                printwc("Pedido chegou!", color="green")
            else:
                estoque.tem_pedidos_pendentes = False

            printwc(f"Produtos em estoque: {estoque.produtos_em_estoque}", color="purple")
            produtosEmEstoque = ",".join(map(str, estoque.produtos_em_estoque))
            result = client.publish("monitor", f"estoque/{estoque.id_estoque}/{produtosEmEstoque}")

    time.sleep(1)