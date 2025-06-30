import socket
import serjipe_message_pb2
import threading
import time

devices_dict = {}
devices = []
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

    # envelopar a mensagem
    envelope = serjipe_message_pb2.Envelope()
    envelope.discover.CopyFrom(discover)
    envelope.erro = "sucesso"

    bytes_envelope = envelope.SerializeToString()

    # envia as requisições para todos os dispositivos
    socket_multicast.sendto(bytes_envelope, (MULTICAST_GROUP, PORT_MULTICAST))

    # fecha socket de envio
    socket_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
    socket_multicast.close()
    multicast_retorno()


def multicast_retorno():
    devices.clear() 
    # cria socket de entrada
    socket_multicast_respostas = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    socket_multicast_respostas.bind(('0.0.0.0', PORT_MULTICAST_RESPOSTA))

    # vai escutar as respostas, esperando durante 3 segundos
    socket_multicast_respostas.settimeout(3.0)

    try:
        while(True):
            data, addr = socket_multicast_respostas.recvfrom(1024)
            envelope_entrada = serjipe_message_pb2.DeviceInfo()
            envelope_entrada.ParseFromString(data)
            
            if envelope_entrada.HasField("device_info"):
                response = envelope_entrada.device_info

            dispositivo = {}
            dispositivo["device_id"] = response.device_id
            dispositivo["type"] = response.type
            dispositivo["ip"] = response.ip
            dispositivo["port"] = response.port
            dispositivo["data"] = {
                "device_id" : response.data.device_id,
                "status" : response.data.status,
                "value_name" : response.data.value_name,
                "value" : response.data.value,
                "timestamp" : response.data.timestamp
            }

            devices.append(dispositivo)

            devices_dict[response.device_id] = {}
            devices_dict[response.device_id]["ip"] = response.ip
            devices_dict[response.device_id]["port"] = response.port

    except socket.timeout:
        print("tempo esgotado")
    except Exception as e:
        print(f"erro: {e}")

    finally:
        # fecha a socket de entrada
        socket_multicast_respostas.close()

# cria a função que vai fazer o multicast periodicamente
def multicast_periodico():
    while True:
        try:
            multicast_envio()
            time.sleep(30.0)   # espera de 30 segundos antes do proximo multicast
        except:
            print("erro")      # falta um tratamento melhor






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
    finally:
        socket_udp_sensor.close()


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
                envelope_entrada = serjipe_message_pb2.Envelope()
                envelope_entrada.ParseFromString(data)

                if envelope_entrada.HasField("command"):
                    response = envelope_entrada.command
                else:
                    # tratamento melhor
                    print("erro de comando invalido")
                match response.action:
                    
                    # listar todos os dispositivos
                    case "LISTAR":
                        envelope = serjipe_message_pb2.Envelope()
                        try:
                            retorno = serjipe_message_pb2.ListarDispositivos()


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

                            retorno.amount = str(len(devices))

                            
                            envelope.listar_dispositivos.CopyFrom(retorno)
                            envelope.erro = "SUCESSO"
                        except:
                            envelope.erro = "FALHA"
                        bytes_envelope = envelope.SerializeToString()
                        conn.sendall(bytes_envelope)
                    
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

Thread_udp_sensor = threading.Thread(
    target=socket_udp_sensor,
    daemon=True
)


Thread_multicast = threading.Thread(
    target=multicast_periodico, 
    daemon=True
)

Thread_udp_sensor.start()
Thread_multicast.start()
server_cliente()
