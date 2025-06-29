import socket
import serjipe_message_pb2
import threading


devices_dict = {}
sensor_dict = {}

MULTICAST_GROUP = '239.1.2.3'
PORT_MULTICAST = 5000
PORT_MULTICAST_RESPOSTA = 4444
PORT_CLIENTE = 8000
PORT_UDP_SENSOR = 7000

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
    discover = serjipe_message_pb2.Discover()
    discover.ip = ip_maquina
    discover.port_multicast = PORT_MULTICAST_RESPOSTA
    discover.port_udp_sensor = PORT_UDP_SENSOR
    discover_bytes = discover.SerializeToString()

    # envia as requisições para todos os dispositivos
    socket_multicast.sendto(discover_bytes, (MULTICAST_GROUP, PORT_MULTICAST))

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
    socket_multicast_respostas.settimeout(3.0)

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
            d["data"] = {
                "device_id" : response.data.device_id,
                "status" : response.data.status,
                "value_name" : response.data.value_name,
                "value" : response.data.value,
                "timestamp" : response.data.timestamp
            }

            devices.append(d)

    except socket.timeout:
        print("tempo esgotado")
    except Exception as e:
        print(f"erro: {e}")

    finally:
        # fecha a socket de entrada
        socket_multicast_respostas.close()
        return devices


def socket_udp_sensor():
    socket_udp_sensor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_udp_sensor.bind(('0.0.0.0', PORT_UDP_SENSOR))

    socket_udp_sensor.settimeout(1.0)

    try:
        while True:
            try:
                data, addr = socket_udp_sensor.recvfrom(1024)
                response = serjipe_message_pb2.DeviceData()
                response.ParseFromString(data)

                d = {
                    "status" : response.status,
                    "value_name" : list(response.value_name),
                    "value" : list(response.value),
                    "timestamp" : response.timestamp
                }

                sensor_dict[response.device_id] = d
            except socket.timeout:
                continue

    except Exception as e:
        print(f"Erro: {e}")


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
                    
                    # listar todos os dispositivos
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
                            device.data.device_id = d["data"]["device_id"]
                            device.data.status = d["data"]["status"]
                            device.data.value_name.extend(d["data"]["value_name"])
                            device.data.value.extend(d["data"]["value"])
                            device.data.timestamp = d["data"]["timestamp"]
                            # ajeita o dicionario com os dispositivos
                            devices_dict[d["device_id"]] = d.copy()

                        bytes = retorno.SerializeToString()
                        conn.sendall(bytes)
                    
                    # repassar um comando
                    case _:
                        socket_dispositivo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        socket_dispositivo.settimeout(3.0)
                        # falta tratamento de erro

                        if response.device_id in devices_dict:
                            ip = devices_dict[response.device_id]["ip"]
                            porta = devices_dict[response.device_id]["port"]
                        else:
                            print("erro")
                        
                        try:
                            socket_dispositivo.connect((ip, porta))

                            bytes_response = response.SerializeToString()
                            socket_dispositivo.settimeout(1.0)
                            socket_dispositivo.sendall(bytes_response)
                            
                            
                            data = socket_dispositivo.recv(1024)
                            conn.sendall(data)
                        except:
                            print("erro")
                        finally:
                            socket_dispositivo.close()
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

thread_udp_sensor = threading.Thread(
    target=socket_udp_sensor,
    daemon=True
)
thread_udp_sensor.start()
server_cliente()
