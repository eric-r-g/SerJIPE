import socket
import serjipe_message_pb2
from threading import Thread


devices_dict = {}

MULTICAST_GROUP = '239.1.2.3'
PORT_MULTICAST = 5000
PORT_MULTICAST_RESPOSTA = 4444
PORT_CLIENTE = 8000

# realiza um multicast para verificar dispositivos válidos
# adicionar uma memoria cache e talvez um processe de fazer a chamada multicast de tempos em tempos

def get_local_ip():
    try:
        # Cria um socket temporário para conectar a um servidor externo
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Conecta ao DNS do Google
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return f"Erro: {e}"

def multicast_envio():
    # cria um socket udp
    socket_multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # configura o socket criado
    socket_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)  # tempo de vida

    # se conecta ao grupo multicast
    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
    socket_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # cria a mensagem para chamar os MULTICAST
    command = serjipe_message_pb2.DeviceInfo()
    command.device_id = "GATEWAY"
    command.type = "GATEWAY"
    command.ip = ip_maquina
    command.port = PORT_MULTICAST_RESPOSTA
    command.status = "ON"
    command_bytes = command.SerializeToString()

    # envia as requisições para todos os dispositivos
    socket_multicast.sendto(command_bytes, (MULTICAST_GROUP, PORT_MULTICAST))

    # fecha socket de envio
    socket_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
    socket_multicast.close()

    return multicast_retorno()

def multicast_retorno():
    devices = []
    # cria socket de entrada
    socket_multicast_respostas = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    socket_multicast_respostas.bind(('0.0.0.0', PORT_MULTICAST_RESPOSTA))

    # vai escutar as respostas, esperando durante 3 segundos
    socket_multicast_respostas.settimeout(3)

    try:
        while(True):
            # recebe os dados com os d
            data, addr = socket_multicast_respostas.recvfrom(1024)
            response = serjipe_message_pb2.DeviceInfo()
            response.ParseFromString(data)
            d = {}
            d["device_id"] = response.device_id
            d["type"] = response.type
            d["ip"] = response.ip
            d["port"] = response.port
            d["status"] = response.status

            devices.append(d)

    except socket.timeout:
        print("tempo esgotado")
    except Exception as e:
        print(f"erro: {e}")

    finally:
        # fecha a socket de entrada
        socket_multicast_respostas.close()
        return devices

# cria um socket com o cliente
def server_cliente():
    # cria um socket tcp
    socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # liga o socket
    socket_cliente.bind(('0.0.0.0', PORT_CLIENTE))

    try:
        socket_cliente.listen(1)
        while True:
            # espera o cliente se conectar
            conn, addr = socket_cliente.accept()
            print(f"conexão realizada com {addr[0]}:{addr[1]}")
            try:
                data = conn.recv(1024)
                if not data:
                    # evita travamento
                    conn.close()
                    continue
                response = serjipe_message_pb2.Command()
                response.ParseFromString(data)
                match response.action:

                    case "LISTAR":
                        devices = multicast_envio()
                        retorno = serjipe_message_pb2.ListarDispositivos()
                        
                        # limpa o dicionario para não acumular
                        devices_dict.clear()

                        for d in devices:
                            # ajeita a mensagem de retorno
                            device = retorno.devices.add()
                            device.device_id = d["device_id"]
                            device.type = d["type"]
                            device.ip = d["ip"]
                            device.port = d["port"]
                            device.status = d["status"]

                            # ajeita o dicionario com os dispositivos
                            devices_dict[d["device_id"]] = d.copy()

                        bytes = retorno.SerializeToString()
                        conn.sendall(bytes)

                    case "LIGAR":
                        socket_dispositivo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        socket_dispositivo.timeout(3)
                        # falta tratamento de erro

                        ip = devices_dict[response.device_id]["ip"]
                        porta = devices_dict[response.device_id]["port"]
                        
                        try:
                            socket_dispositivo.connect((ip, porta))

                            bytes_response = response.SerializeToString()
                            socket_dispositivo.sendall(bytes_response)
                            # retornar uma resposta para o cliente
                        except:
                            print("erro")
                        finally:
                            socket_dispositivo.close()
                    case _:
                        print("comando invalido")
            finally:
                conn.close()
    except Exception as e:
        print(f"erro: {e}")
    finally:
        # encerra as conexões
        socket_cliente.close()
    # termina o processo

try:#
    ip_maquina = get_local_ip()
except Exception as e:
    print(f"erro: {e}")

server_cliente()
