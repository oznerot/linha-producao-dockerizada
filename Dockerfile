FROM python:3

RUN pip install paho-mqtt

COPY ./print_with_color.py /print_with_color.py
COPY ./estoque_teste.py /estoque_teste.py
#COPY ./fabrica_teste1.py /fabrica_teste1.py
COPY ./fabrica_teste2 /fabrica_teste2.py
COPY ./linha_teste.py /linha_teste.py
COPY ./almoxarifado_teste.py /almoxarifado_teste.py
COPY ./fornecedor_teste.py /fornecedor_teste.py