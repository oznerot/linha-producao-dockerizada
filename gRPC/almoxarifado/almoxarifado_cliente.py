import grpc
import almoxarifado_pb2
import almoxarifado_pb2_grpc

def main():
    channel = grpc.insecure_channel('localhost:50051')
    stub = almoxarifado_pb2_grpc.AlmoxarifadoServiceStub(channel)

    # Exemplo de uso do cliente para montar um pedido de peças
    pedido_pecas = almoxarifado_pb2.PedidoPecas(pecas=[1, 2, 3, 4, 5])
    response = stub.MontarPedidoPecas(pedido_pecas)
    print('Pedido de peças enviado.')

if __name__ == '__main__':
    main()