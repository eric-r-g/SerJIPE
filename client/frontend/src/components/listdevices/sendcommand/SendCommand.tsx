//import type { Command, DeviceInfo } from "../../../lib/interfaces.ts";
//import axios from "axios";
//import { getAxiosConfig } from "../../../lib/utils.ts";

/*interface SendCommandProps{
    device: DeviceInfo,
    updateDevice: (device: DeviceInfo) => void;
    updateErrorMsg: (newErrorMsg: string) => void;
}*/
function SendCommand(){

    /*function enviarComando(action: string, deviceId: string, parameter: string){
        let data = {
            action: action,
            deviceId: deviceId,
            parameter: parameter
        } as Command;

        axios.request(getAxiosConfig(data, '/api/comando', 'POST'))
        .then((response) =>{
            let deviceInfo = {
                device_id: response.data.deviceId,
                status: response.data.status,
                value_name: response.data.valueNameList,
                value: response.data.valueList
            } as DeviceInfo;*/

            /*if(props.device.type == 'sensor_trafego'){
                let indice_formatar = deviceData.valueNameList.findIndex((str) =>{ return str.toLowerCase().includes('congestionamento') });
                let formatar = deviceData.valueList[indice_formatar];
                deviceData.valueList[indice_formatar] = Number(formatar).toFixed(1);
            }else if(props.device.type == 'poste'){
                let indice_formatar = deviceData.valueNameList.findIndex((str) =>{ return str.toLowerCase().includes('modo') });
                let formatar = deviceData.valueList[indice_formatar];
                deviceData.valueList[indice_formatar] = formatar == '1'?'Ligado':'Desligado';
            }*/

            /*props.updateDevice(deviceInfo);
        })
        .catch((err) => props.updateErrorMsg("O servidor respondeu o comando com: "+err.response.data));
    }*/

    /*if(props.device.type == 'sensor_temperatura' || props.device.type == 'sensor_trafego'){
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
    }else if(props.device.type == 'semaforo'){
        let data = props.device.data;

        let tempoVerde = data.valueList[data.valueNameList.findIndex((value) =>{ return value.toLowerCase().includes('verde')})];
        let tempoAmarelo = data.valueList[data.valueNameList.findIndex((value) =>{ return value.toLowerCase().includes('amarelo')})];
        let tempoVermelho = data.valueList[data.valueNameList.findIndex((value) =>{ return value.toLowerCase().includes('vermelho')})];

        return(
            <div>
                <button onClick={() => enviarComando('DESLIGAR', props.device.deviceId, '')}>Desligar</button>
                <button onClick={() => enviarComando('LIGAR', props.device.deviceId, '')}>Ligar</button>
                <label htmlFor={`paramgreen${props.device.deviceId}`}>Tempo verde: </label><input type="number" defaultValue={tempoVerde} name={`paramgreen${props.device.deviceId}`} id={`paramgreen${props.device.deviceId}`} onChange={(e) =>{
                    enviarComando('AJUSTAR_TEMPO', props.device.deviceId, `VERDE=${e.target.value}`);
                }}/>
                <label htmlFor={`paramyellow${props.device.deviceId}`}>Tempo amarelo: </label><input type="number" defaultValue={tempoAmarelo} name={`paramyellow${props.device.deviceId}`} id={`paramyellow${props.device.deviceId}`} onChange={(e) =>{
                    enviarComando('AJUSTAR_TEMPO', props.device.deviceId, `AMARELO=${e.target.value}`);
                }}/>
                <label htmlFor={`paramred${props.device.deviceId}`}>Tempo vermelho: </label><input type="number" defaultValue={tempoVermelho} name={`paramred${props.device.deviceId}`} id={`paramred${props.device.deviceId}`} onChange={(e) =>{
                    enviarComando('AJUSTAR_TEMPO', props.device.deviceId, `VERMELHO=${e.target.value}`);
                }}/>
            </div>
        )
    }else if(props.device.type == 'poste'){
        let brilho = props.device.data.valueList[props.device.data.valueNameList.findIndex((value) =>{ return value.toLowerCase().includes('brilho')})];

        return(
            <div>
                <button onClick={() => enviarComando('DESLIGAR', props.device.deviceId, '')}>Desligar</button>
                <button onClick={() => enviarComando('LIGAR', props.device.deviceId, '')}>Ligar</button>
                <button onClick={() => enviarComando('MODO_AUTOMATICO', props.device.deviceId, '')}>Modo automático</button>
                <button onClick={() => enviarComando('MODO_MANUAL', props.device.deviceId, '')}>Modo manual</button>
                <label htmlFor={`brilho${props.device.deviceId}`}>Alterar brilho: </label><input type="number" defaultValue={brilho} name={`brilho${props.device.deviceId}`} id={`brilho${props.device.deviceId}`} onChange={(e) =>{
                    enviarComando('ALTERAR_BRILHO', props.device.deviceId, e.target.value);
                }}/>
            </div>
        )
    }else if(props.device.type == 'lixeira_inteligente'){
        return(
            <div>
                <button onClick={() => enviarComando('DESLIGAR', props.device.deviceId, '')}>Desligar</button>
                <button onClick={() => enviarComando('LIGAR', props.device.deviceId, '')}>Ligar</button>
                <button onClick={() => enviarComando('GERAR_RELATORIO', props.device.deviceId, '')}>Gerar relatório</button>
            </div>
        )
    }*/

    return(
        <div>
            <p>Nenhum comando encontrado</p>
        </div>
    )
}

export default SendCommand;