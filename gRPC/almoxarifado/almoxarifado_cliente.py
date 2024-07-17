import grpc
import almoxarifado_pb2 as almoxarifado__pb2


class AlmoxarifadoServiceStub(object):
    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel to use for remote communication.
        """
        self.MontarPedidoPecas = channel.unary_unary(
            '/almoxarifado.AlmoxarifadoService/MontarPedidoPecas',
            request_serializer=almoxarifado__pb2.PedidoPecas.SerializeToString,
            response_deserializer=almoxarifado__pb2.Empty.FromString,
        )


def main():
    channel = grpc.insecure_channel('localhost:50051')
    stub = AlmoxarifadoServiceStub(channel)

    # Exemplo de uso do cliente para montar um pedido de peças
    pedido_pecas = almoxarifado_pb2.PedidoPecas(pecas=[1, 2, 3, 4, 5])
    response = stub.MontarPedidoPecas(pedido_pecas)
    print('Pedido de peças enviado.')

if __name__ == '__main__':
    main()