import express from 'express';
import { createRequire } from 'module';
import { sendTCPData } from './socket_functions.js';
import bodyParser from 'body-parser';
const require = createRequire(import.meta.url);

const messages = require('./serjipe_message_pb.cjs');
const gatewayPort = 8000;
const app = express();

app.use(express.static('dist'));

app.get('/', (req, res) =>{
    res.sendFile('/index.html', {root: '/dist'});
})

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
        .catch((err) => res.status(500).send(err));
    }catch(e){
        res.status(500).send(err.code);
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
app.post('/api/comando', bodyParser.json(), (req, res) =>{
    const comando = new messages.Command();

    const data = req.body;
    comando.setDeviceId(data.deviceId); comando.setAction(data.action); comando.setParameter(data.parameter);

    try{
        sendTCPData(gatewayPort, comando.serializeBinary())
        .then((response) =>{
            let device_data = messages.DeviceData.deserializeBinary(response);
            res.send(JSON.stringify(device_data.toObject()));
        })
        .catch((err) => res.status(500).send(err));
    }catch(e){
        res.status(500).send(err.code);
    }
})

export default app;