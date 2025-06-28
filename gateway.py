import socket
import serjipe_message_pb2
from threading import Thread

devices = []

PORT_CLIENTE = 8000

MULTICAST_GROUP = '239.1.2.3'
PORT_MULTICAST = 5000


# cria um socket com o cliente
def server_cliente():
    # cria um socket tcp
    socker_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # liga o socket
    socker_cliente.bind(('0.0.0.0', PORT_CLIENTE))

    # espera o cliente se conectar
    socker_cliente.listen(1)
    conn, addr = socker_cliente.accept()
    print(f"conexão realizada com {addr[0]}:{addr[1]}")

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            # aqui realizar as respostas devidas pra cada uma das requisições
            conn.sendall(b"ECHO: " + data) # retornar a resposta devida (ainda falta)
    except Exception as e:
        print(f"erro: {e}")
    finally:
        # encerra as conexões
        conn.close()
        socker_cliente.close()
    # termina o processo



# realiza um multicast para verificar dispositivos válidos
# adicionar uma memoria cache e talvez um processe de fazer a chamada multicast de tempos em tempos
def multicast():
    # cria um socket udp
    socket_multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # configura o socket criado
    socket_multicast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)      # permite o reuso
    socket_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)  # tempo de vida

    # liga o socket 
    socket_multicast.bind(('0.0.0.0', PORT_MULTICAST))

    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
    socket_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)



    # cria a mensagem para chamar os MULTICAST
    command = serjipe_message_pb2.Command()
    # o campo parameter se tornou inutil no multicast, porém para sistemas mais avançados pode ser usado
    command.device_id = "gateway-1"
    command.action = "MULTICAST"
    command_bytes = command.SerializeToString()

    # envia as requisições para todos os dispositivos
    socket_multicast.sendto(command_bytes, (MULTICAST_GROUP, PORT_MULTICAST))

    # talvez alterar essa parte pra não voltar no socket multicast, e sim um socket udp
    # vai escutar as respostas, esperando durante 10 segundos
    socket_multicast.settimeout(10.0)
    try:
        while(True):
            # recebe os dados com os d
            data, addr = socket_multicast.recvfrom(1024)
            response = serjipe_message_pb2.DeviceInfo()
            response.ParseFromString(data)
            devices.append(response)

    except socket.timeout:
        print("tempo esgotado")
    except Exception as e:
        print(f"erro: {e}")

    finally:
        # fecha a socket
        socket_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
        socket_multicast.close()

