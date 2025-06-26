import { useState } from 'react'
import './App.css'
import HeaderDiv from './components/HeaderDiv/HeaderDiv.tsx'
import ListDevices from './components/listdevices/ListDevices.tsx'

function App() {
  //const [devices, setDevices] = useState(new Array<Device>());

  return (
    <div id='main-grid'>
      <HeaderDiv/>
      <ListDevices devices={[{device_id: 'test0'}, {device_id: 'test1'}]}/>
    </div>
  )
}

export default App
