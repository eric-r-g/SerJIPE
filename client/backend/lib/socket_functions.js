import Net from 'net';

// Enviar mensagem com um socket TCP
export function sendTCPData(port, data){
    return new Promise((resolve, reject) =>{
        try{
            const socket = new Net.Socket();
            socket.setTimeout(5000);

            socket.connect({port: port, host: 'localhost'}, () =>{
                try{
                    socket.write(data);
                }catch(err){
                    reject(`Erro ao enviar mensagem para o gateway no port ${port}: ${err.message}`);
                }
                socket.on('data', (message) =>{
                    socket.end();
                    resolve(message);
                })

            })

            socket.on('error', (err) => reject(`Erro ao se conectar com o gateway no port ${port}: ${err.code}`));

            socket.on('timeout', () => {
                socket.end();
                reject("O gateway demorou muito para responder (TIMEOUT)");
            })

        }catch(err){
            reject("Erro na criação do socket TCP: "+err.message);
        }
    });
}