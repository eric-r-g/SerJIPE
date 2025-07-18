import express from 'express';
import amqp from 'amqplib';
import { setEndpoints } from './endpoints.js';
import { DeviceList } from './devicesList.js';
import { listenToMulticast, sendDataMulticast } from './socket_functions.js';
import { getLocalIp, MULTICAST_GROUP, PORT_MULTICAST, PORT_MULTICAST_RESPOSTA, sensoresType } from './config.js';
import { SensorReceiver } from './SensorReceiver.js';

function createConnection(app){
    return new Promise((resolve, reject) =>{
        amqp.connect('amqp://localhost')
        .then((connection) =>{
            // Eventos da conexão

            // Se a conexão cair, tentar reconectar
            // Uma possibilidade pra organizar isso aqui melhor é fazer a função de reconectar como um método, ai deixa o server.js chamar ele e definir o tempo de reconexão
            connection.on('close', () =>{
                app.channels = [];
                setTimeout(() =>{ 
                    createConnection()
                    .then((connection) =>{
                        app.connection = connection;
                        app.channels = createQueues(app.connection, sensoresType);
                    })
                    .catch((err) => { throw err }); // No momento ele só tenta se reconectar uma vez, se quiser tentar dnv fazer nesse catch, ou setar um interval e limpar dps(no catch tbm)
                }, 3000);
            })
            connection.on('error', (err) =>{
                app.channels = [];
                throw err;
            })

            resolve(connection);
        })
        .catch((err) => {throw err});
    });
}
function createQueues(connection, types, app){
    let channels = [];
    for(let i = 0; i < types.length; i++){
        try{
            let channel = new SensorReceiver(connection, types[i], (data) =>{
                /*
                    Assumindo que vou receber umm json no formato:
                    {
                            string device_id = 1;            //  "LIX_1234
                            string status = 4;               //  "ON", "OFF", "ERROR"
                            repeated string value_name = 5;  //  "{temperatura, tempo de espera}"
                            repeated string value = 6;       //  "{25.5 , 5s}"
                    }
                */

                let obj = JSON.parse(data.content.toString());
                let toAdd = {
                    device_id: obj.device_id,
                    status: obj.status,
                    value_name: obj.value_name,
                    value: obj.value,
                    timestamp: obj.timestamp
                }

                app.devicesList.addDevice(toAdd);

                channel.channel.ack(data, true);
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
            getLocalIp().then((ip) => {this.localIp = ip}).catch((err) => {throw err})// temp
            createConnection(this)
            .then((connection) =>{
                this.connection = connection;
                this.channels = createQueues(this.connection, sensoresType, this);
            })
            .catch((err) => { throw err });
        }catch(err){
            throw err;
        }



        // Endpoints da API do express
        this.server.use(express.static('dist'));
        this.server.use(express.json());
        setEndpoints(this);

        // Isso aqui também pode virar um método, pra dai chamar no server.js
        setInterval(() =>{

           let data = {
                gateway_ip: this.localIp,
                gateway_port: PORT_MULTICAST_RESPOSTA,
                broker_info:{
                    host: this.localIp,
                    queue: sensoresType
                }
           }

            sendDataMulticast(PORT_MULTICAST, MULTICAST_GROUP, JSON.stringify(data));

            listenToMulticast(PORT_MULTICAST_RESPOSTA, MULTICAST_GROUP, 3000)
            .then((devices) =>{
                devices.forEach((device) =>{
                    /*
                        Assumindo que vou receber umm json no formato:
                        {
                                string device_id = 1;            //  "LIX_1234
                                string type = 2;                 //  "sensor", "atuador"
                                string grpc_endpoint = 3;        //  "localhost:50051"
                                string status = 4;               //  "ON", "OFF", "ERROR"
                                repeated string value_name = 5;  //  "{temperatura, tempo de espera}"
                                repeated string value = 6;       //  "{25.5 , 5s}"
                        }
                    */
                   let obj = JSON.parse(device);
                   let toAdd = {
                        device_id: obj.device_id,
                        type: obj.type,
                        grpc_endpoint: obj.grpc_endpoint,
                        status: obj.status,
                        value_name: obj.value_name,
                        value: obj.value
                   }

                   this.devicesList.addDevice(toAdd);
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