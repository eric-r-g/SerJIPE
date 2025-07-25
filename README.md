# SerJIPE

Trabalho de distribuição de processos e dados, voltado para a criação de um modelo de uma cidade inteligente que funciona em uma rede local.

## Índice

- [Sobre](#sobre)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação e uso](#instalação-e-uso)
- [Licença](#licença)

## Sobre

Este projeto é um sistema distribuído para gerenciamento de sensores em uma rede local, utilizando multicast UDP para descoberta de dispositivos, com comunicação via grpc e RabbitMQ, além de uma arquitetura webservices para comunicação entre cliente e gateway.

## Funcionalidades

- Descoberta de dispositivos via multicast
- Recebimento de dados de sensores via RabbitMQ
- Comunicação cliente-gateway via WebServices
- Armazenamento e exibição dos dispositivos conectados

## Requisitos

- Python 3.10+
- `protobuf` para o grpc
- NodeJS
- RabbitMQ

## Instalação e uso

### Gateway

Entre na pasta /gateway, instale os pacotes do nodejs:

```bash
npm install
```

Agora rode o servidor com:

```bash
npm run start
```

### Dispositivos

Entre na pasta /dispositivos, instale a biblioteca para o uso do Protocol Buffers no python:

```bash
pip install protobuf
```

Instale a biblioteca para o uso do Protocol JSON no python:

```bash
pip install pika
```

Instale a biblioteca para o uso do Protocol GRPC no python:

```bash
pip install grpc
```

Agora rode um dos dispositivos com:

```bash
python nome_do_dispositivo.py
```

Opcionalmente, os dispositivos podem ser iniciados em outra máquina da rede interna, no zip entregue com a atividade temos um setup de máquina virtual pronta "alpine01.ova". Esse setup tem um ambiente virtual em ~/venv que pode já tem os scripts dos dispositivos.

### Cliente

Depois de iniciar o servidor do gateway, o cliente estará sendo hosteado no endereço que o servidor informar: <http://localhost:8003>

## Licença

MIT License

Copyright (c) 2025 Eric Gomes, Paulo Marinho, João Ítalo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
