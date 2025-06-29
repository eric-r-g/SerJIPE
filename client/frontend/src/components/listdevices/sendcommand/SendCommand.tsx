import { useState } from "react";
import type { Command, DeviceInfo } from "../../../lib/interfaces.ts";
import axios from "axios";
import { getAxiosConfig } from "../../../lib/utils.ts";

interface SendCommandProps{
    device: DeviceInfo
}
function SendCommand(props: SendCommandProps){
    const [comando, setComando] = useState({action: '', device_id: '', parameter: ''} as Command);

    function enviarComando(action = comando.action, device_id = comando.device_id, parameter = comando.parameter){
        let data = {
            action: action,
            device_id: device_id,
            parameter: parameter
        } as Command;

        axios.request(getAxiosConfig(JSON.stringify(data), '/api/comando', 'POST'))
        .then((response) =>{
            console.log(response.data); // parsear isso aqui direito depois de testar
        })
        .catch((err) => console.log(err)); // fazer um display de erro se der tempo
    }

    return(
        <div>
            <label htmlFor={`action${props.device.device_id}`}>Ação: </label>
            <input type="text" onChange={(e) => setComando((prev) =>{
                prev.action = e.target.value;
                return prev;
            })}/>
            <label htmlFor={`device_id${props.device.device_id}`}>Id do dispositivo: </label>
            <input type="text" onChange={(e) => setComando((prev) =>{
                prev.device_id = e.target.value;
                return prev;
            })}/>
            <label htmlFor={`parameter${props.device.device_id}`}>Parametro: </label>
            <input type="text" onChange={(e) => setComando((prev) =>{
                prev.parameter = e.target.value;
                return prev;
            })}/>

            <button onClick={() => enviarComando()}>Enviar</button>
        </div>
    )
}

export default SendCommand;