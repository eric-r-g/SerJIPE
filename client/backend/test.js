import amqp from '@types/amqplib';

amqp.connect("test")
.then((connection) =>{
    connection.createChannel()
    .then((channel) =>{
        channel.consume("queue", (msg) =>{
            channel.ack(msg, true);
        })
    })
})