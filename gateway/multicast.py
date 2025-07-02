import socket
import serjipe_message_pb2
import time
from config import *
from devices_manager import limpa_device, add_device

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
    limpa_device()

    try:
        while(True):
            try:
                data, addr = socket_multicast_respostas.recvfrom(1024)
                envelope_entrada = serjipe_message_pb2.Envelope()
                envelope_entrada.ParseFromString(data)
            
                if envelope_entrada.HasField("device_info"):
                    try:
                        add_device(envelope_entrada.device_info)
                    except Exception as e:
                        print(f"Falha ao processar os dados: {e}")
                else:
                    raise ValueError("Ausencia de campo")
            except socket.timeout:
                print("tempo de recebimento esgotado")
                break
            except Exception as e:
                print(f"Dados corrompidos ou errados: {e}")
                continue

            
    finally:
        # fecha a socket de entrada
        socket_multicast_respostas.close()


def multicast_periodico():
    while True:
        try:
            multicast_envio()
            time.sleep(10.0)   # espera de 30 segundos antes do proximo multicast
        except Exception as e:
            print(f"erro no multicast periodico: {e}")      # falta um tratamento melhor
            continue
