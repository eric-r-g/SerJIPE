import socket
import threading
import struct   #Para manipulação de dados binários (usado no multicast)
import time
import random
from datetime import datetime   #Obter data/hora atual
import uuid     #Gerar id's únicos
import serjipe_message_pb2  #Módulo gerado pelo Protocol Buffers para as mensagens

class Lixeira:
    def __init__(self): #Inicialização do dispositivo
        #Especificidades
        self.organico = random.randint(10, 40)
        self.reciclavel = random.randint(40, 60)
        self.eletronico = 100 - self.organico - self.reciclavel

        #Gera um ID único para o dispositivo
        self.id_disp = f"LIX-{str(uuid.uuid4())[:8]}"

        self.tipo = "lixeira_inteligente"

        self.status = "ON"

        self.ip = self.obter_ip_local()

        #Escolhe uma porta TCP aleatória
        self.porta_tcp = random.randint(10000, 20000)

        #Configurações de multicast
        self.grupo_multicast = '239.1.2.3'
        self.multicast_port = 5000

        #Informações do gateway (preenchidas após descoberta)
        self.gateway_ip = None
        self.porta_udp_gateway = 0

        print(f"Lixeira {self.id_disp} iniciado em {self.ip}:{self.porta_tcp}")

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
                            #Desserializa a mensagem
                            envelope = serjipe_message_pb2.Envelope()
                            envelope.ParseFromString(data)

                            if envelope.HasField("discover"):
                                mensagem = serjipe_message_pb2.Discover()
                                mensagem.CopyFrom(envelope.discover)
                            else:
                                #Tratamento
                                print("erro de comando invalido")
                            
                            #Salva as informações
                            self.gateway_ip = mensagem.ip
                            self.porta_udp_gateway = mensagem.port_udp_sensor
                            print(f"[{self.id_disp}] Gateway encontrado: {self.gateway_ip}")

                            #Prepara a resposta com informações do dispositivo
                            device_info = serjipe_message_pb2.DeviceInfo(
                                device_id = self.id_disp,
                                type = self.tipo,
                                ip = self.ip,
                                port = self.porta_tcp,
                                data = serjipe_message_pb2.DeviceData(
                                    device_id = self.id_disp,
                                    status = self.status,
                                    value_name = ["Reciclável (%)", "Orgânico (%)", "Eletrônico (%)"],
                                    value = [f"{self.reciclavel:.1f}", f"{self.organico:.1f}", f"{self.eletronico:.1f}"],
                                    timestamp = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                                )
                            )
                            #Cria o envelope de envio
                            envelopeEnvio = serjipe_message_pb2.Envelope()
                            envelopeEnvio.device_info.CopyFrom(device_info)
                            envelopeEnvio.erro = 'SUCESSO'
                            

                        except Exception as e:
                            print(f"[{self.id_disp}] Erro ao processar mensagem de descoberta: {str(e)}")
                            envelopeEnvio = serjipe_message_pb2.Envelope()
                            envelopeEnvio.erro = "FALHA"
                        finally:
                            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as response_sock:
                                response_sock.sendto(envelopeEnvio.SerializeToString(), (self.gateway_ip, mensagem.port_multicast))
                                
                            print(f"[{self.id_disp}] Registrado no gateway!")
                            continue
                        

                    except socket.timeout:
                        #Timeout - continua ouvindo
                        continue
                    except ConnectionResetError:
                        print(f"[{self.id_disp}] Erro de conexão resetada. Reiniciando socket...")
                        break  # Sai do loop secundário para recriar socket
                    except Exception as e:
                        print(f"[{self.id_disp}] Desligado")
                        break

            except Exception as e:
                print(f"[{self.id_disp}] Desligado")
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
        server.bind((self.ip, self.porta_tcp))

        # Habilita o socket para aceitar conexões
        server.listen()

        while True:
            try:
                #Aceita e recebe os dados da conexão
                conn, endr = server.accept()
                data = conn.recv(1024)  #Até 1024 bytes

                envelope = serjipe_message_pb2.Envelope()
                envelope.ParseFromString(data)

                envelopeEnvio = serjipe_message_pb2.Envelope()
                envelopeEnvio.erro = 'SUCESSO'

                if envelope.HasField("command"):
                    command = envelope.command
                else:
                    #Tratamento
                    raise Exception("erro de comando invalido")

                #Verifica se é para esse dispositivo
                if command.device_id == self.id_disp:
                    #Processa a solicitação
                    if command.action == "DESLIGAR":
                        self.status = "OFF"
                        print(f"[{self.id_disp}] Desligado")
                    elif command.action == "LIGAR":
                        self.status = "ON"
                        print(f"[{self.id_disp}] Ligado")
                    elif command.action == "GERAR_RELATORIO":
                        variacao1 = random.randint(-10, 10)
                        self.reciclavel += variacao1
                        self.reciclavel = max(20, min(self.reciclavel, 80))
                        variacao2 = random.randint(-5, 5)
                        self.organico += variacao2
                        self.organico = max(5, min(self.organico, 50))
                        self.eletronico = 100 - self.reciclavel - self.organico
                        if self.eletronico < 0:
                            self.eletronico = 0
                    
                    #Confirmação de recebimento (envio de DeviceData)
                    device_data = serjipe_message_pb2.DeviceData(
                        device_id = self.id_disp,
                        status = self.status,
                        value_name = ["Reciclável (%)", "Orgânico (%)", "Eletrônico (%)"],
                        value = [f"{self.reciclavel:.1f}", f"{self.organico:.1f}", f"{self.eletronico:.1f}"],
                        timestamp = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                    )

                    envelopeEnvio.device_data.CopyFrom(device_data)
                    
                    conn.send(envelopeEnvio.SerializeToString())

            except Exception as e:
                print(f"Erro no servidor TCP: {str(e)}")

            finally:
                if ('conn' in locals()):
                    #Fecha a conexão
                    conn.close()

    def run(self): #Inicia as funcionalidades em threads separadas
        #Escuta por pedidos de descoberta multicast
        threading.Thread(target=self.descoberta_multicast, daemon=True).start()

        #Servidor TCP para comandos
        threading.Thread(target=self.servidor_comando_tcp, daemon=True).start()

        #Loop que mantem o programa rodando
        while True:
            time.sleep(1)   #Evitar que termine imediatamente

if __name__ == "__main__":
    lixeira = Lixeira()
    lixeira.run()