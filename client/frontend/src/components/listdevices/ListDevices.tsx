import { useEffect, useState } from "react";
import './listdevices.css';
import type { DeviceInfo } from "../../lib/interfaces";
import SendCommand from "./sendcommand/SendCommand";

interface ListDevicesProps{
    devices: Array<DeviceInfo> // any tem que ser mudado pra device dps
}

function ListDevices(props: ListDevicesProps){
    const [devicesList, setDevicesList] = useState(getDevicesList());

    useEffect(() =>{
        setDevicesList(getDevicesList());
    }, [props.devices]);

    function getDevicesList(){
        return props.devices.map((device, index) => {
            return(
                <div className="devices-item" key={`device${index}`}>
                    <div className="device-header-wrapper">
                        <header className="device-header">
                            <p>Dispositivo {device.device_id}</p>
                        </header>
                        <div className="device-buttons">
                            <button>Ligar/Desligar</button>
                        </div>
                    </div>
                    <div className="device-info-wrapper">
                        <div><h3>Informações do dispositivo</h3>
                            <div>
                                <p>ID: {device.device_id}</p>
                                <p>Tipo: {device.type}</p>
                                <p>IP: {device.ip}</p>
                                <p>Porta: {device.port}</p>
                                <p>Status: {device.status}</p>
                            </div>
                        </div>
                        <div><h3>Ultima leitura</h3>
                            <div>
                                <p>Valor: {device.lastReading.value}</p>
                                <p>Hora: {device.lastReading.timestamp}</p>
                            </div>
                        </div>
                        <div><h3>Enviar comando</h3>
                            <SendCommand device={device}/>
                        </div>
                    </div>
                </div>
            )
        })
    }

    return (
        <div id="list-devices">
            {devicesList}
        </div>
    )
}

export default ListDevices;