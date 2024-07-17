import grpc
import time
import argparse

import fabrica_pb2
import fabrica_pb2_grpc

from concurrent import futures

class FabricaServicer(fabrica_pb2_grpc.FabricaServiceServicer):

    def __init__(self, id_fabrica, tipo_fabrica, num_linhas):
        self.id_fabrica = id_fabrica
        self.tipo_fabrica = tipo_fabrica
        self.num_linhas = num_linhas

    def EnviarPedidoPecas(self, request, context):
        lista_pedido_pecas = request.itens
        # Implementação da lógica para enviar pedido de peças
        print(f"Recebido pedido de peças da almoxarifado: {lista_pedido_pecas}")
        response = fabrica_pb2.Resposta(status="Pedido de peças recebido pela fábrica")
        return response

    def ReceberPedidoPecas(self, request, context):
        lista_pedido_pecas = request.itens
        # Implementação da lógica para receber pedido de peças
        print(f"Enviando pedido de peças para as linhas de produção: {lista_pedido_pecas}")
        response = fabrica_pb2.Resposta(status="Pedido de peças enviado para produção")
        return response

    def EnviarProdutosEstoque(self, request, context):
        lista_produtos = request.itens
        # Implementação da lógica para enviar produtos para estoque
        print(f"Enviando produtos para o estoque: {lista_produtos}")
        response = fabrica_pb2.Resposta(status="Produtos enviados para o estoque")
        return response

    def EnviarPedidoLinha(self, request, context):
        lista_produtos = request.itens
        # Implementação da lógica para enviar pedido para linha
        print(f"Enviando pedido para linha de produção específica: {lista_produtos}")
        response = fabrica_pb2.Resposta(status="Pedido enviado para linha de produção")
        return response

    def EnviarPedidoLinhaDistribuido(self, request, context):
        lista_produtos = request.itens
        # Implementação da lógica para enviar pedido para linhas distribuído
        print(f"Enviando pedido para todas as linhas de produção: {lista_produtos}")
        response = fabrica_pb2.Resposta(status="Pedido distribuído para todas as linhas")
        return response

def serve():
    parser = argparse.ArgumentParser(description='Argumentos para execução da fábrica gRPC.')
    parser.add_argument('-i', '--id_fabrica', type=str, default="2", help="Define o ID da fábrica")
    parser.add_argument('-n', '--num_linhas', type=int, default=8, help="Define o número de linhas da fábrica")
    parser.add_argument('-t', '--tipo_fabrica', type=str, default="puxada", help="Define o tipo de fábrica (puxada ou empurrada)")
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    fabrica_pb2_grpc.add_FabricaServiceServicer_to_server(
        FabricaServicer(args.id_fabrica, args.tipo_fabrica, args.num_linhas), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print(f'Servidor gRPC da fábrica {args.id_fabrica} iniciado na porta 50052.')
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()

if __name__ == '__main__':
    serve()