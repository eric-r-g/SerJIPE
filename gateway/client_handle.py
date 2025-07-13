import socket
import copy
import json
import sys
import serjipe_message_pb2
from config import *

from devices_manager import listar_devices, atualizar_device_data, get_device_info

# função ainda para ser alterada, grpc aqui
def handler_comando(command):
    # melhorar o tratamento de erros e o thread lock

    socket_dispositivo = None
    try:
        socket_dispositivo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_dispositivo.settimeout(3.0)
    except Exception as e:
        print(f"Falha na criação do socket de repassagem: {e}")
        return None, True

    device_info, erro = get_device_info(response.device_id)
    
    if erro:
        print("erro no get_info")
        return None, True

    response = None
    try:
        socket_dispositivo.connect((device_info.ip, device_info.port))

        
        bytes_response = envelope_entrada.SerializeToString()
        socket_dispositivo.settimeout(1.0)
        socket_dispositivo.sendall(bytes_response)
        
        # atualizar para guardas as informações
        envelope_retorno = serjipe_message_pb2.Envelope()

        data = socket_dispositivo.recv(1024)
        envelope_retorno.ParseFromString(data)
        
        if envelope_retorno.HasField("device_data"):
            response = envelope_retorno.device_data

        if response != None:
            atualizar_device_data(response)

    except Exception as e:
        print(f"erro no envio da mensagem: {e}")
        return None, True
    
    finally:
        if socket_dispositivo:
            socket_dispositivo.close()

    return response, False

def requisicoes_cliente():
    while True:
        command = json.loads(sys.stdin.readline())

        mensagem_retorno =  {
            "request_id" : command["request_id"],
            "payload" : {}
        }

        try:
            # se a ação for para listar os dispositivos
            if command["action"] == "LISTAR":    
                retorno, erro = listar_devices()
                if erro:
                    raise ValueError("impossivel de completar ação")

                mensagem_retorno["payload"] = copy.deepcopy(retorno)
            # se for para repassar um comando
            else:
                retorno, erro = handler_comando(command)
                if erro:
                    raise ValueError("impossivel de completar ação")

                mensagem_retorno["payload"] = copy.deepcopy(retorno)

            # envelope_retorno.erro = "SUCESSO" sem questão de erro mais

        except Exception as e:
            print("")
            # envelope_retorno.erro = "FALHA"  sem questão de erro mais

        print(json.dumps(mensagem_retorno, flush=True))

    # termina o processo
