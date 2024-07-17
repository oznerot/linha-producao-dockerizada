import grpc
import fabrica_pb2
import fabrica_pb2_grpc

def main():
    channel = grpc.insecure_channel('localhost:50052')
    stub = fabrica_pb2_grpc.FabricaServiceStub(channel)

    # Exemplo de uso do cliente para enviar um pedido de peças
    pedido_pecas = fabrica_pb2.Pedido(itens=[1, 2, 3, 4, 5])
    response = stub.EnviarPedidoPecas(pedido_pecas)
    print('Pedido de peças enviado.')

if __name__ == '__main__':
    main()