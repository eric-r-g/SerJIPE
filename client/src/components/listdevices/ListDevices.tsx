import { useEffect, useState } from "react";
import './listdevices.css';
import type { DeviceInfo } from "../../lib/interfaces";
import SendCommand from "./sendcommand/SendCommand";

interface ListDevicesProps{
    devices: Array<DeviceInfo> // any tem que ser mudado pra device dps
    updateDevice: (device: DeviceInfo) => void;
    updateErrorMsg: (newErrorMsg: string) => void;
}

function GetDeviceValues(props: {device: DeviceInfo}){
    if(props.device.value == undefined || props.device.value_name == undefined)
        return(
            <div>
                <p>Nenhum atributo encontrado</p>
            </div>
        )
    
    return(
        <div>
            {
                props.device.value_name.map((valueName, index) =>{
                    return(
                        <p id={`valueData${props.device.device_id}-${index}`}>
                            {valueName}: {props.device.value[index]}
                        </p>
                    )
                })
            }
        </div>

    )
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
                                <p>Dispositivo {device.device_id}</p>
                            </header>
                        </div>
                        <div className="device-info-wrapper">
                            <div><h3>Informações do dispositivo</h3>
                                <div>
                                    <p>ID: {device.device_id}</p>
                                    <p>Status: {device.status}</p>
                                </div>
                            </div>
                            <div><h3>Ultima leitura</h3>
                                <GetDeviceValues device={device}/>
                            </div>
                            <div><h3>Enviar comando</h3>
                                <SendCommand device={device} updateDevice={props.updateDevice} updateErrorMsg={props.updateErrorMsg}/>
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