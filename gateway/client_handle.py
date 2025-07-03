import socket
import serjipe_message_pb2
from config import *

from devices_manager import listar_devices, atualizar_device_data, get_device_info

def handler_comando(response, envelope_entrada):
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

def server_cliente():
    # criação do socket tcp cliente
    socket_cliente = None
    try:
        socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_cliente.bind(('0.0.0.0', PORT_CLIENTE))
        socket_cliente.listen(1)
    except Exception as e:
        print(f"erro na criação do socket")
        if socket_cliente:
            socket_cliente.close()

    try:
        
        while True:
            # espera o cliente se conectar
            conn = None
            try:
                conn, addr = socket_cliente.accept()
                print(f"conexão realizada com {addr[0]}:{addr[1]}")
                data = conn.recv(1024)

                envelope_entrada = serjipe_message_pb2.Envelope()
                envelope_entrada.ParseFromString(data)
                response = envelope_entrada.command

            except Exception as e:
                print(f"Falha no recebimento no cliente: {e}")
                conn.close()
                continue

            envelope_retorno = serjipe_message_pb2.Envelope()
            try:
                # se a ação for para listar os dispositivos
                if response.action == "LISTAR":    
                    retorno, erro = listar_devices()
                    if erro:
                        raise ValueError("impossivel de completar ação")

                    envelope_retorno.listar_dispositivos.CopyFrom(retorno)
                # se for para repassar um comando
                else:
                    retorno, erro = handler_comando(response, envelope_entrada)
                    if erro:
                        raise ValueError("impossivel de completar ação")

                    envelope_retorno.device_data.CopyFrom(retorno)

                envelope_retorno.erro = "SUCESSO"

            except Exception as e:
                
                envelope_retorno.erro = "FALHA"

            try:
                bytes_envelope = envelope_retorno.SerializeToString()
                conn.sendall(bytes_envelope)
            except Exception as e:
                print(f"falha no envio de mensagem para o cliente: {e}")
            finally:
                if conn:
                    conn.close()

    except Exception as e:
        print(f"erro no socket Cliente: {e}")
    finally:
        # encerra as conexões
        socket_cliente.close()
    # termina o processo
