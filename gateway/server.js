import App from './lib/app.js';

const PORT_FRONTEND = 8003;

try{
    const app = new App('../../gateway/main.py');

    app.listen(PORT_FRONTEND, () =>{
        console.log(`Server listening on http://localhost:${PORT_FRONTEND}`);
    })
}catch(err){
    console.trace(err);
}