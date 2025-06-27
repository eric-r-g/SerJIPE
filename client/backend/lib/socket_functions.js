import Net from 'net';

// Enviar mensagem com um socket TCP
export function sendTCPData(port, data){
    return new Promise((resolve, reject) =>{
        try{
            const socket = new Net.Socket();
            socket.connect({port: port, host: 'localhost'}, () =>{
                socket.write(data);
                socket.on('data', (message) =>{
                    socket.end();
                    resolve(message);
                })
            })
        }catch(err){
            reject(err);
        }
    });
}