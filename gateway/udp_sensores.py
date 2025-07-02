import socket
import serjipe_message_pb2

from config import *
from devices_manager import atualizar_device_data

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
            envelope_entrada = serjipe_message_pb2.Envelope()
            envelope_entrada.ParseFromString(data)
            
            # verifica se possui o campo certo
            if envelope_entrada.HasField("device_data"):
                atualizar_device_data(envelope_entrada.device_data)

        except socket.timeout:
            continue
        except Exception as e:
            print(f"Erro no recebimento da mensagem: {e}")
            break

    if sock_udp_sensor:
        sock_udp_sensor.close()