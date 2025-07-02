import { useEffect, useState } from "react";
import './listdevices.css';
import type { DeviceData, DeviceInfo } from "../../lib/interfaces";
import SendCommand from "./sendcommand/SendCommand";

interface ListDevicesProps{
    devices: Array<DeviceInfo> // any tem que ser mudado pra device dps
    updateDevice: (device: DeviceData) => void;
    updateWarning: (newWarning: string) => void;
}

function ListDevices(props: ListDevicesProps){
    const [devicesList, setDevicesList] = useState(getDevicesList());

    useEffect(() =>{
        setDevicesList(getDevicesList());
    }, [props.devices]);

    function getDevicesList(){
        if(props.devices.length > 0)
            return props.devices.map((device, index) => {
                return(
                    <div className="devices-item" key={`device${index}`}>
                        <div className="device-header-wrapper">
                            <header className="device-header">
                                <p>Dispositivo {device.deviceId}</p>
                            </header>
                        </div>
                        <div className="device-info-wrapper">
                            <div><h3>Informações do dispositivo</h3>
                                <div>
                                    <p>ID: {device.deviceId}</p>
                                    <p>Tipo: {device.type}</p>
                                    <p>IP: {device.ip}</p>
                                    <p>Porta: {device.port}</p>
                                </div>
                            </div>
                            <div><h3>Ultima leitura - {device.data.timestamp}</h3>
                                <div>
                                    <p>{device.data.status}</p>
                                    {
                                        device.data.valueNameList.map((valueName, index) =>{
                                            return(
                                                <p id={`valueData${device.deviceId}-${index}`}>
                                                    {valueName}: {device.data.valueList[index]}
                                                </p>
                                            )
                                        })
                                    }
                                </div>
                            </div>
                            <div><h3>Enviar comando</h3>
                                <SendCommand device={device} updateDevice={props.updateDevice} updateWarning={props.updateWarning}/>
                            </div>
                        </div>
                    </div>
                )
            })
        else
            return(
                <div>
                    <h2>Nenhum dispositivo encontrado!</h2>
                </div>
            )
    }

    return (
        <div id="list-devices">
            {devicesList}
        </div>
    )
}

export default ListDevices;