const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');


const packageDefinition = protoLoader.loadSync("serjipe_message.proto",{
  keepCase: true,
  longs: Number,        
  enums: String,        
  defaults: true,      
})

const serjipe = grpc.loadPackageDefinition(packageDefinition);

async function handleComando(endereco, acao, parametro){
    const client = new serjipe.ControleDispositivosService(
    endereco,
    grpc.credentials.createInsecure()
    );

    try{
        const command = {
            action: acao,
            parameter: parametro
        }
        const response = await new Promise((resolve, reject) => {
            client.EnviarComando(command, (err, retorno) => {
                if (err) reject(err);
                else resolve(retorno);
            });
        });

        return response;
    } catch (err) {
        // lida com o erro
    } finally {
        client.close()
    }
}