import { useState } from "react";
import type { Command, DeviceData, DeviceInfo } from "../../../lib/interfaces.ts";
import axios from "axios";
import { getAxiosConfig } from "../../../lib/utils.ts";

interface SendCommandProps{
    device: DeviceInfo,
    updateDevice: (device: DeviceData) => void;
    updateWarning: (newWarning: string) => void;
}
function SendCommand(props: SendCommandProps){
    const [comando, setComando] = useState({action: '', deviceId: '', parameter: ''} as Command);

    function enviarComando(action = comando.action, deviceId = comando.deviceId, parameter = comando.parameter){
        let data = {
            action: action,
            deviceId: deviceId,
            parameter: parameter
        } as Command;

        axios.request(getAxiosConfig(data, '/api/comando', 'POST'))
        .then((response) =>{
            let deviceData = {
                deviceId: response.data.deviceId,
                status: response.data.status,
                timestamp: response.data.timestamp,
                valueNameList: response.data.valueNameList,
                valueList: response.data.valueList
            } as DeviceData;

            props.updateDevice(deviceData);
        })
        .catch((err) => props.updateWarning("O servidor respondeu com: "+err.message));
    }

    return(
        <div>
            <label htmlFor={`action${props.device.deviceId}`}>Ação: </label>
            <input type="text" onChange={(e) => setComando((prev) =>{
                prev.action = e.target.value;
                return prev;
            })}/>
            <label htmlFor={`device_id${props.device.deviceId}`}>Id do dispositivo: </label>
            <input type="text" onChange={(e) => setComando((prev) =>{
                prev.deviceId = e.target.value;
                return prev;
            })}/>
            <label htmlFor={`parameter${props.device.deviceId}`}>Parametro: </label>
            <input type="text" onChange={(e) => setComando((prev) =>{
                prev.parameter = e.target.value;
                return prev;
            })}/>

            <button onClick={() => enviarComando()}>Enviar</button>
        </div>
    )
}

export default SendCommand;