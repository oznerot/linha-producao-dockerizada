import grpc
import time
import argparse
from concurrent import futures
from fornecedor_pb2 import EnviarPecasRequest, EnviarPecasResponse
from fornecedor_pb2_grpc import FornecedorServiceServicer, add_FornecedorServiceServicer_to_server

from print_with_color import print_with_color as printwc

_ONE_DAY_IN_SECONDS = 86400

class FornecedorServicer(FornecedorServiceServicer):
    def EnviarPecas(self, request, context):
        printwc("Enviando peças para o almoxarifado.", color="yellow")
        lista_pecas = self.converter_lista(request.lista_pecas)
        
        if request.pedido_proprio:
            mensagem = f"Fornecedor {id_fornecedor} enviou peças para almoxarifado {request.id_almoxarifado} (auto): {lista_pecas}"
        else:
            mensagem = f"Fornecedor {id_fornecedor} enviou peças para almoxarifado {request.id_almoxarifado}, fabrica {request.id_fabrica}, linha {request.id_linha}: {lista_pecas}"

        return EnviarPecasResponse(mensagem=mensagem)

    def converter_lista(self, lista1):
        lista2 = lista1.split(";")
        lista3 = []
        for pedido_produto in lista2:
            lista3.append(pedido_produto.split(","))
        lista4 = [0] * len(lista3)
        for indice, quantidade in lista3:
            lista4[int(indice)] = int(quantidade)
        return lista4

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_FornecedorServiceServicer_to_server(FornecedorServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    printwc("Servidor Fornecedor gRPC iniciado. Escutando na porta 50051.", color="purple")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Argumentos para execução do fornecedor.')
    parser.add_argument('-i', '--id_fornecedor', type=str, default="1", help="Define o ID do fornecedor")
    args = parser.parse_args()

    id_fornecedor = args.id_fornecedor

    serve()