#Linha
import paho.mqtt.client as mqtt 
import time  

npecas = 10
produto1 = [0,1,2,3,4,5,8,9]
pecasNaLinha = [1,1,1,1,1,1,1,1,1,1]
nlinha = 0
def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
        client.subscribe("fabrica")
    else:
        print("could not connect, return code:", return_code)

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    print("Received message: " ,msg)
    comando = msg.split("/")
    if(comando[0] == "fabrica" and comando[1] == str(nlinha)):
        pecas = comando[2].split(",")
        #pecasRecebidas = []
        for i in range(len(pecas)):
            peca = int(pecas[i])
            pecasNaLinha[peca] += 1

def pedirpecas(pecas):
    pedido = ""
    for i in range (len(pecas)):
        pedido = pedido + str(pecas[i])
        if(i < len(pecas) - 1):
            pedido = pedido + ","
    result = client.publish("fabrica", "linha/" + str(nlinha) + "/" + pedido)
    #print(pedido)

def montarproduto(produto):
    contador = 0
    pecas_faltantes = []
    pecas_consumidas = []
    if(produto == 1):
        numero_pecas_produto = len(produto1)
        for i in range (numero_pecas_produto):
            if(pecasNaLinha[produto1[i]] > 0):
                pecas_consumidas.append(produto1[i])
            else:
                contador+= 1
                pecas_faltantes.append(produto1[i])
    if(contador == 0):
        for i in range (len(pecas_consumidas)):
            pecasNaLinha[pecas_consumidas[i]] -= 1
        return True
    else:
        #print(pecas_faltantes)
        #print(pecasNaLinha)
        pedirpecas(pecas_faltantes)
        return False    


def montarpedido(pedido):
    montou = montarproduto(pedido)
    return montou


broker_hostname ="localhost"
port = 1883 
nlinha = input("escreva o numero da linha")
client = mqtt.Client("linha" + nlinha)
# client.username_pw_set(username="user_name", password="password") # uncomment if you use password auth
client.on_connect=on_connect
client.on_message=on_message

client.connect(broker_hostname, port) 
client.loop_start()

pedidos = [1,1,1,1]
npedidos = 4
pedidoatual = 0
do = True

while(do):
    if(client.is_connected()):
        if(npedidos - pedidoatual > 0):
            #print(pedidos[pedidoatual])
            print("montando pedido: " + str(pedidoatual))
            if(montarpedido(pedidos[pedidoatual])):
                pedidoatual += 1
                print("pedido montado")

            time.sleep(1)