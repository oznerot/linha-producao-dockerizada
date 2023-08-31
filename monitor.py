import paho.mqtt.client as mqtt 
import time
import matplotlib.pyplot as plt

broker_hostname = "mosquitto"
port = 1883 

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
        client.subscribe("monitor")
    else:
        print("could not connect, return code:", return_code)

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    command = msg.split("/")
    if(command[0] == "estoque"):
        valores = command[2].split(',')
    print("Received message: " , msg)


client = mqtt.Client("monitor")
# client.username_pw_set(username="user_name", password="password") # uncomment if you use password auth
client.on_connect=on_connect

client.connect(broker_hostname, port)
client.loop_start()

topic = "Test"
msg_count = 0

categorias = []
for i in range(0, 5):
    categorias.append(0)
valores = []

while True:
    # Criar o gráfico de barras
    print("a")
    if(len(valores) > 0):
        plt.bar(categorias, valores)

        # Adicionar rótulos e título
        plt.xlabel('produtos')
        plt.ylabel('quantidade')
        plt.title('Gráfico de Barras')

        # Exibir o gráfico
        plt.show(block = False)
    time.sleep(0.5)