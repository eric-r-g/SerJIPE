import { spawn } from 'node:child_process';

// classe pro subprocesso do Gateway
class Gateway{
    constructor(gatewayPath){
        try{
            process = spawn('python', ['-u', gatewayPath]);
        }catch(err){
            throw err;
        }

        process.on('close', () => {
            let err = new Error("O gateway não iniciou ou foi encerrado de forma inesperada")
            throw err;
        });

        process.stdout.setEncoding('utf-8');
        process.stderr.setEncoding('utf-8');
    }

    sendMessage(message){
        process.stdin.write(message);
        process.stdin.end();
    }
    
    startListening(callback){ // Talvez seja desnecessário fazer assim, qualquer coisa muda isso pro constructor
        process.stdout.on('data', (data) => callback(data));
        process.stderr.on('data', (data) => callback(data));
    }
    stopListening(){
        process.stdout.off('data');
        process.stderr.off('data');
    }
}

export default Gateway;