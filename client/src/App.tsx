import { useEffect, useState } from 'react'
import './App.css'
import ListDevices from './components/listdevices/ListDevices.tsx'
import type { DeviceInfo } from './lib/interfaces.ts';
import logo from '/JIPElogo.png';
import axios from 'axios';
import { getAxiosConfig } from './lib/utils.ts';

function App() {
  const [devices, setDevices] = useState(new Array<DeviceInfo>());
  const [warning, setWarning] = useState("Nenhum aviso!");
  const [errorMsg, setErrorMsg] = useState("Nenhum erro");

  useEffect(() =>{
    requestDevicesList();
    const updateInterval = setInterval(() =>{
        requestDevicesList();
    }, 5000);

    return () => clearInterval(updateInterval);
  }, []);

  function requestDevicesList(){
    axios.request(getAxiosConfig(null, '/api/dispositivos', 'GET'))
    .then((response) =>{
        updateWarning(`Ultima atualização em ${new Date().toLocaleString()}`);
        let list = (response.data.devices) as Array<DeviceInfo>;

        // Formatar e organizar a lista antes de atualizar
        //list.sort((a, b) => a.port - b.port);
        list = list.map((dispositivo) =>{
            /*if(dispositivo.type == 'sensor_trafego'){
                let indice_formatar = dispositivo.data.valueNameList.findIndex((str) =>{ return str.toLowerCase().includes('congestionamento') });
                let formatar = dispositivo.data.valueList[indice_formatar];
                dispositivo.data.valueList[indice_formatar] = Number(formatar).toFixed(1);
            }else if(dispositivo.type == 'poste'){
                let indice_formatar = dispositivo.data.valueNameList.findIndex((str) =>{ return str.toLowerCase().includes('modo') });
                let formatar = dispositivo.data.valueList[indice_formatar];
                dispositivo.data.valueList[indice_formatar] = formatar == '1'?'Ligado':'Desligado';
            }*/

            return dispositivo;
        })
        updateDevices(list);
    })
    .catch((err) => setErrorMsg(`O servidor respondeu a requisição em ${new Date().toLocaleString()} com: ${err.response.data}`));
  }

  // Update all devices
  function updateDevices(devices: Array<DeviceInfo>){
    setDevices(devices);
  }

  // Update single
  function updateDevice(deviceInfo: DeviceInfo){
    let newDevices = [...devices];
    let index = newDevices.findIndex((deviceTofind) =>{ return deviceTofind.device_id == deviceInfo.device_id});
    newDevices[index] = deviceInfo;

    console.log(deviceInfo);

    setDevices(newDevices);
  }

  function updateWarning(newWarning: string){
    setWarning(newWarning);
  }

  function updateErrorMsg(newErrorMsg: string){
    setErrorMsg(newErrorMsg);
  }

  return (
    <div id='main-grid'>
        <div id="header-div">
            <header id='header'>
                <div id='center-img'>
                    <img src={logo} alt="Logo SerJIPE" />
                </div>
            </header>
            <div id='warning'>
                <p>{warning}</p>
                <p style={{color: 'rgb(255, 119, 119)'}}>{errorMsg}</p>
            </div>
        </div>
        <ListDevices devices={devices} updateDevice={updateDevice} updateErrorMsg={updateErrorMsg}/>
    </div>
  )
}

export default App
