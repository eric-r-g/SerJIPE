const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');


const packageDefinition = protoLoader.loadSync("serjipe_message.proto",{
  keepCase: true,
  longs: Number,        
  enums: String,        
  defaults: true,      
})

const serjipe = grpc.loadPackageDefinition(packageDefinition);

function callback(err, retorno){
    if (err) {
        // tratamento de erro devido
    }
    else {
        // atualiza com o deviceInfo devido
    }
}

function handleComando(endereco, acao, parametro, callback){
    const client = new serjipe.ControleDispositivosService(
        endereco,
        grpc.credentials.createInsecure()
    );

    const command = {
        action: acao,
        parameter: parametro
    }

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