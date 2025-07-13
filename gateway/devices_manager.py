import threading
import copy

device_dict = {}
devices_lock = threading.Lock()

def limpa_device():
    with devices_lock:
        device_dict.clear()

def add_device(device_info):
    with devices_lock:
        device_dict[device_info["device_id"]] = copy.deepcopy(device_info)

def atualizar_device_data(device_data):
    with devices_lock:
        if device_data["device_id"] in device_dict:
            device_dict[device_data["device_id"]]["data"] = copy.deepcopy(device_data)

def listar_devices():
    retorno = None
    erro = False
    try:
        retorno = []
        with devices_lock:
            for device_id in device_dict:
                retorno.append(copy.deepcopy(device_dict[device_id]))
    except Exception as e:
        erro = True

    return retorno, erro

def get_device_info(device_id):
    with devices_lock:
        if device_id in device_dict:
            return copy.deepcopy(device_dict[device_id]), False
        else:
            return None, True