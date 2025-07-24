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
            resolve(connection);
        })
        .catch((err) => {reject(err)});
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
                            string device_id;            //  "LIX_1234
                            string status;               //  "ON", "OFF", "ERROR"
                            string type;
                            repeated string value_name;  //  "{temperatura, tempo de espera}"
                            repeated string value;       //  "{25.5 , 5s}"
                    }
                */

                let obj = JSON.parse(data.content.toString());
                let toAdd = {
                    device_id: obj.device_id,
                    status: obj.status,
                    type: obj.type,
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
    reconnectionInterval;

    constructor(){
        // Criação dos objetos iniciais
        this.channels = [];
        this.devicesList = new DeviceList();
        this.server = express();

        getLocalIp().then((ip) => {this.localIp = ip}).catch((err) => {throw err})// temp
            
        createConnection(this)
        .then((connection) =>{
            this.connection = connection;
            this.channels = createQueues(this.connection, sensoresType, this);

            // Eventos da conexão

            // Se a conexão cair, tentar reconectar
            // Uma possibilidade pra organizar isso aqui melhor é fazer a função de reconectar como um método, ai deixa o server.js chamar ele e definir o tempo de reconexão
            connection.on('close', () =>{
                console.log("Conexão com o RabbitMQ foi fechada, tentando reconectar em 5 segundos");
                this.channels = [];
                this.reconnectionInterval = setInterval(() =>{
                    createConnection()
                    .then((connection) =>{
                        this.connection = connection;
                        this.channels = createQueues(this.connection, sensoresType, this);

                        clearInterval(this.reconnectionInterval);
                    })
                    .catch(() =>{
                        console.log("Conexão com o RabbitMQ falhou, tentando novamente em 5 segundos");
                    })
                }, 5000);
            })

            connection.on('error', (err) =>{
                this.channels = [];
                throw err;
            })
        })
        .catch((err) => {
            if(err.code == "ECONNREFUSED"){
                console.log("Conexão com o RabbitMQ falhou, tentando novamente em 5 segundos");
                this.reconnectionInterval = setInterval(() =>{
                    createConnection()
                    .then((connection) =>{
                        this.connection = connection;
                        this.channels = createQueues(this.connection, sensoresType, this);

                        clearInterval(this.reconnectionInterval);
                    })
                    .catch(() =>{
                        console.log("Conexão com o RabbitMQ falhou, tentando novamente em 5 segundos");
                    })
                }, 5000);
            }else{
                throw err;  
            } 
        });



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
                let encontrados = [];
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

                    if(toAdd.value_name == undefined || toAdd.value == undefined)
                        this.devicesList.updateDeviceInfo(toAdd.device_id, toAdd);
                    else
                        this.devicesList.addDevice(toAdd);
                    encontrados.push(toAdd.device_id);
                })

                // Deletar os que não enviaram o multicast
                this.devicesList.getDevices().forEach((device) =>{
                    if(!encontrados.includes(device.device_id)){
                        this.devicesList.removeDevice(device);
                    } 
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