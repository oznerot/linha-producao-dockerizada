import paho.mqtt.client as mqtt 
import time

broker_hostname = "mosquitto"
port = 1883 

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
        client.subscribe("fabrica_almoxarifado")
        client.subscribe("almoxarifado_fornecedor")
        client.subscribe("estoque_fabrica")
        client.subscribe("fabrica_linha")
        client.subscribe("fabrica")
    else:
        print("could not connect, return code:", return_code)

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    print("Received message: " , msg)

client = mqtt.Client("monitor")
# client.username_pw_set(username="user_name", password="password") # uncomment if you use password auth
client.on_connect=on_connect

client.connect(broker_hostname, port)
client.loop_start()

topic = "Test"
msg_count = 0

while msg_count < 100:
    time.sleep(0.1)