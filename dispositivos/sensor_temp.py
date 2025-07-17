"""Basicamente, a gente vai trocar o UDP pelo RabbitMQ para receber os dados dos sensores.

Na Descoberta: O Gateway agora tem que mandar a mensagem de anúncio em JSON (não mais em Protobuf) e, 
nessa mensagem, precisa incluir o endereço do RabbitMQ.

No Recebimento de Dados: você precisa criar um "ouvinte" novo para o RabbitMQ que rode numa thread separada. 
Ele vai receber os dados de temperatura o sensor envia, também em JSON, e atualizar o sistema."""



import socket
import threading
import struct
import time
import random
from datetime import datetime
import uuid
#import serjipe_message_pb2  #não usaremos mais protobuf.
import json  #Usaremos JSON para a descoberta e para as mensagens do broker
import pika  #A biblioteca para se comunicar com o RabbitMQ

class SensorTemperatura:
    def __init__(self):  # Inicialização do dispositivo

        
        # Especificidades
        self.temperatura_atual = 25
        self.intervalo_envio = 15

        # Gera um ID único para o dispositivo
        self.id_disp = f"TEMP-{str(uuid.uuid4())[:8]}"
        self.tipo = "sensor_temperatura"
        self.status = "ON"
        self.ip = self.obter_ip_local()

       
        # self.porta_tcp = random.randint(10000, 20000)

        #Configurações de multicast
        self.grupo_multicast = '239.1.2.3'
        self.multicast_port = 5000

        #Informações do gateway (preenchidas após descoberta)
        self.gateway_ip = None
        #troca a porta UDP pelo dicionário de informações do Broker
       
        self.broker_info = None  #novo

      
        print(f"Sensor {self.id_disp} iniciado em {self.ip}")

    def obter_ip_local(self):  #Obtém o endereço local da máquina
   
     
       
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def descoberta_multicast(self):  # Escuta por pedidos de descoberta do gateway
        while True:  # Loop principal para reiniciar automaticamente
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', self.multicast_port))
                grupo = socket.inet_aton(self.grupo_multicast)
                mreq = struct.pack('4s4s', grupo, socket.inet_aton('0.0.0.0'))
                s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                s.settimeout(10.0)

                print(f"[{self.id_disp}] Aguardando descoberta...")

                while True:  # Loop secundário para recebimentos
                    try:
                        data, endr = s.recvfrom(1024)
                
                        #Antes, Protobuf Agora,JSON.
                        try:
                            #1. Decodifica a mensagem JSON que o Gateway enviou.
                            mensagem_gateway = json.loads(data.decode('utf-8'))

                            #2. Guarda as informações
                            self.gateway_ip = mensagem_gateway.get("gateway_ip")
                            self.broker_info = mensagem_gateway.get("broker_info")  # <-- A informação mais importante!
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
                            
                            porta_resposta_gateway = 5008
                            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as response_sock:
                                response_sock.sendto(json.dumps(resposta_json).encode('utf-8'), (self.gateway_ip, porta_resposta_gateway))
                            
                            print(f"[{self.id_disp}] Registrado no gateway!")
                            s.close() # Fecha o socket de descoberta
                            return  # Termina a função (e a thread)

                        except Exception as e:
                            print(f"[{self.id_disp}] Erro ao processar mensagem de descoberta: {str(e)}")
                       

                    except socket.timeout:
                        continue # Volta a esperar por uma mensagem

            except Exception as e:
                print(f"[{self.id_disp}] Erro na thread de descoberta: {e}. Tentando novamente em 5s.")
                time.sleep(5)




    def envio_dados(self):  # Afunção de envio, agora para o BROKER.
       
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
                    temp_esperada = 28.0 if 6 <= hora < 18 else 22.0
                    if self.temperatura_atual < temp_esperada: self.temperatura_atual += 0.1
                    elif self.temperatura_atual > temp_esperada: self.temperatura_atual -= 0.1
                    variacao = random.uniform(-0.3, 0.3)
                    temperatura = round(self.temperatura_atual + variacao, 1)
                    temperatura = max(18.0, min(temperatura, 32.0))

                    # Cria a mensagem como um dicionário Python (que será convertido para JSON).
                    
                    mensagem_dados = {
                        "device_id": self.id_disp,
                        "status": self.status,
                        "value_name": ["Temperatura atual (°C)", "Intervalo de envio (segundos)"],
                        "value": [f"{temperatura:.1f}", str(self.intervalo_envio)],
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

    def run(self):  # Inicia as funcionalidades em threads separadas
       
        threading.Thread(target=self.descoberta_multicast, daemon=True).start()

    


        threading.Thread(target=self.envio_dados, daemon=True).start()

        #Loop que mantem o rodando
        while True:
            time.sleep(1)

if __name__ == "__main__":
    sensor = SensorTemperatura()
    sensor.run()