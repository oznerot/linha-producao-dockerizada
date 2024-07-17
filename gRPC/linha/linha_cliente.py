import grpc
import argparse
from linha_pb2 import *
from linha_pb2_grpc import LinhaServiceStub

from print_with_color import print_with_color as printwc

def enviar_pedido_pecas(id_fabrica, id_linha, lista_pedido_pecas):
    channel = grpc.insecure_channel('localhost:50052')
    stub = LinhaServiceStub(channel)
    
    request = EnviarPedidoPecasRequest(
        lista_pedido_pecas=lista_pedido_pecas,
        id_fabrica=id_fabrica,
        id_linha=id_linha
    )
    
    response = stub.EnviarPedidoPecas(request)
    printwc(f"Resposta do servidor: {response.mensagem}", color="cyan")

def enviar_pedido_produtos(id_fabrica, id_linha, lista_pedido_produtos):
    channel = grpc.insecure_channel('localhost:50052')
    stub = LinhaServiceStub(channel)
    
    request = EnviarPedidoProdutosRequest(
        lista_pedido_produtos=lista_pedido_produtos,
        id_fabrica=id_fabrica,
        id_linha=id_linha
    )
    
    response = stub.EnviarPedidoProdutos(request)
    printwc(f"Resposta do servidor: {response.mensagem}", color="cyan")

def montar_pedido_produtos(id_fabrica, id_linha, lista_pedido_produtos):
    channel = grpc.insecure_channel('localhost:50052')
    stub = LinhaServiceStub(channel)
    
    request = MontarPedidoProdutosRequest(
        lista_pedido_produtos=lista_pedido_produtos,
        id_fabrica=id_fabrica,
        id_linha=id_linha
    )
    
    response = stub.MontarPedidoProdutos(request)
    printwc(f"Resposta do servidor: {response.mensagem}", color="cyan")

def pedir_pecas(id_fabrica, id_linha, lista_pedido_pecas):
    channel = grpc.insecure_channel('localhost:50052')
    stub = LinhaServiceStub(channel)
    
    request = PedirPecasRequest(
        lista_pedido_pecas=lista_pedido_pecas,
        id_fabrica=id_fabrica,
        id_linha=id_linha
    )
    
    response = stub.PedirPecas(request)
    printwc(f"Resposta do servidor: {response.mensagem}", color="cyan")

def receber_pecas(id_fabrica, id_linha, lista_pecas_recebidas):
    channel = grpc.insecure_channel('localhost:50052')
    stub = LinhaServiceStub(channel)
    
    request = ReceberPecasRequest(
        lista_pecas_recebidas=lista_pecas_recebidas,
        id_fabrica=id_fabrica,
        id_linha=id_linha
    )
    
    response = stub.ReceberPecas(request)
    printwc(f"Resposta do servidor: {response.mensagem}", color="cyan")

def checar_estoque_pecas(id_fabrica, id_linha):
    channel = grpc.insecure_channel('localhost:50052')
    stub = LinhaServiceStub(channel)
    
    request = ChecarEstoquePecasRequest(
        id_fabrica=id_fabrica,
        id_linha=id_linha
    )
    
    response = stub.ChecarEstoquePecas(request)
    printwc(f"Resposta do servidor: {response.mensagem}", color="cyan")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cliente para linha via gRPC.')
    parser.add_argument('-i', '--id_linha', type=str, default="0", help="Define o ID da linha")
    parser.add_argument('-f', '--id_fabrica', type=str, default="2", help="Define o ID da fábrica que a linha pertence")
    args = parser.parse_args()

    try:
        # Exemplo de chamadas aos métodos gRPC
        enviar_pedido_pecas(args.id_fabrica, args.id_linha, "0,10;1,20;2,30")
        enviar_pedido_produtos(args.id_fabrica, args.id_linha, "produto1,5;produto2,10")
        montar_pedido_produtos(args.id_fabrica, args.id_linha, "produto1,5;produto2,10")
        pedir_pecas(args.id_fabrica, args.id_linha, "0,10;1,20;2,30")
        receber_pecas(args.id_fabrica, args.id_linha, [10, 20, 30])
        checar_estoque_pecas(args.id_fabrica, args.id_linha)
    except grpc.RpcError as e:
        printwc(f"Erro ao executar operação gRPC: {e}", color="red")