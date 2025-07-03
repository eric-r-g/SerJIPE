# SerJIPE

Trabalho de distribuição de processos e dados, voltado para a criação de um modelo de uma cidade inteligente com múltiplos dispositivos que funciona em uma rede local

## Índice

- [Sobre](#sobre)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
- [Licença](#licença)

## Sobre

Este projeto é um sistema distribuído para gerenciamento de sensores em uma rede local, utilizando multicast UDP para descoberta de dispositivos, comunicação via TCP e mensagens serializadas com Protocol Buffers.

## Funcionalidades

- Descoberta de dispositivos via multicast
- Recebimento de dados de sensores via UDP
- Comunicação cliente-servidor via TCP
- Serialização de mensagens com Protocol Buffers
- Armazenamento e exibição dos dispositivos conectados

## Requisitos

- Python 3.10+
- `protobuf`
- Sistemas compatíveis com sockets (Linux recomendado)

```bash
pip install protobuf
```
## Licença

MIT License

Copyright (c) 2025 Eric Gomes, Paulo Marinho, 

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
