#!/bin/bash
#cria imagem
docker build -t pahomqtt .
#cria containers
docker compose up