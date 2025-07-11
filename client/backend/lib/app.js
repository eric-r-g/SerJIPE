import express from 'express';
import Gateway from './gatewayProcess.js';
import { setEndpoints } from './endpoints.js';

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

        this.server.use(express.static('dist'));
        this.server.use(express.json());

        setEndpoints(this);
    }

    listen(PORT, callback){
        this.server.listen(PORT, callback());
    }
}

export default App;