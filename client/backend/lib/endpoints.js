// Mudar o nome desse arquivo se fizer mais sentido

import { createRequire } from 'module';
import { sendTCPData } from './socket_functions.js';

// Função pra organizar os endpoints num lugar separado e deixar um pouco mais legível
export function setEndpoints(server){
    const gatewayPort = 8000;

    const require = createRequire(import.meta.url);
    const messages = require('./serjipe_message_pb.cjs');

    // Listar todos os dispositivos
    server.get('/api/dispositivos', (req, res) =>{
        const comando = new messages.Command();
        comando.setDeviceId('GATEWAY'); comando.setAction('LISTAR'); comando.setParameter('');

        const envelope = new messages.Envelope();
        envelope.setCommand(comando);

        try{
            sendTCPData(gatewayPort, envelope.serializeBinary())
            .then((response) =>{
                let envelopeRes = messages.Envelope.deserializeBinary(response);

                if(envelopeRes.getErro() == "FALHA"){
                    console.log('falha')
                    res.status(500).send("Um erro ocorreu");
                }
                else if(envelopeRes.getCargaCase() == 5){
                    let dispositivos = envelopeRes.getListarDispositivos();

                    if(parseInt(dispositivos.getAmount()) > 0){
                        res.send(JSON.stringify(dispositivos.toObject()));
                    }else{
                        res.send(JSON.stringify({devicesList: []}));
                    }

                }else{
                    res.send("O cliente recebeu um tipo de mensagem protobuf inesperada");
                }
            })
            .catch((err) => res.status(500).send(err));
        }catch(e){
            res.status(500).send("Erro inesperado ao enviar mensagem para o gateway: "+err.message);
        }
    })

    // Enviar comando qualquer
        /*
            requisição:
            {
                deviceId: string,
                action: string,
                parameter: string
            }
        */
    server.post('/api/comando', (req, res) =>{
        const comando = new messages.Command();

        const data = req.body;
        comando.setDeviceId(data.deviceId); comando.setAction(data.action); comando.setParameter(data.parameter);

        const envelope = new messages.Envelope();
        envelope.setCommand(comando);

        try{
            sendTCPData(gatewayPort, envelope.serializeBinary())
            .then((response) =>{
                let envelopeRes = messages.Envelope.deserializeBinary(response);

                if(envelopeRes.getErro() == "FALHA"){
                    res.status(500).send("Um erro ocorreu");
                }
                else if(envelopeRes.getCargaCase() == 3){
                    let deviceData = envelopeRes.getDeviceData();

                    res.send(JSON.stringify(deviceData.toObject()));
                }else{
                    res.send("O cliente recebeu um tipo de mensagem protobuf inesperada");
                }
            })
            .catch((err) => res.status(500).send(err));
        }catch(e){
            res.status(500).send("Erro inesperado ao enviar comando para o gateway: "+err.message);
        }
    })

    server.get('/', (req, res) =>{
        res.sendFile('/index.html', {root: '/dist'});
    })
}