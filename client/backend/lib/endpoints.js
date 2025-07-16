// Função pra organizar os endpoints num lugar separado e deixar um pouco mais legível
import { handleComando } from "./handlerComando";
export function setEndpoints(app){
    app.server.get('/api/dispositivos', (req, res) =>{
        try{
            let command = {
                device_id: "GATEWAY",
                action: "LISTAR",
                parameter: ""
            }
            res.send(JSON.stringify(
                {
                    devices: app.devicesList.getDevices()
                }
            ))
        }catch(err){
            res.status(500).send("Erro inesperado ao enviar mensagem para o gateway: "+err.message);
        }
    })


    app.server.post('/api/comando', (req, res) =>{
        const data = req.body;

        try{
            endereco = app.devicesList.getDevice(data.device_id).grpc_endpoint;
            let command = {
                action: data.action,
                parameter: data.parameter
            }

            handleComando(endereco, command, (err, retorno) => {
                if (err) {
                    // tratamento erro
                }
                else {
                    // aqui vai ser adicionado o objeto
                    app.devicesList.addDevice();
                }
                
            });
            
        }catch(e){
            res.status(500).send("Erro inesperado ao enviar comando para o gateway: "+err.message);
        }
    })

    app.server.get('/', (req, res) =>{
        res.sendFile('/index.html', {root: '/dist'});
    })
}