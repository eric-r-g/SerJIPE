import express from 'express';
import amqp from 'amqplib';
import { setEndpoints } from './endpoints.js';
import { DeviceList } from './devicesList.js';
import { listenToMulticast, sendDataMulticast } from './socket_functions.js';
import { getLocalIp, MULTICAST_GROUP, PORT_MULTICAST, PORT_MULTICAST_RESPOSTA, sensoresType } from './config.js';
import { createRequire } from 'module';
import { SensorReceiver } from './SensorReceiver.js';

const require = createRequire(import.meta.url);
const messages = require('./serjipe_message_pb.cjs');

function createConnection(){
    return new Promise((resolve, reject) =>{
        amqp.connect('amqp://localhost', (err, connection) =>{
            if(err) reject(err);
            resolve(connection);
        })
    });
}
function createQueues(connection, types){
    let channels = [];
    for(let i = 0; i < types.length; i++){
        try{
            let channel = new SensorReceiver(connection, types[i], (data) =>{
                let obj = JSON.parse(data);
                // ToDo: Atualizar devicesList, não sei ainda qual a estrutura desse json
                // Provavelmente passar esse callback pro construtor do app
            })
            channels.push(channel);
        }catch(err){
            console.log(`Erro ao criar a fila ${types[i]}: ${err}`);
        }
    }
    return channels;
}

// Classe pro app
class App {
    server;
    devicesList;
    localIp;
    connection;
    channels;

    constructor(){
        // Criação dos objetos iniciais
        this.channels = [];
        this.devicesList = new DeviceList();
        this.server = express();

        try{
            this.localIp = getLocalIp();
            createConnection()
            .then((connection) =>{
                this.connection = connection;
                this.channels = createQueues(this.connection, sensoresType);
            })
            .catch((err) => { throw err });
        }catch(err){
            throw err;
        }

        // Se a conexão cair, tentar reconectar
        // Uma possibilidade pra organizar isso aqui melhor é fazer a função de reconectar como um método, ai deixa o server.js chamar ele e definir o tempo de reconexão
        this.connection.on('close', () =>{
            this.channels = [];
            setTimeout(() =>{ 
                createConnection()
                .then((connection) =>{
                    this.connection = connection;
                    this.channels = createQueues(this.connection, sensoresType);
                })
                .catch((err) => { throw err }); // No momento ele só tenta se reconectar uma vez, se quiser tentar dnv fazer nesse catch, ou setar um interval e limpar dps(no catch tbm)
            }, 3000);
        })
        this.connection.on('error', (err) =>{
            this.channels = [];
            throw err;
        })

        // Endpoints da API do express
        this.server.use(express.static('dist'));
        this.server.use(express.json());
        setEndpoints(this);

        // Isso aqui também pode virar um método, pra dai chamar no server.js
        setInterval(() =>{
            const discover = new messages.Discover();

            // ToDo: Definir o discover

            sendDataMulticast(PORT_MULTICAST, MULTICAST_GROUP, discover.serializeBinary());

            listenToMulticast(PORT_MULTICAST_RESPOSTA, MULTICAST_GROUP, 3000)
            .then((devices) =>{
                devices.forEach((device) =>{
                    // ToDo: Atualizar devicesList, não sei ainda se a resposta vai ser protobuf, creio que sim
                })
            })
            .catch((err) => console.log("Erro ao ouvir respostas do multicast: " + err));
        }, 5000);
    }

    listen(PORT, callback){
        this.server.listen(PORT, callback());
    }
}

export default App;