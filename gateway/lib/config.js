import dns from 'dns';
import os from 'os';

export const MULTICAST_GROUP = '239.1.2.3';
export const PORT_MULTICAST = 5000;
export const PORT_MULTICAST_RESPOSTA = 4444;
export const PORT_UDP_SENSOR = 7000;
export const sensoresType = ['temperatura', 'trafego'];

export function getLocalIp(){
    return new Promise((resolve, reject) =>{
        dns.lookup(os.hostname(), { family: 4 }, (err, addr) =>{
            if(err) reject(err);
            else resolve(addr);
        })
    })
}