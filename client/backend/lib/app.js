import express from 'express';
import { createRequire } from 'module';
import { sendTCPData } from './socket_functions';
const require = createRequire(import.meta.url);

const messages = require('./serjipe_message_pb.cjs');
const gatewayPort = 8001;
const app = express();

// Listar todos os dispositivos
app.get('/api/dispositivos', (req, res) =>{
    const comando = new messages.Command();
    comando.setDeviceId(''); comando.setAction('MULTICAST'); comando.setParameter('');

    sendTCPData(gatewayPort, comando.serializeBinary())
    .then((response) =>{
        let dispositivos = messages.ListarDispositivos.deserializeBinary(response);
        res.send(JSON.stringify(dispositivos.toObject()));
    })
    .catch((err) => res.status(505).send(err.message));
})

// Pegar info de um dispositivo
app.get('/api/dispositivos/:id', (req, res) =>{
    let device_id = req.params.id;

    // não temos ainda decidido um comando pra pegar a informação de só um dispositivo
})

// Enviar comando qualquer
    /*
        requisição:
        {
            device_id: string,
            action: string,
            parameter: string
        }
    */
app.post('/api/comando', (req, res) =>{
    const comando = new messages.Command();

    const data = req.body.data;
    comando.setDeviceId(data.device_id); comando.setAction(data.action); comando.setParameter(data.parameter);

    sendTCPData(gatewayPort, comando.serializeBinary())
    .then((response) =>{
        let device_info = messages.DeviceInfo.deserializeBinary(response); //a ideia aqui seria o gateway devolver a informação do dispositivo, da pra mudar dps
        res.send(JSON.stringify(device_info.toObject()));
    })
    .catch((err) => res.status(505).send(err.message));
})

export default app;