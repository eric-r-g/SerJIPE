import socket
import threading
import struct   #Para manipulação de dados binários (usado no multicast)
import time
import random
from datetime import datetime   #Obter data/hora atual
import uuid     #Gerar id's únicos
import serjipe_message_pb2  #Módulo gerado pelo Protocol Buffers para as mensagens
import json
import pika

class SensorTrafego:
    def __init__(self): #Inicialização do dispositivo
        #Especificidades
        self.intervalo_envio = 15
        self.contagem_veiculos = random.randint(40, 300)
        self.nivel_congestionamento = random.randint(10, 90)  # (%)

        #Gera um ID único para o dispositivo
        self.id_disp = f"TRAF-{str(uuid.uuid4())[:8]}"
        self.tipo = "sensor_trafego"
        self.status = "ON"
        self.ip = self.obter_ip_local()

        # self.porta_tcp = random.randint(10000, 20000)

        #Configurações de multicast
        self.grupo_multicast = '239.1.2.3'
        self.multicast_port = 5000

        #Informações do gateway (preenchidas após descoberta)
        self.gateway_ip = None
        self.broker_info = None

        print(f"Sensor {self.id_disp} iniciado em {self.ip}")

    def obter_ip_local(self): #Obtém o endereço local da máquina
        #Cria um socket temporário UDP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #família (IPv4), tipo (UDP)
        try:
            #Tenta conectar a um servidor externo
            s.connect(("8.8.8.8", 80))

            #Obtém o endereço IP local usado na conexão
            ip = s.getsockname()[0]
        except Exception:
            #Em caso de erro, usa o IP de loopback (local host)
            ip = "127.0.0.1"
        finally:
            #Fecha o socket
            s.close()
        return ip
    

    def descoberta_multicast(self):   #Escuta por pedidos de descoberta do gateway
        while True: #Loop principal para reiniciar automaticamente
            try:
                #Cria socket UDP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                #Associa o socket a todas as interfaces de rede na porta multicast
                s.bind(('0.0.0.0', self.multicast_port))

                #Prepara para entrar no grupo multicast
                #Converte o endereço IP para formato binário
                grupo = socket.inet_aton(self.grupo_multicast)

                #Empacota o endereço do grupo e a interface
                mreq = struct.pack('4s4s', grupo, socket.inet_aton('0.0.0.0'))

                #Configura o socket para entrar no grupo multicast
                s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

                #Define timeout para evitar bloqueio permanente
                s.settimeout(5.0) 

                print(f"[{self.id_disp}] Aguardando descoberta...")
                
                while True: #Loop secundário para recebimentos
                    try:
                        #Aguarda receber dados no socket multicast (buffer de 1024 bytes)
                        data, endr = s.recvfrom(1024)

                        try:
                            #1. Decodifica a mensagem JSON que o Gateway enviou.
                            mensagem_gateway = json.loads(data.decode('utf-8'))

                            #2. guarda as informações
                            self.gateway_ip = mensagem_gateway.get("gateway_ip")
                            self.broker_info = mensagem_gateway.get("broker_info")
                            print(f"[{self.id_disp}] Gateway encontrado: {self.gateway_ip}")
                            print(f"[{self.id_disp}] Info do Broker: {self.broker_info}")

                            #3.Prepara uma resposta em JSON, usando suas variáveis.
                            resposta_json = {
                                "device_id": self.id_disp,
                                "type": self.tipo,
                                "ip": self.ip,
                                "status": self.status
                            }
                            
                            #4 Envia a resposta de volta para o Gateway.
                            porta_resposta_gateway = mensagem_gateway.get("gateway_port")
                            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as response_sock:
                                response_sock.sendto(json.dumps(resposta_json).encode('utf-8'), (self.gateway_ip, porta_resposta_gateway))
                            print(f"[{self.id_disp}] Registrado no gateway!")

                        except Exception as e:
                            print(f"[{self.id_disp}] Erro ao processar mensagem de descoberta: {str(e)}")
                    except socket.timeout:
                        #Timeout - continua ouvindo
                        continue
            except Exception as e:
                print(f"[{self.id_disp}] Erro na thread de descoberta: {e}. Tentando novamente em 5s.")
                time.sleep(5)
        if s:
            s.close()

    # estou aqui
    def envio_dados(self):    #Enviar dados periódicos do sensor para o gateway -via UDP-

        #Primeiro, espera a thread de descoberta preencher self.broker_info.
        print(f"[{self.id_disp}] Thread de envio aguardando informações do broker...")
        while not self.broker_info:
            time.sleep(1)

        print(f"[{self.id_disp}] Informações do broker obtidas. Iniciando publicação de dados...")
        
        try:
            #Conecta ao RabbitMQ
            credentials = pika.PlainCredentials('guest', 'guest')
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.broker_info['host'], credentials=credentials))
            channel = connection.channel()
            queue_name = self.broker_info['queue'][0]
            channel.queue_declare(queue=queue_name, durable=True)


            while True:
                if self.status == "ON":
                    hora = datetime.now().hour
                    if 6 <= hora < 18:
                        mudanca_frota = random.randint(-10, 20)
                    else:
                        mudanca_frota = random.randint(-20, 10)

                    self.nivel_congestionamento += mudanca_frota/self.contagem_veiculos
                    self.contagem_veiculos += mudanca_frota
                    self.contagem_veiculos = max(20, min(self.contagem_veiculos, 500))

                    mensagem_dados = {
                        "device_id": self.id_disp,
                        "status": self.status,
                        "type": "sensor_trafego",
                        "value_name": ["Contagem de veículos (por km²)", "Nível de congestionamento (%)", "Intervalo de envio (segundos)"],
                        "value": [str(self.contagem_veiculos), str(self.nivel_congestionamento) ,str(self.intervalo_envio)],
                        "timestamp": datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                    }

                    # Envia os dados para a fila do RabbitMQ.
                    channel.basic_publish(
                        exchange='',
                        routing_key=queue_name,
                        body=json.dumps(mensagem_dados)
                    )

                time.sleep(self.intervalo_envio)

        except pika.exceptions.AMQPConnectionError as e:
            print(f"[{self.id_disp}] CRÍTICO: Perda de conexão com o RabbitMQ. {e}")
        finally:
            if 'connection' in locals() and connection.is_open:
                connection.close()
            print(f"[{self.id_disp}] Thread de envio encerrada.")



    def run(self): #Inicia as funcionalidades em threads separadas
        #Escuta por pedidos de descoberta multicast
        threading.Thread(target=self.descoberta_multicast, daemon=True).start()

        #Envio de dados
        threading.Thread(target=self.envio_dados, daemon=True).start()

        #Loop que mantem o programa rodando
        while True:
            time.sleep(1)   #Evitar que termine imediatamente

if __name__ == "__main__":
    sensor = SensorTrafego()
    sensor.run()
