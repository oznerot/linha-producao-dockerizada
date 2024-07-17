import paho.mqtt.client as mqtt
import time
import matplotlib.pyplot as plt

broker_hostname = "mosquitto"
port = 1883

categorias = ['Produto A', 'Produto B', 'Produto C', 'Produto D', 'Produto E']
valores = [0, 0, 0, 0, 0]

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("Connected to MQTT broker")
        client.subscribe("monitor")
    else:
        print("Could not connect to MQTT broker, return code:", return_code)

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    command = msg.split("/")
    if command[0] == "estoque":
        valores = list(map(int, command[2].split(',')))
        update_bar_chart()

def update_bar_chart():
    plt.clf()  # Limpa a figura atual para evitar sobreposição de barras
    plt.bar(categorias, valores)
    plt.xlabel('Produtos')
    plt.ylabel('Quantidade')
    plt.title('Gráfico de Barras')
    plt.draw()
    plt.pause(0.001)  # Aguarda um pequeno tempo para atualização gráfica

client = mqtt.Client("monitor")
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_hostname, port)
client.loop_start()

plt.ion()  # Ativa o modo interativo do matplotlib

try:
    while True:
        time.sleep(1)  # Pode ajustar o intervalo de atualização conforme necessário
except KeyboardInterrupt:
    print("Interrupted, closing...")
    client.disconnect()
    plt.ioff()
    plt.close()