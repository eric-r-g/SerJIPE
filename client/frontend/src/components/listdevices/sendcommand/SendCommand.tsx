import type { Command, DeviceData, DeviceInfo } from "../../../lib/interfaces.ts";
import axios from "axios";
import { getAxiosConfig } from "../../../lib/utils.ts";

interface SendCommandProps{
    device: DeviceInfo,
    updateDevice: (device: DeviceData) => void;
    updateWarning: (newWarning: string) => void;
}
function SendCommand(props: SendCommandProps){

    function enviarComando(action: string, deviceId: string, parameter: string){
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

    if(props.device.type == 'sensor_temperatura'){
        let interval = props.device.data.valueList[props.device.data.valueNameList.findIndex((value) =>{ return value.toLowerCase().includes('intervalo')})];

        return(
            <div>
                <button onClick={() => enviarComando('DESLIGAR', props.device.deviceId, '')}>Desligar</button>
                <button onClick={() => enviarComando('LIGAR', props.device.deviceId, '')}>Ligar</button>
                <label htmlFor={`param${props.device.deviceId}`}>Mudar intervalo: </label><input type="number" defaultValue={interval} name={`param${props.device.deviceId}`} id={`param${props.device.deviceId}`} onChange={(e) =>{
                    enviarComando('SETAR_INTERVALO', props.device.deviceId, e.target.value);
                }}/>
            </div>
        )
    }
}

export default SendCommand;