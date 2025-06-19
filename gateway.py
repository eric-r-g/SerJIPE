import socket
import serjipe_message_pb2

MULTICAST_GROUP = '239.1.2.3'
PORT = 5000

# cria um socket multcast

devices = []

def multcast():
    # entra no socket multcast
    socket_multcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    socket_multcast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_multcast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1) 

    socket_multcast.bind(('0.0.0.0', PORT))

    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
    socket_multcast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)



    # cria o comando para chamar os MULTCAST
    command = serjipe_message_pb2.Command()
    # o campo parameter se tornou inutil no multicast, porém para sistemas mais avançados se torna importante
    command.device_id = "gateway-1"
    command.action = "MULTICAST"
    command_bytes = command.SerializeToString()

    # envia as requisições para todos os dispositivos
    socket_multcast.sendto(command_bytes, (MULTICAST_GROUP, PORT))

    # vai escutar as respostas, esperando durante 10 segundos
    socket_multcast.settimeout(10.0)
    try:
        while(True):
            # recebe os dados com os d
            data, addr = socket_multcast.recvfrom(1024)
            response = serjipe_message_pb2.DeviceInfo()
            response.ParseFromString(data)
            devices.append(response)

    except socket.timeout:
        print("tempo esgotado")
    except Exception as e:
        print(f"erro: {e}")

    finally:
        # fecha a socket
        socket_multcast.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
        socket_multcast.close()

    # falta agora só escutar

