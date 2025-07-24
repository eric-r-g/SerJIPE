import type { Command, DeviceInfo } from "../../../lib/interfaces.ts";
import axios from "axios";
import { getAxiosConfig } from "../../../lib/utils.ts";

interface SendCommandProps{
    device: DeviceInfo,
    updateDevice: (device: DeviceInfo) => void;
    updateErrorMsg: (newErrorMsg: string) => void;
}
function SendCommand(props: SendCommandProps){

    function enviarComando(action: string, device_id: string, parameter: string){
        let data = {
            action: action,
            device_id: device_id,
            parameter: parameter
        } as Command;

        axios.request(getAxiosConfig(data, '/api/comando', 'POST'))
        .then((response) =>{
            let deviceInfo = {
                device_id: response.data.device_id,
                type: response.data.type,
                status: response.data.status,
                value_name: response.data.value_name,
                value: response.data.value
            } as DeviceInfo;

            /*if(props.device.type == 'sensor_trafego'){
                let indice_formatar = deviceData.valueNameList.findIndex((str) =>{ return str.toLowerCase().includes('congestionamento') });
                let formatar = deviceData.valueList[indice_formatar];
                deviceData.valueList[indice_formatar] = Number(formatar).toFixed(1);
            }else if(props.device.type == 'poste'){
                let indice_formatar = deviceData.valueNameList.findIndex((str) =>{ return str.toLowerCase().includes('modo') });
                let formatar = deviceData.valueList[indice_formatar];
                deviceData.valueList[indice_formatar] = formatar == '1'?'Ligado':'Desligado';
            }*/

            props.updateDevice(deviceInfo);
        })
        .catch((err) => props.updateErrorMsg("O servidor respondeu o comando com: "+err.response.data));
    }

    if(props.device.type == 'sensor_temperatura' || props.device.type == 'sensor_trafego'){
        return(
            <div><p>Sem Comandos!</p></div>
        )
    }else if(props.device.type == 'semaforo'){
        let values = props.device.value;
        let names = props.device.value_name;

        let tempoVerde = values[names.findIndex((value) =>{ return value.toLowerCase().includes('verde')})];
        let tempoAmarelo = values[names.findIndex((value) =>{ return value.toLowerCase().includes('amarelo')})];
        let tempoVermelho = values[names.findIndex((value) =>{ return value.toLowerCase().includes('vermelho')})];

        return(
            <div>
                <button onClick={() => enviarComando('DESLIGAR', props.device.device_id, '')}>Desligar</button>
                <button onClick={() => enviarComando('LIGAR', props.device.device_id, '')}>Ligar</button>
                <label htmlFor={`paramgreen${props.device.device_id}`}>Tempo verde: </label><input type="number" defaultValue={tempoVerde} name={`paramgreen${props.device.device_id}`} id={`paramgreen${props.device.device_id}`} onChange={(e) =>{
                    enviarComando('AJUSTAR_TEMPO', props.device.device_id, `VERDE=${e.target.value}`);
                }}/>
                <label htmlFor={`paramyellow${props.device.device_id}`}>Tempo amarelo: </label><input type="number" defaultValue={tempoAmarelo} name={`paramyellow${props.device.device_id}`} id={`paramyellow${props.device.device_id}`} onChange={(e) =>{
                    enviarComando('AJUSTAR_TEMPO', props.device.device_id, `AMARELO=${e.target.value}`);
                }}/>
                <label htmlFor={`paramred${props.device.device_id}`}>Tempo vermelho: </label><input type="number" defaultValue={tempoVermelho} name={`paramred${props.device.device_id}`} id={`paramred${props.device.device_id}`} onChange={(e) =>{
                    enviarComando('AJUSTAR_TEMPO', props.device.device_id, `VERMELHO=${e.target.value}`);
                }}/>
            </div>
        )
    }else if(props.device.type == 'poste'){
        let brilho = props.device.value[props.device.value_name.findIndex((value) =>{ return value.toLowerCase().includes('brilho')})];

        return(
            <div>
                <button onClick={() => enviarComando('DESLIGAR', props.device.device_id, '')}>Desligar</button>
                <button onClick={() => enviarComando('LIGAR', props.device.device_id, '')}>Ligar</button>
                <button onClick={() => enviarComando('MODO_AUTOMATICO', props.device.device_id, '')}>Modo automático</button>
                <button onClick={() => enviarComando('MODO_MANUAL', props.device.device_id, '')}>Modo manual</button>
                <label htmlFor={`brilho${props.device.device_id}`}>Alterar brilho: </label><input type="number" defaultValue={brilho} name={`brilho${props.device.device_id}`} id={`brilho${props.device.device_id}`} onChange={(e) =>{
                    enviarComando('ALTERAR_BRILHO', props.device.device_id, e.target.value);
                }}/>
            </div>
        )
    }else if(props.device.type == 'lixeira_inteligente'){
        return(
            <div>
                <button onClick={() => enviarComando('DESLIGAR', props.device.device_id, '')}>Desligar</button>
                <button onClick={() => enviarComando('LIGAR', props.device.device_id, '')}>Ligar</button>
                <button onClick={() => enviarComando('GERAR_RELATORIO', props.device.device_id, '')}>Gerar relatório</button>
            </div>
        )
    }

    return(
        <div>
            <p>Nenhum comando encontrado</p>
        </div>
    )
}

export default SendCommand;