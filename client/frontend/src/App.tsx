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
        list.sort((a, b) => a.port - b.port);
        updateDevices(response.data.devicesList);
    })
    .catch((err) => setWarning(`O servidor respondeu a requisição em ${new Date().toLocaleString()} com: ${err.message}`));
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
            <div id='controls'>
                <button onClick={requestDevicesList}>Atualizar dispositivos</button>
            </div>
            <p>{warning}</p>
        </div>
        <ListDevices devices={devices} updateDevice={updateDevice} updateWarning={updateWarning}/>
    </div>
  )
}

export default App
