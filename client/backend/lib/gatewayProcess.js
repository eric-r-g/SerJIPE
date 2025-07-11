import { spawn } from 'node:child_process';

// classe pro subprocesso do Gateway
class Gateway{
    constructor(gatewayPath){
        try{
            process = spawn('python', ['-u', gatewayPath], {serialization: 'json'});
        }catch(err){
            throw err;
        }

        process.on('close', () => {
            throw new Error("O gateway não iniciou ou foi encerrado de forma inesperada");
        });

        process.stdout.setDefaultEncoding('utf-8');

        process.stdin.setKeepAlive(true);
    }

    sendMessage(message){
        process.stdin.write(message);
        process.stdin.write('\n');

        return new Promise((resolve, reject) => {

            function handleData(data){
                resolve(data); // ToDo: fazer checagem da mensagem antes de dar esse resolve
                process.stdout.off('data', handleData);
            }

            process.stdout.on('data', handleData);
        });
        
    }
    
    startListening(callback){ // Só pra debug
        process.stdout.on('data', (data) => callback(data));
    }
    stopListening(){
        process.stdout.off('data');
    }
}

export default Gateway;