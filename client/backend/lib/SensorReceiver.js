export class SensorReceiver{
    channel;
    constructor(connection, queue, callback){
        connection.createChannel()
        .then((channel) =>{
            this.channel = channel;
            channel.assertQueue(queue, { durable: true })
            .then(() =>{
                channel.consume(queue, callback);
            })
            .catch((err) => { throw err });
        })
        .catch((err) => { throw err });
    }
}