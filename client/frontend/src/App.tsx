import { useEffect, useState } from 'react'
import './App.css'
import ListDevices from './components/listdevices/ListDevices.tsx'
import type { DeviceData, DeviceInfo } from './lib/interfaces.ts';
import logo from '/JIPElogo.png';
import axios from 'axios';
import { getAxiosConfig } from './lib/utils.ts';

function App() {
  const [devices, setDevices] = useState(new Array<DeviceInfo>());
  const [warning, setWarning] = useState("Nenhum aviso!");

  useEffect(() =>{
    const updateInterval = setInterval(() =>{
        requestDevicesList();
    }, 5000);

    return () => clearInterval(updateInterval);
  }, []);

  function requestDevicesList(){
    axios.request(getAxiosConfig(null, '/api/dispositivos', 'GET'))
    .then((response) =>{
        updateWarning(`Ultima atualização em ${new Date().toLocaleString()}`);
        let list = (response.data.devicesList) as Array<DeviceInfo>;

        // Formatar e organizar a lista antes de atualizar
        list.sort((a, b) => a.port - b.port);
        list.map((dispositivo) =>{
            if(dispositivo.type == 'sensor_trafego'){
                let indice_formatar = dispositivo.data.valueNameList.findIndex((str) =>{ return str.toLowerCase().includes('congestionamento') });
                let formatar = dispositivo.data.valueList[indice_formatar];
                dispositivo.data.valueList[indice_formatar] = Number(formatar).toFixed(1);
            }else if(dispositivo.type == 'poste'){
                let indice_formatar = dispositivo.data.valueNameList.findIndex((str) =>{ return str.toLowerCase().includes('modo') });
                let formatar = dispositivo.data.valueList[indice_formatar];
                dispositivo.data.valueList[indice_formatar] = formatar == '1'?'Ligado':'Desligado';
            }

            return dispositivo;
        })
        updateDevices(response.data.devicesList);
    })
    .catch((err) => setWarning(`O servidor respondeu a requisição em ${new Date().toLocaleString()} com: ${err}`));
  }

  // Update all devices
  function updateDevices(devices: Array<DeviceInfo>){
    setDevices(devices);
  }

  // Update single
  function updateDevice(deviceData: DeviceData){
    let newDevices = [...devices];
    let index = newDevices.findIndex((deviceTofind) =>{ return deviceTofind.deviceId == deviceData.deviceId});
    newDevices[index].data = deviceData;

    setDevices(newDevices);
  }

  function updateWarning(newWarning:  string){
    setWarning(newWarning);
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
            </div>
        </div>
        <ListDevices devices={devices} updateDevice={updateDevice} updateWarning={updateWarning}/>
    </div>
  )
}

export default App
