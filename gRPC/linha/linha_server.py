import grpc
import time
import argparse
from concurrent import futures
from linha_pb2 import *
from linha_pb2_grpc import LinhaServiceServicer, add_LinhaServiceServicer_to_server

from print_with_color import print_with_color as printwc

_ONE_DAY_IN_SECONDS = 86400

class LinhaServicer(LinhaServiceServicer):
    def __init__(self, id_linha, id_fabrica, limiar_pecas):
        self.id_linha = id_linha
        self.id_fabrica = id_fabrica
        self.limiar_pecas = limiar_pecas
        self.buffer_pecas = [1] * 100
        self.status_buffer = "VERMELHO"

    def EnviarPedidoPecas(self, request, context):
        lista_pedido_pecas = request.lista_pedido_pecas
        printwc(f"Enviando pedido de peças: {lista_pedido_pecas}", color="yellow")
        return EnviarPedidoPecasResponse(mensagem=f"Pedido de peças enviado para linha {self.id_linha}, fábrica {self.id_fabrica}")

    def EnviarPedidoProdutos(self, request, context):
        lista_pedido_produtos = request.lista_pedido_produtos
        printwc(f"Enviando produtos: {lista_pedido_produtos}", color="green")
        return EnviarPedidoProdutosResponse(mensagem=f"Produtos enviados para linha {self.id_linha}, fábrica {self.id_fabrica}")

    def MontarPedidoProdutos(self, request, context):
        lista_pedido_produtos = request.lista_pedido_produtos
        printwc(f"Montando pedido de produtos: {lista_pedido_produtos}", color="red")
        return MontarPedidoProdutosResponse(mensagem=f"Pedido de produtos montado para linha {self.id_linha}, fábrica {self.id_fabrica}")

    def PedirPecas(self, request, context):
        lista_pedido_pecas = request.lista_pedido_pecas
        printwc(f"Pedindo peças ao almoxarifado: {lista_pedido_pecas}", color="yellow")
        return PedirPecasResponse(mensagem=f"Pedido de peças feito para almoxarifado pela linha {self.id_linha}, fábrica {self.id_fabrica}")

    def ReceberPecas(self, request, context):
        lista_pecas_recebidas = request.lista_pecas_recebidas
        printwc(f"Recebendo peças: {lista_pecas_recebidas}", color="yellow")
        return ReceberPecasResponse(mensagem=f"Peças recebidas pela linha {self.id_linha}, fábrica {self.id_fabrica}")

    def ChecarEstoquePecas(self, request, context):
        status = "VERDE"
        for quantidade in self.buffer_pecas:
            if quantidade < self.limiar_pecas:
                status = "VERMELHO"
                break
            elif quantidade < self.limiar_pecas + self.limiar_pecas // 2:
                status = "AMARELO"

        self.status_buffer = status

        if self.status_buffer == "VERMELHO":
            printwc("Estoque com nível crítico [VERMELHO].", color="red")
            return ChecarEstoquePecasResponse(status_buffer=self.status_buffer, mensagem=f"Estoque com nível crítico [VERMELHO] para linha {self.id_linha}, fábrica {self.id_fabrica}")
        elif self.status_buffer == "AMARELO":
            printwc("Estoque com nível baixo [AMARELO].", color="yellow")
            return ChecarEstoquePecasResponse(status_buffer=self.status_buffer, mensagem=f"Estoque com nível baixo [AMARELO] para linha {self.id_linha}, fábrica {self.id_fabrica}")
        else:
            printwc("Estoque com nível bom [VERDE].", color="green")
            return ChecarEstoquePecasResponse(status_buffer=self.status_buffer, mensagem=f"Estoque com nível bom [VERDE] para linha {self.id_linha}, fábrica {self.id_fabrica}")

def serve():
    parser = argparse.ArgumentParser(description='Argumentos para execução da linha.')
    parser.add_argument('-i', '--id_linha', type=str, default="0", help="Define o ID da linha")
    parser.add_argument('-f', '--id_fabrica', type=str, default="2", help="Define o ID da fábrica que a linha pertence")
    parser.add_argument('-l', '--limiar_pecas', type=int, default="20", help="Define o limiar de peças do nível vermelho")
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_LinhaServiceServicer_to_server(LinhaServicer(args.id_linha, args.id_fabrica, args.limiar_pecas), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    printwc("Servidor Linha gRPC iniciado. Escutando na porta 50052.", color="purple")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()