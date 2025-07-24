import Net from 'net';
import dgram from 'dgram';

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

export function sendDataMulticast(port, group, data){
    try{
        const socket = dgram.createSocket('udp4');
        socket.bind(() =>{
            //socket.setMulticastInterface(group); // não sei por que isso não foi necessário

            socket.send(data, port, group, (err) =>{
                if(err) throw err;
                socket.close();
            });
        })



    }catch(err){
        throw err;
    }
}

// Retorna um array com todas as mensagens recebidas no tempo
export function listenToMulticast(port, group, ms){
    return new Promise((resolve, reject) =>{
        let devices = [];
        
        try{
            const socket = dgram.createSocket('udp4');

            socket.on('message', (msg) =>{
                devices.push(msg);
            })

            socket.bind(port, () =>{
                socket.addMembership(group);

                setTimeout(() =>{
                    socket.close();
                    resolve(devices);
                }, ms);
            });
        }catch(err){
            reject("Erro na criação do socket UDP:" + err.message);
        }
    })

}