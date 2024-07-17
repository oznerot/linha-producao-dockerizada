import grpc
import argparse
import time
from fornecedor_pb2 import EnviarPecasRequest
from fornecedor_pb2_grpc import FornecedorServiceStub

from print_with_color import print_with_color as printwc

def enviar_pecas_para_almoxarifado(id_almoxarifado, lista_pecas, id_fabrica=None, id_linha=None, pedido_proprio=False):
    channel = grpc.insecure_channel('localhost:50051')
    stub = FornecedorServiceStub(channel)
    
    request = EnviarPecasRequest(
        lista_pecas=lista_pecas,
        id_almoxarifado=id_almoxarifado,
        id_fabrica=id_fabrica,
        id_linha=id_linha,
        pedido_proprio=pedido_proprio
    )
    
    response = stub.EnviarPecas(request)
    printwc(f"Resposta do servidor: {response.mensagem}", color="cyan")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cliente para enviar peças ao fornecedor via gRPC.')
    parser.add_argument('-a', '--id_almoxarifado', type=str, required=True, help="ID do almoxarifado de destino")
    parser.add_argument('-p', '--lista_pecas', type=str, required=True, help="Lista de peças a enviar, no formato 'peca,quantidade;...'")
    parser.add_argument('-f', '--id_fabrica', type=str, default=None, help="ID da fábrica de origem")
    parser.add_argument('-l', '--id_linha', type=str, default=None, help="ID da linha de produção de origem")
    parser.add_argument('--pedido_proprio', action='store_true', help="Indica se é um pedido próprio (auto)")

    args = parser.parse_args()

    id_almoxarifado = args.id_almoxarifado
    lista_pecas = args.lista_pecas
    id_fabrica = args.id_fabrica
    id_linha = args.id_linha
    pedido_proprio = args.pedido_proprio

    try:
        enviar_pecas_para_almoxarifado(id_almoxarifado, lista_pecas, id_fabrica, id_linha, pedido_proprio)
    except grpc.RpcError as e:
        printwc(f"Erro ao enviar peças: {e}", color="red")