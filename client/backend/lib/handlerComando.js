const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');


const packageDefinition = protoLoader.loadSync("serjipe_message.proto",{
  keepCase: true,
  longs: Number,        
  enums: String,        
  defaults: true,      
})

const serjipe = grpc.loadPackageDefinition(packageDefinition);

export function handleComando(endereco, command, callback){
    const client = new serjipe.ControleDispositivosService(
        endereco,
        grpc.credentials.createInsecure()
    );

    client.EnviarComando(command, (err, retorno) => {
        client.close();

        if (err) { 
            callback(err);
        }
        else {
            callback(null, retorno);
        }
    });
}