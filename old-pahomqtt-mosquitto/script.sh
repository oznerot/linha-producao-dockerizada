#!/bin/bash

#remove containers antigos
docker compose down
#deleta a imagem anterior
docker rmi pahomqtt
#cria imagem
docker build -t pahomqtt .
#cria containers
docker compose up 