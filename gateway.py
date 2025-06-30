import socket
import serjipe_message_pb2
import threading
import time

devices_dict = {}
devices = []

MULTICAST_GROUP = '239.1.2.3'      # grupo multicast para o discover
PORT_MULTICAST = 5000              # Porta propria para o Multicast
PORT_MULTICAST_RESPOSTA = 4444     # Porta de recebimento para o Multicast
PORT_CLIENTE = 8000                # Porta para se comunicar com o cliente
PORT_UDP_SENSOR = 7000             # Porta para receber dados udp



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

# realiza um multicast para verificar dispositivos válidos
def multicast_envio():
    # criação do socket udp

    socket_multicast = None
    try:
        # cria um socket udp e configura o socket
        socket_multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        socket_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)  # Serve para definir quantos roteadores ele vai passar

        #se conecta ao grupo multicast
        mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
        socket_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    except Exception as e:
        print(f"Falha criação socket_mult: {e}")
        if socket_multicast:
            socket_multicast.close()
        return
    
    try:
        # cria a mensagem para chamar os MULTICAST
        discover = serjipe_message_pb2.Discover()
        discover.ip = ip_maquina
        discover.port_multicast = PORT_MULTICAST_RESPOSTA
        discover.port_udp_sensor = PORT_UDP_SENSOR

        # cria a mensagem envolope para receber o discover
        envelope = serjipe_message_pb2.Envelope()
        envelope.discover.CopyFrom(discover)
        envelope.erro = "SUCESSO"

        # Serializa os dados
        bytes_envelope = envelope.SerializeToString()

    except Exception as e:
        print(f"erro na criação da mensagem: {e}")
        socket_multicast.close()
        return

    try:    
        # envia as requisições para todos os dispositivos
        socket_multicast.sendto(bytes_envelope, (MULTICAST_GROUP, PORT_MULTICAST))
    except Exception as e:
        print(f"Falha no envio: {e}")
    finally:
        # fecha socket de envio
        socket_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
        socket_multicast.close()
        multicast_retorno()


def multicast_retorno():
    # adicionar recursos de thread lock depois

    # cria socket de entrada
    socket_multicast_respostas = None
    try:
        #criação e configuração do socket de entrada
        socket_multicast_respostas = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        socket_multicast_respostas.bind(('0.0.0.0', PORT_MULTICAST_RESPOSTA))

        #  vai escutar as respostas, esperando durante 3 segundos
        socket_multicast_respostas.settimeout(3.0)
    except Exception as e:
        print(f"Falha criação socket_mult: {e}")
        if socket_multicast_respostas:
            socket_multicast_respostas.close()
        return
    
    # limpa os devices que já havia antes
    with devices_lock:
        devices.clear() 

    try:
        while(True):
            try:
                data, addr = socket_multicast_respostas.recvfrom(1024)
                envelope_entrada = serjipe_message_pb2.Envelope()
                envelope_entrada.ParseFromString(data)
            
                if envelope_entrada.HasField("device_info"):
                    response = envelope_entrada.device_info
                else:
                    raise ValueError("Ausencia de campo")
            except socket.timeout:
                print("tempo de recebimento esgotado")
                break
            except Exception as e:
                print(f"Dados corrompidos ou errados: {e}")
                continue

            try:
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
                
                with devices_lock:
                    devices.append(dispositivo)

                with devices_dict_lock:
                    devices_dict[response.device_id] = {}
                    devices_dict[response.device_id]["ip"] = response.ip
                    devices_dict[response.device_id]["port"] = response.port
            except Exception as e:
                print(f"Falha ao processar os dados: {e}")
    finally:
        # fecha a socket de entrada
        socket_multicast_respostas.close()

# cria a função que vai fazer o multicast periodicamente
def multicast_periodico():
    while True:
        try:
            multicast_envio()
            time.sleep(30.0)   # espera de 30 segundos antes do proximo multicast
        except Exception as e:
            print(f"erro no multicast periodico: {e}")      # falta um tratamento melhor
            continue


# criação do socket udp para ouvir as respostas dos sensores
def socket_udp_sensor():
    # altera para que seja ao inves de um sensor dict, seja nos dispositivos (necessitando de thread lock)

    sock_udp_sensor = None
    try:
        # cria um socket udp para ouvir as respostas do udp
        sock_udp_sensor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_udp_sensor.bind(('0.0.0.0', PORT_UDP_SENSOR))

        sock_udp_sensor.settimeout(1.0)
    except Exception as e:
        print(f"erro na criação do socket_sensor")
        if sock_udp_sensor:
            sock_udp_sensor.close()
        return

    while True:
        try:
            # recebimento das mensagens
            data, addr = sock_udp_sensor.recvfrom(1024)
            Envelope_entrada = serjipe_message_pb2.Envelope()
            Envelope_entrada.ParseFromString(data)
            
            # verifica se possui o campo certoo
            if Envelope_entrada.HasField("device_data"):
                response = Envelope_entrada.device_data

            # criação do valor que será armazenado (vai mudar)
            d = {
                "status" : response.status,
                "value_name" : list(response.value_name),
                "value" : list(response.value),
                "timestamp" : response.timestamp
            }

            if response.device_id in devices_dict:
                with devices_dict_lock:
                    devices_dict[response.device_id]["data"] = d.copy()
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Erro no recebimento da mensagem: {e}")
            break

    if sock_udp_sensor:
        sock_udp_sensor.close()


def listar_clientes():
    envelope_retorno = serjipe_message_pb2.Envelope()

    try:
        retorno = serjipe_message_pb2.ListarDispositivos()

        with devices_lock:
            for d in devices:
                # ajeita a mensagem de retorno
                try:
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
                except Exception as e:
                    print(f"Falha na criação de um dispositivo: {e}")
                    continue

            retorno.amount = str(len(devices))

                    
        envelope_retorno.listar_dispositivos.CopyFrom(retorno)
        envelope_retorno.erro = "SUCESSO"
    except Exception as e:
        print(f"falha na criação da lista de dispositivos")
        envelope_retorno.erro = "FALHA"

    return envelope_retorno

def handler_comando(response, envelope_entrada):
    # melhorar o tratamento de erros e o thread lock

    envelope_retorno = serjipe_message_pb2.Envelope()
    socket_dispositivo = None
    try:
        socket_dispositivo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_dispositivo.settimeout(3.0)
    except Exception as e:
        print(f"Falha na criação do socket de repassagem: {e}")
        envelope_retorno.erro = f"Falha na criação do socket de repassagem: {e}"

    if response.device_id in devices_dict:
        with devices_dict_lock:
            ip = devices_dict[response.device_id]["ip"]
            porta = devices_dict[response.device_id]["port"]
    else:
        print("falha: Dispositivo inexistente")
        envelope_retorno.erro = "FALHA: dispositivo inexistente"

    
    try:
        socket_dispositivo.connect((ip, porta))

        
        bytes_response = envelope_entrada.SerializeToString()
        socket_dispositivo.settimeout(1.0)
        socket_dispositivo.sendall(bytes_response)
        
        
        data = socket_dispositivo.recv(1024)
        envelope_retorno.ParseFromString(data)
    except Exception as e:
        print(f"erro no envio da mensagem: {e}")
        envelope_retorno.erro = f"FALHA no envio ou recebimento da mensagem: {e}"
    finally:
        if socket_dispositivo:
            socket_dispositivo.close()

    return envelope_retorno

# cria um socket com o cliente
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

            # se a ação for para listar os dispositivos
            if response.action == "LISTAR":          
                envelope_retorno = listar_clientes()
            # se for para repassar um comando
            else:
                envelope_retorno = handler_comando(response, envelope_entrada)
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

try:
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

devices_lock = threading.Lock()
devices_dict_lock = threading.Lock()
multicast_envio()
Thread_udp_sensor.start()
Thread_multicast.start()
server_cliente()
