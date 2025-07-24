// Isso é tão direto ao ponto que talvez seja desnecessária uma classe separada, qualquer coisa dps mudo
export class DeviceList{
    list;
    constructor(){
        this.list = new Map();
    }

    // Também atualiza
    addDevice(device){
        this.list.set(device.device_id, device);
    }
    
    updateDeviceInfo(oldDeviceId, newDevice){
        let oldDevice = this.getDevice(oldDeviceId);
        if(!oldDevice) return;

        oldDevice.type = newDevice.type;
        oldDevice.status = newDevice.status;

        this.list.set(oldDeviceId, oldDevice);
    }

    removeDevice(device){
        this.list.delete(device.device_id);
    }

    clearList(){
        this.list.clear();
    }

    getDevices(){
        return Array.from(this.list.values());
    }

    getDevice(device_id){
        return this.list.get(device_id);
    }
}