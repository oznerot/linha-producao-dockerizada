import grpc
import time
import argparse
import estoque_pb2
import estoque_pb2_grpc
from print_with_color import print_with_color as printwc

parser = argparse.ArgumentParser(description='Argumentos para execução do estoque.')
parser.add_argument('-i', '--id_estoque', type=str, default="1", help="Define o ID do estoque")
args = parser.parse_args()

grpc_server_address = 'localhost:50051'

class EstoqueCliente:
    def __init__(self, id_estoque):
        self.id_estoque = id_estoque
        self.produtos_em_estoque = [0] * 5

    def check_stock(self):
        with grpc.insecure_channel(grpc_server_address) as channel:
            stub = estoque_pb2_grpc.EstoqueServiceStub(channel)
            response = stub.ConsultarEstoque(estoque_pb2.Empty())
            return response.produtos_em_estoque

    def send_order(self, id_fabrica, produtos):
        with grpc.insecure_channel(grpc_server_address) as channel:
            stub = estoque_pb2_grpc.EstoqueServiceStub(channel)
            pedido = estoque_pb2.Pedido(id_fabrica=id_fabrica, produtos=produtos)
            response = stub.EnviarPedido(pedido)
            return response.success

estoque_cliente = EstoqueCliente(args.id_estoque)

while True:
    produtos_em_estoque = estoque_cliente.check_stock()
    printwc(f"Produtos em estoque: {produtos_em_estoque}", color="purple")
    time.sleep(1)