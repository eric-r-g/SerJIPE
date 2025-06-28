import socket
import threading
import struct   #Para manipulação de dados binários (usado no multicast)
import time
import random
from datetime import datetime   #Obter data/hora atual
import uuid     #Gerar id's únicos
import serjipe_message_pb2  #Módulo gerado pelo Protocol Buffers para as mensagens

class SensorTemperatura:
    def __init__(self): #Construtor da classe - inicializa o sensor
        #Especificidades
        self.temperatura_atual = 25
        self.intervalo_envio = 15

        #Gera um ID único para o dispositivo
        self.device_id = f"TEMP-{str(uuid.uuid4())[:8]}"

        self.type = "sensor_temperatura"

        self.status = "ON"

        self.ip = self.get_local_ip()

        #Escolhe uma porta TCP aleatória
        self.tcp_port = random.randint(10000, 20000)

        #Configurações de multicast
        self.multicast_group = '239.1.2.3'
        self.multicast_port = 5000

        #Informações do gateway (preenchidas após descoberta)
        self.gateway_ip = None
        self.gateway_udp_port = 7000

        print(f"Sensor {self.device_id} iniciado em {self.ip}:{self.tcp_port}")

    def get_local_ip(self): #Obtém o endereço local da máquina
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
    
    def discovery_listener(self):   #Escuta por pedidos de descoberta do gateway
        while True: #Loop principal para reiniciar automaticamente
            try:
                #Cria socket UDP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                #Associa o socket a todas as interfaces de rede na porta multicast
                s.bind(('0.0.0.0', self.multicast_port))

                #Prepara para entrar no grupo multicast
                #Converte o endereço IP para formato binário
                group = socket.inet_aton(self.multicast_group)

                #Empacota o endereço do grupo e a interface
                mreq = struct.pack('4s4s', group, socket.inet_aton('0.0.0.0'))

                #Configura o socket para entrar no grupo multicast
                s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

                #Define timeout para evitar bloqueio permanente
                s.settimeout(5.0) 

                print(f"[{self.device_id}] Aguardando descoberta...")
                
                while True: #Loop secundário para recebimentos
                    try:
                        #Aguarda receber dados no socket multicast (buffer de 1024 bytes)
                        data, endr = s.recvfrom(1024)

                        try:
                            #Desserializa a mensagem como DeviceInfo
                            mensagem = serjipe_message_pb2.DeviceInfo()
                            mensagem.ParseFromString(data)

                            # Verifica se é a mensagem de multicast (device_id == "multicast")
                            if (mensagem.device_id == "GATEWAY"):
                                #Salva e informa o IP do gateway
                                self.gateway_ip = mensagem.ip
                                print(f"[{self.device_id}] Gateway encontrado: {self.gateway_ip}")

                                #Prepara a resposta com informações do dispositivo
                                device_info = serjipe_message_pb2.DeviceInfo(
                                    device_id=self.device_id,
                                    type=self.type,
                                    ip=self.ip,
                                    port=self.tcp_port,
                                    status=self.status
                                )

                                #Usa um socket diferente para resposta (evita conflito)
                                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as response_sock:
                                    response_sock.sendto(device_info.SerializeToString(), (self.gateway_ip, mensagem.port))
                                
                                print(f"[{self.device_id}] Registrado no gateway!")

                        except Exception as e:
                            print(f"[{self.device_id}] Erro ao processar mensagem de descoberta: {str(e)}")
                            continue

                    except socket.timeout:
                        #Timeout - continua ouvindo
                        continue
                    except ConnectionResetError:
                        print(f"[{self.device_id}] Erro de conexão resetada. Reiniciando socket...")
                        break  # Sai do loop secundário para recriar socket
                    except Exception as e:
                        print(f"[{self.device_id}] Desligado")
                        break

            except Exception as e:
                print(f"[{self.device_id}] Desligado")
                break

            finally:
                # Fecha o socket antes de recriar
                try:
                    if 's' in locals():
                        s.close()
                except:
                    pass
            
            # Espera antes de recriar o socket
            time.sleep(1)

    def servidor_comando_tcp(self): #Servidor para receber comandos do gateway
        #Socket TCP
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #Associa o socket ao IP e porta TCP do dispositivo
        server.bind((self.ip, self.tcp_port))

        # Habilita o socket para aceitar conexões
        server.listen()

        while True:
            # Aceita e recebe os dados da conexão
            conn, addr = server.accept()
            data = conn.recv(1024)  #Até 1024 bytes

            #Preenche um obejto de comando com os dados
            command = serjipe_message_pb2.Command()
            command.ParseFromString(data)

            #Verifica se é para esse dispositivo
            if command.device_id == self.device_id:
                #Processa a solicitação
                if command.action == "DESLIGAR":
                    self.status = "OFF"
                    print(f"[{self.device_id}] Desligado")
                elif command.action == "LIGAR":
                    self.status = "ON"
                    print(f"[{self.device_id}] Ligado")
                elif command.action == "SETAR_INTERVALO":
                    try:
                        #Tenta converter o parâmetro para inteiro
                        novo_intervalo = int(command.parameter)
                        #Atualiza o intervalo de envio de dados
                        self.intervalo_envio = novo_intervalo
                        print(f"Intervalo alterado para {novo_intervalo}s")
                    except ValueError:
                        #Trata erro se o parâmetro não for número
                        print("Parâmetro inválido para intervalo")
                
                #Confirmação de recebimento
                conn.send(b"OK")

                #Fecha a conexão
                conn.close()

    def send_data(self):    #Enviar dados periódicos do sensor para o gateway -via UDP-
        while True:
            if(self.gateway_ip and self.status == "ON"):
                #Simula uma leitura de temperatura
                hora = datetime.now().hour
                if 6 <= hora < 18:  # Dia: tendência de aquecimento
                    temp_esperada = 28.0
                else:  # Noite: tendência de resfriamento
                    temp_esperada = 22.0
                    
                # Ajusta gradualmente para a temperatura-alvo
                if self.temperatura_atual < temp_esperada:
                    self.temperatura_atual += 0.1
                elif self.temperatura_atual > temp_esperada:
                    self.temperatura_atual -= 0.1
                    
                # Adiciona variação aleatória pequena (±0.1°C)
                variacao = random.uniform(-0.1, 0.1)
                temperatura = round(self.temperatura_atual + variacao, 1)
                
                # Limites realistas
                temperatura = max(18.0, min(temperatura, 32.0))

                #Cria a mensagem de dados do sensor
                sensor_data = serjipe_message_pb2.SensorData(
                    device_id=self.device_id,
                    value=temperatura,
                    timestamp=datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                )

                #Socket UDP temporário
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                #Envia os dados para o gateway
                s.sendto(sensor_data.SerializeToString(), (self.gateway_ip, self.gateway_udp_port))

            time.sleep(self.intervalo_envio)

    def run(self): #Inicia as funcionalidades em threads separadas
        #Escuta por pedidos de descoberta multicast
        threading.Thread(target=self.discovery_listener, daemon=True).start()

        #Servidor TCP para comandos
        threading.Thread(target=self.servidor_comando_tcp, daemon=True).start()

        #Envio de dados
        threading.Thread(target=self.send_data, daemon=True).start()

        #Loop que mantem o programa rodando
        while True:
            time.sleep(1)   #Evitar que termine imediatamente

if __name__ == "__main__":
    sensor = SensorTemperatura()
    sensor.run()
