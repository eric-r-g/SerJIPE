import threading
from multicast import multicast_periodico, multicast_envio
from udp_sensores import sensores_receiver
from client_handle import server_cliente

def main():
    # Inicia threads
    Thread_udp_sensor = threading.Thread(
        target=sensores_receiver,
        daemon=True
    )

    Thread_multicast = threading.Thread(
        target=multicast_periodico, 
        daemon=True
    )

    multicast_envio()
    Thread_udp_sensor.start()
    Thread_multicast.start()
    server_cliente()

if __name__ == "__main__":
    main()