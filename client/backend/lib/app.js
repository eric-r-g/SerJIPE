import express from 'express';
import Gateway from './gatewayProcess.js';
import { setEndpoints } from './endpoints.js';

import amqp from 'amqplib'

amqp.connect()

// Classe pro app, incluindo o subprocesso do gateway
class App {
    server;
    gateway;
    constructor(gatewayPath){
        this.server = express();

        try{
            this.gateway = new Gateway(gatewayPath)
        }catch(err){
            throw err;
        }

        /*ToDo:
            Criação da conexão com o rabbitmq
                fazer reconexão caso a conexão seja fechada
                    (connection emite um 'close' quando a conexão é fechada, daí da pra reconectar direto ou botar um timeout. Quando um erro é emitido nem sempre ele emite um close então ficar de olho)
                Criação dos SensorReceiver feito aqui, um pra cada fila, lembrar de recriar eles caso a conexão caia
            
            Setar timeout pra ficar mandando multicast aqui, escutar aqui tbm
            O devicesList tem que ficar aqui tbm
        */

        this.server.use(express.static('dist'));
        this.server.use(express.json());

        setEndpoints(this);
    }

    listen(PORT, callback){
        this.server.listen(PORT, callback());
    }
}

export default App;