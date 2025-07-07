import threading
import serjipe_message_pb2

device_dict = {}
devices_lock = threading.Lock()

def limpa_device():
    with devices_lock:
        device_dict.clear()

def add_device(device_info):
    with devices_lock:
        device_dict[device_info.device_id] = serjipe_message_pb2.DeviceInfo()
        device_dict[device_info.device_id].CopyFrom(device_info)

def atualizar_device_data(device_data):
    with devices_lock:
        if device_data.device_id in device_dict:
            device_dict[device_data.device_id].data.CopyFrom(device_data)

def listar_devices():
    retorno = None
    erro = False
    try:
        retorno = serjipe_message_pb2.ListarDispositivos()

        with devices_lock:
            retorno.devices.extend([device for device in device_dict.values()])
            retorno.amount = str(len(device_dict))
    except Exception as e:
        print(f"falha na criação da lista de dispositivos: {e}")
        erro = True

    return retorno, erro

def get_device_info(device_id):
    with devices_lock:
        if device_id in device_dict:
            return device_dict.get(device_id), False
        else:
            return None, True