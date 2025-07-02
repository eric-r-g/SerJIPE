import socket

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

ip_maquina = get_local_ip()