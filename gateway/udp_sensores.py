import pika
import json
import threading
import time
from config import *
from devices_manager import atualizar_device_data
# generalizar os processamentos 

def callback(ch, method, properties, body):
    # aqui será substituido pelo devido processamento;
    data = json.loads(body.decode())
    atualizar_device_data(data)

def sensor_receiver(queue_type):
    # caso a conexão caia, ele vai tentar se reconectar
    
    while(True):
        # aqui cria e se conectar a conexão do rabbit
        connection = None
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        except Exception as e:
            print("erro na criação da conexão com o Rabbit")
            if connection:
                connection.close()
                time.sleep(1)
                continue

        channel = None
        try:
            # cria o canal de comunicação
            channel= connection.channel()
            channel.queue_declare(
                queue=queue_type,
                durable=True
            )

            # estabelece o callback e começa a consumir
            channel.basic_consume(queue=queue_type, auto_ack=True, on_message_callback=callback)
            channel.start_consuming()
        except Exception as e:
            print(f"erro em um dos canais especificos: {e}")
            if channel:
                channel.close()
            time.sleep(1)
            continue

# função responsavel por criar os canais de comunicação
def sensores_receiver():
    # para cada um dos tipos de sensores, cria sua propria thread e fila para escuta-lo
    threads_sensor = []

    # criação das threads
    for type in sensores_type:
        thread = threading.Thread(
            target=sensor_receiver,
            args=(type,),
            daemon=True
        )
        thread.start()
        threads_sensor.append(thread)

    
    
