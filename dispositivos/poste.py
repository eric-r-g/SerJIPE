import json
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

class Poste:
    def __init__(self): #Inicialização do dispositivo
        #Especificidades
        self.brilho = 100
        self.automatico = 0
        self.consumo_medio = 0

        #Gera um ID único para o dispositivo
        self.id_disp = f"P-{str(uuid.uuid4())[:8]}"

        self.type = "poste"

        self.status = "OFF"

        self.ip = self.obter_ip_local()

        # Escolhe uma porta para o gRPC aleatória
        self.porta_grpc = random.randint(50052, 60000)
        self.grpc_endpoint = f"{self.ip}:{self.porta_grpc}"

        #Configurações de multicast
        self.grupo_multicast = '239.1.2.3'
        self.multicast_port = 5000

        #Informações do gateway (preenchidas após descoberta)
        self.gateway_ip = None
        self.porta_udp_gateway = 0

        print(f"Poste {self.id_disp} iniciado!")

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
                            print(mensagem_gateway)

                            #Prepara a resposta com informações do dispositivo
                            resposta_json = {
                                "device_id": self.id_disp,
                                "type": self.type,
                                "grpc_endpoint": self.grpc_endpoint,
                                "status": self.status,
                                "value_name": ["Brilho (%)", "Modo Automático", "Consumo de energia (kWh)"],
                                "value": [str(self.brilho), str(self.automatico), f"{self.consumo_medio:.1f}"],
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
    def __init__(self, poste):
        self.poste = poste  # Referência ao dispositivo

    def EnviarComando(self, request, context):
        #Comando no request. Retornar DeviceInfo
        acao = request.action
        parametro = request.parameter

        if acao == "DESLIGAR":
            self.poste.status = "OFF"
            print(f"[{self.poste.id_disp}] Desligado")
        elif acao == "LIGAR":
            self.poste.status = "ON"
            print(f"[{self.poste.id_disp}] Ligado")
        elif acao == "MODO_AUTOMATICO":
            self.poste.automatico = 1
        elif acao == "MODO_MANUAL":
            self.poste.automatico = 0
        elif acao == "ALTERAR_BRILHO":
            try:
                self.poste.brilho = int(parametro)
            except ValueError:
                print("Parâmetro inválido para brilho")
            
        #Atualizar o estado no modo automatico
        if(self.poste.automatico):
            hora = datetime.now().hour
            if(hora >= 18 or hora <= 6):
                self.poste.status = "ON"
            else:
                self.poste.status = "OFF"

        #Atualizar consumo
        if(self.poste.status == "ON"):
            self.poste.consumo_medio = (self.poste.brilho/100)*0.7
        else:
            self.consumo_medio = 0

        #Envio de DeviceInfo
        device_info = serjipe_message_pb2.DeviceInfo(
            device_id = self.poste.id_disp,
            type = self.poste.type,
            grpc_endpoint = self.poste.grpc_endpoint,
            status = self.poste.status,
            value_name = ["Brilho (%)", "Modo Automático", "Consumo de energia (kWh)"],
            value = [str(self.poste.brilho), str(self.poste.automatico), f"{self.poste.consumo_medio:.1f}"],
        )

        return device_info

def serve(poste):    #Inicia o servidor grpc
    port = str(poste.porta_grpc)
    
    #Utiliza um pool de threads para as requisições
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Registra a implementação do serviço ControleDispositivosService no servidor.
    serjipe_message_pb2_grpc.add_ControleDispositivosServiceServicer_to_server(ControleDispositivosService(poste), server)
    
    #Configuração da porta de escuta
    server.add_insecure_port("[::]:" + port)

    server.start()
    print("Servidor iniciado em " + port)
    return server

if __name__ == "__main__":
    poste = Poste()

    #Inicia thread de descoberta multicast
    threading.Thread(target=poste.descoberta_multicast, daemon=True).start()
    
    #Inicializa o sistema de logging(registro de eventos)
    logging.basicConfig()

    server = serve(poste)

    #Loop que mantem o programa rodando
    try:
        while True:
            time.sleep(3600) 
    except KeyboardInterrupt:
        print("Desligando dispositivo")
        server.stop(0)
