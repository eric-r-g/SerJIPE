import { useEffect, useState } from "react";
import './listdevices.css';

interface ListDevicesProps{
    devices: Array<any> // any tem que ser mudado pra device dps
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
                        <p>Informações do dispositivo</p>
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