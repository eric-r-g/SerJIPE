// Isso é tão direto ao ponto que talvez seja desnecessária uma classe separada, qualquer coisa dps mudo
export class DeviceList{
    list;
    constructor(){
        this.list = new Map();
    }

    // Também atualiza
    addDevice(device){
        this.list.set(device.id, device);
    }

    removeDevice(device){
        this.list.delete(device);
    }

    clearList(){
        this.list.clear();
    }

    getDevices(){
        return this.list.values();
    }

    getDevice(deviceId){
        return this.list.get(deviceId);
    }
}