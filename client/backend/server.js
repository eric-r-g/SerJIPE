import App from './lib/app.js';

const PORT = 8003;

try{
    const app = new App('../../gateway/main.py');

    app.listen(PORT, () =>{
        console.log(`Server listening on http://localhost:${PORT}`);
    })
}catch(err){
    console.trace(err);
}