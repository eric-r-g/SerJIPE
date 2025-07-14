export class SensorReceiver{
    channel;
    constructor(connection, queue, callback){
        this.connection = connection;

        connection.createChannel((err, channel) =>{
            if(err) throw err;

            this.channel = channel;
            channel.assertQueue(queue, { durable: true });

            channel.consume(queue, callback(msg));
        })
    }
}