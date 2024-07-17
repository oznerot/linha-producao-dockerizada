import grpc
from concurrent import futures
import time
import argparse
import random
import estoque_pb2
import estoque_pb2_grpc

class Estoque(estoque_pb2_grpc.EstoqueServiceServicer):
    def __init__(self, id_estoque, num_pedidos=5, min_produto=0, max_produto=10):
        self.id_estoque = id_estoque
        self.produtos_em_estoque = [0] * 5
        self.num_pedidos = num_pedidos
        self.pedidos_fabricas_puxadas = {2: [[random.randint(min_produto, max_produto) for _ in range(5)] for _ in range(num_pedidos + 1)]}
        self.pedidos_atuais = {2: self.pedidos_fabricas_puxadas[2][1]}
        self.tem_pedidos_pendentes = True

    def ConsultarEstoque(self, request, context):
        return estoque_pb2.EstoquePecas(pecas=self.produtos_em_estoque)

    def EnviarPedido(self, request, context):
        id_fabrica = request.id_fabrica
        produtos_pedido = request.produtos

        if id_fabrica in self.pedidos_fabricas_puxadas:
            for produto, quantidade in enumerate(produtos_pedido):
                self.pedidos_atuais[id_fabrica][produto] -= quantidade
                self.produtos_em_estoque[produto] += quantidade
            return estoque_pb2.RespostaPedido(success=True)
        else:
            return estoque_pb2.RespostaPedido(success=False)

def serve():
    parser = argparse.ArgumentParser(description='Argumentos para execução do estoque.')
    parser.add_argument('-i', '--id_estoque', type=str, default="1", help="Define o ID do estoque")
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    estoque_service = Estoque(args.id_estoque)  # Passando o id_estoque ao criar uma instância de Estoque
    estoque_pb2_grpc.add_EstoqueServiceServicer_to_server(estoque_service, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print(f"Servidor de Estoque iniciado na porta 50051 com ID {args.id_estoque}...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()