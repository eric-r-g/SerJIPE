// Função pra organizar os endpoints num lugar separado e deixar um pouco mais legível
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
            let command = {
                device_id: data.device_Id,
                action: data.action,
                parameter: data.parameter
            }
            // ToDo: enviar comando com grpc
        }catch(e){
            res.status(500).send("Erro inesperado ao enviar comando para o gateway: "+err.message);
        }
    })

    app.server.get('/', (req, res) =>{
        res.sendFile('/index.html', {root: '/dist'});
    })
}