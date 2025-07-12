import pika
import json
import threading
import time

from config import *
from devices_manager import atualizar_device_data

# generalizar os processamentos 

def callback(ch, method, properties, body):
    # aqui será substituido pelo devido processamento;
    print(body)

def sensor_receiver(connection, queue_type):
    # caso a conexão caia, ele vai tentar se reconectar
    while(True):
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

# função responsavel por criar os canais de comunicação
def sensores_receiver():
    # aqui cria e se conectar a conexão do rabbit
    connection = None
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    except Exception as e:
        print("erro na criação da conexão com o Rabbit")
        if connection:
            connection.close()

    # para cada um dos tipos de sensores, cria sua propria thread e fila para escuta-lo
    sensores_type = ["temp", "trafego"]
    threads_sensor = []

    # criação das threads
    for type in sensores_type:
        thread = threading.Thread(
            target=sensor_receiver,
            args=(connection, type),
            daemon=True
        )
        thread.start()
        threads_sensor.append(thread)

    for thread in threads_sensor:
        thread.join()
    
    if connection:
        connection.close()
    
