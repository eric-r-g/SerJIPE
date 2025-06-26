import server from './lib/app.js';

const PORT = 8003;

server.listen(PORT, () =>{
    console.log('server listening on http://localhost:'+PORT);
})