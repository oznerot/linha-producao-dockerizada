# Use a imagem base do Python 3
FROM python:3

# Atualizar pip e instalar as dependências principais
RUN pip install --upgrade pip
RUN pip install grpcio grpcio-tools protobuf matplotlib

# Definir o diretório de trabalho no contêiner
WORKDIR /app

# Copiar os arquivos necessários para o contêiner
ARG SERVICE_NAME
COPY print_with_color.py /app/print_with_color.py
COPY ${SERVICE_NAME}/${SERVICE_NAME}.proto /app/${SERVICE_NAME}.proto
COPY ${SERVICE_NAME}/${SERVICE_NAME}_server.py /app/${SERVICE_NAME}_server.py
COPY ${SERVICE_NAME}/${SERVICE_NAME}_cliente.py /app/${SERVICE_NAME}_client.py

# Gerar o código Python a partir do arquivo .proto
RUN python -m grpc_tools.protoc -I/app --python_out=/app --grpc_python_out=/app /app/${SERVICE_NAME}.proto

# Expor a porta gRPC utilizada pelo serviço
EXPOSE 50051

# Comando de entrada padrão para iniciar o servidor
CMD ["python", "/app/${SERVICE_NAME}_server.py"]