import grpc
import time
import matplotlib.pyplot as plt
from concurrent import futures

import monitor_pb2
import monitor_pb2_grpc

categorias = ['Produto A', 'Produto B', 'Produto C', 'Produto D', 'Produto E']
valores = [0, 0, 0, 0, 0]

class MonitorServicer(monitor_pb2_grpc.MonitorServiceServicer):
    def ObterValores(self, request_iterator, context):
        for request in request_iterator:
            # Simulando processamento ou lógica para obter valores atualizados
            yield monitor_pb2.ValoresResponse(valores=valores)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    monitor_pb2_grpc.add_MonitorServiceServicer_to_server(MonitorServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started. Listening on port 50051...")
    try:
        while True:
            time.sleep(86400)  # Espera um dia ou pode ser interrompido manualmente
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()