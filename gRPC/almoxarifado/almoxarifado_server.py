import grpc
import time
import random
import argparse

import almoxarifado_pb2
import almoxarifado_pb2_grpc

from concurrent import futures

class AlmoxarifadoServicer(almoxarifado_pb2_grpc.AlmoxarifadoServiceServicer):
    def __init__(self, id_almoxarifado, limiar_estoque_pecas):
        self.id_almoxarifado = id_almoxarifado
        self.estoque_pecas = [1] * 100  # Exemplo inicial de estoque
        self.limiar_estoque_pecas = limiar_estoque_pecas
        self.status_estoque_pecas = "VERMELHO"
        self.fornecedor_channel = grpc.insecure_channel('localhost:50052')  # Canal para o serviço do fornecedor

    def MontarPedidoPecas(self, request, context):
        lista_pedido_pecas = request.pecas
        pedido_completo = True
        pecas_consumidas = [0] * 100
        pecas_faltantes = [0] * 100

        for peca, quantidade in enumerate(lista_pedido_pecas):
            if self.estoque_pecas[peca] >= quantidade:
                pecas_consumidas[peca] = quantidade
            else:
                pedido_completo = False
                pecas_faltantes[peca] = quantidade - self.estoque_pecas[peca]
    
        if pedido_completo:
            for peca, quantidade in enumerate(pecas_consumidas):
                self.estoque_pecas[peca] -= quantidade
            print(f'Pedido de peças montado para almoxarifado {self.id_almoxarifado}.')
        else:
            print(f'Faltam peças no estoque para montar o pedido para almoxarifado {self.id_almoxarifado}.')
            self.PedirPecas(pecas_faltantes, context)

        return almoxarifado_pb2.StatusPedido(status="Pedido de peças processado.")

    def PedirPecas(self, lista_pedido_pecas, context):
        stub = almoxarifado_pb2_grpc.FornecedorServiceStub(self.fornecedor_channel)
        request = almoxarifado_pb2.PedidoPecas(pecas=lista_pedido_pecas)
        response = stub.PedirPecasFornecedor(request)
        print(f"Pedido de peças enviado ao fornecedor para almoxarifado {self.id_almoxarifado}. Status: {response.status}")

    def ReceberPecas(self, request, context):
        lista_pecas = request.pecas
        for peca, quantidade in enumerate(lista_pecas):
            self.estoque_pecas[peca] += quantidade
        print(f'Peças recebidas pelo almoxarifado {self.id_almoxarifado}.')
        return almoxarifado_pb2.StatusPedido(status="Peças recebidas.")

    def ChecarEstoquePecas(self, request, context):
        status = "VERDE"
        for quantidade in self.estoque_pecas:
            if quantidade < self.limiar_estoque_pecas:
                status = "VERMELHO"
                break
        self.status_estoque_pecas = status

        if self.status_estoque_pecas == "VERMELHO":
            print(f"Estoque crítico (VERMELHO) para almoxarifado {self.id_almoxarifado}.")
            self.PedirPecas([self.limiar_estoque_pecas] * 100, context)
        else:
            print(f"Estoque normal (VERDE) para almoxarifado {self.id_almoxarifado}.")

        return almoxarifado_pb2.StatusEstoque(status=self.status_estoque_pecas)

def serve():
    parser = argparse.ArgumentParser(description='Argumentos para execução do almoxarifado gRPC.')
    parser.add_argument('-i', '--id_almoxarifado', type=str, default="1", help="Define o ID do almoxarifado")
    parser.add_argument('-l', '--limiar_estoque_pecas', type=int, default="20", help="Define o limiar de peças do nível vermelho")
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    almoxarifado_pb2_grpc.add_AlmoxarifadoServiceServicer_to_server(
        AlmoxarifadoServicer(args.id_almoxarifado, args.limiar_estoque_pecas), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print(f'Servidor gRPC do almoxarifado {args.id_almoxarifado} iniciado na porta 50051.')
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()