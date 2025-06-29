import express from 'express';
import { createRequire } from 'module';
import { sendTCPData } from './socket_functions.js';
const require = createRequire(import.meta.url);

const messages = require('./serjipe_message_pb.cjs');
const gatewayPort = 8000;
const app = express();

// Listar todos os dispositivos
app.get('/api/dispositivos', (req, res) =>{
    const comando = new messages.Command();
    comando.setDeviceId('GATEWAY'); comando.setAction('LISTAR'); comando.setParameter('');

    try{
        sendTCPData(gatewayPort, comando.serializeBinary())
        .then((response) =>{
            let dispositivos = messages.ListarDispositivos.deserializeBinary(response);
            res.send(JSON.stringify(dispositivos.toObject()));
        })
        .catch((err) => res.status(500).send(err.message));
    }catch(e){
        res.status(500).send(err.message);
    }
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

    try{
        sendTCPData(gatewayPort, comando.serializeBinary())
        .then((response) =>{
            let device_data = messages.DeviceData.deserializeBinary(response);
            res.send(JSON.stringify(device_data.toObject()));
        })
        .catch((err) => res.status(500).send(err.message));
    }catch(e){
        res.status(500).send(err.message);
    }
})

export default app;