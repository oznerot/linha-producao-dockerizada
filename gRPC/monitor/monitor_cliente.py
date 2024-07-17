import grpc
import time
import matplotlib.pyplot as plt

import monitor_pb2
import monitor_pb2_grpc

categorias = ['Produto A', 'Produto B', 'Produto C', 'Produto D', 'Produto E']
valores = [0, 0, 0, 0, 0]

def update_bar_chart():
    plt.clf()
    plt.bar(categorias, valores)
    plt.xlabel('Produtos')
    plt.ylabel('Quantidade')
    plt.title('Gráfico de Barras')
    plt.draw()
    plt.pause(0.001)

def plotar_grafico():
    channel = grpc.insecure_channel('localhost:50051')
    stub = monitor_pb2_grpc.MonitorServiceStub(channel)
    try:
        for response in stub.ObterValores(monitor_pb2.ValoresRequest()):
            global valores
            valores = response.valores
            update_bar_chart()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    plt.ion()
    plotar_grafico()