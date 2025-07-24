import socket
import threading
import struct   #Para manipulação de dados binários (usado no multicast)
import time
import random
from datetime import datetime   #Obter data/hora atual
import uuid     #Gerar id's únicos
import serjipe_message_pb2  #Módulo gerado pelo Protocol Buffers para as mensagens
import serjipe_message_pb2_grpc
from concurrent import futures  #Utilização de threads
import grpc
import logging
import json  #Usaremos JSON para a descoberta multicast

class Lixeira:
    def __init__(self): #Inicialização do dispositivo
        #Especificidades
        self.organico = random.randint(10, 40)
        self.reciclavel = random.randint(40, 60)
        self.eletronico = 100 - self.organico - self.reciclavel

        #Gera um ID único para o dispositivo
        self.id_disp = f"LIX-{str(uuid.uuid4())[:8]}"

        self.type = "lixeira_inteligente"

        self.status = "ON"

        self.ip = self.obter_ip_local()
        
        # Escolhe uma porta para o gRPC aleatória
        self.porta_grpc = random.randint(50052, 60000)
        self.grpc_endpoint = f"{self.ip}:{self.porta_grpc}"

        #Configurações de multicast
        self.grupo_multicast = '239.1.2.3'
        self.multicast_port = 5000

        #Informações do gateway (preenchidas após descoberta)
        self.gateway_ip = None
        self.porta_resposta_gateway = 0

        print(f"Lixeira {self.id_disp} iniciado em {self.ip}")

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
                            #Decodifica a mensagem JSON que o gateway enviou.
                            mensagem_gateway = json.loads(data.decode('utf-8'))

                            #Guarda as informações
                            self.gateway_ip = mensagem_gateway.get("gateway_ip")
                            self.porta_resposta_gateway = mensagem_gateway.get("gateway_port")
                            print(f"[{self.id_disp}] Gateway encontrado: {self.gateway_ip}")
                            
                            #Prepara a resposta com informações do dispositivo
                            resposta_json = {
                                "device_id": self.id_disp,
                                "type": self.type,
                                "grpc_endpoint": self.grpc_endpoint,
                                "status": self.status,
                                "value_name": ["Reciclável (%)", "Orgânico (%)", "Eletrônico (%)"],
                                "value": [f"{self.reciclavel:.1f}", f"{self.organico:.1f}", f"{self.eletronico:.1f}"]
                            }

                            #Envia a resposta de volta para o Gateway
                            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as response_sock:
                                response_sock.sendto(json.dumps(resposta_json).encode('utf-8'), (self.gateway_ip, self.porta_resposta_gateway))
                                
                            print(f"[{self.id_disp}] Registrado no gateway!")
                            
                        except Exception as e:
                            print(f"[{self.id_disp}] Erro ao processar mensagem de descoberta: {str(e)}")

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


class ControleDispositivosService(serjipe_message_pb2_grpc.ControleDispositivosServiceServicer):    #Servidor para comandos via gRPC
    def __init__(self, disp):
        self.disp = disp  # Referência ao dispositivo

    def EnviarComando(self, request, context):
        #Comando no request. Retornar DeviceInfo
        acao = request.action
        parametro = request.parameter

        if acao == "DESLIGAR":
            self.disp.status = "OFF"
            print(f"[{self.disp.id_disp}] Desligado")
        elif acao == "LIGAR":
            self.disp.status = "ON"
            print(f"[{self.disp.id_disp}] Ligado")
        elif acao == "GERAR_RELATORIO":
            variacao1 = random.randint(-10, 10)
            self.disp.reciclavel += variacao1
            self.disp.reciclavel = max(20, min(self.disp.reciclavel, 80))
            variacao2 = random.randint(-5, 5)
            self.disp.organico += variacao2
            self.disp.organico = max(5, min(self.disp.organico, 50))
            self.disp.eletronico = 100 - self.disp.reciclavel - self.disp.organico
            if self.disp.eletronico < 0:
                self.disp.eletronico = 0

        #Envio de DeviceInfo
        device_info = serjipe_message_pb2.DeviceInfo(
            device_id = self.disp.id_disp,
            type = self.disp.type,
            grpc_endpoint = self.disp.grpc_endpoint,
            status = self.disp.status,
            value_name = ["Reciclável (%)", "Orgânico (%)", "Eletrônico (%)"],
            value = [f"{self.disp.reciclavel:.1f}", f"{self.disp.organico:.1f}", f"{self.disp.eletronico:.1f}"]
        )

        return device_info

def serve(disp):    #Inicia o servidor grpc
    port = str(disp.porta_grpc)
    
    #Utiliza um pool de threads para as requisições
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Registra a implementação do serviço ControleDispositivosService no servidor.
    serjipe_message_pb2_grpc.add_ControleDispositivosServiceServicer_to_server(ControleDispositivosService(disp), server)
    
    #Configuração da porta de escuta
    server.add_insecure_port("[::]:" + port)

    server.start()
    print("Servidor iniciado em " + port)
    return server

if __name__ == "__main__":
    disp = Lixeira()

    #Inicia thread de descoberta multicast
    threading.Thread(target=disp.descoberta_multicast, daemon=True).start()
    
    #Inicializa o sistema de logging(registro de eventos)
    logging.basicConfig()

    server = serve(disp)

    #Loop que mantem o programa rodando
    try:
        while True:
            time.sleep(3600) 
    except KeyboardInterrupt:
        print("Desligando dispositivo")
        server.stop(0)
