// Mudar o nome desse arquivo se fizer mais sentido
// ToDo: Tem várias coisas comentadas que vou deixar por enquanto mas da pra tirar tudo

//import { createRequire } from 'module';

// Função pra organizar os endpoints num lugar separado e deixar um pouco mais legível
export function setEndpoints(app){
    //const gatewayPort = 8000;

    //const require = createRequire(import.meta.url);
    //const messages = require('./serjipe_message_pb.cjs');

    // Listar todos os dispositivos
    app.server.get('/api/dispositivos', (req, res) =>{
        /*const comando = new messages.Command();
        comando.setDeviceId('GATEWAY'); comando.setAction('LISTAR'); comando.setParameter('');

        const envelope = new messages.Envelope();
        envelope.setCommand(comando);*/

        try{
            /*sendTCPData(gatewayPort, envelope.serializeBinary())
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
            .catch((err) => res.status(500).send(err));*/
            let command = {
                device_id: "GATEWAY",
                action: "LISTAR",
                parameter: ""
            }

            app.gateway.sendMessage(JSON.stringify(command))
            .then((data) => res.send(data));
        }catch(err){
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
    app.server.post('/api/comando', (req, res) =>{
        const data = req.body;

        /*const comando = new messages.Command();

        comando.setDeviceId(data.deviceId); comando.setAction(data.action); comando.setParameter(data.parameter);

        const envelope = new messages.Envelope();
        envelope.setCommand(comando);*/

        try{
            /*sendTCPData(gatewayPort, envelope.serializeBinary())
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
            .catch((err) => res.status(500).send(err));*/
            let command = {
                device_id: data.device_Id,
                action: data.action,
                parameter: data.parameter
            }

            app.gateway.sendMessage(JSON.stringify(command))
            .then((data) => res.send(data));
        }catch(e){
            res.status(500).send("Erro inesperado ao enviar comando para o gateway: "+err.message);
        }
    })

    app.server.get('/', (req, res) =>{
        res.sendFile('/index.html', {root: '/dist'});
    })
}