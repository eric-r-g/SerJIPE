import { useState } from 'react'
import './App.css'
import HeaderDiv from './components/HeaderDiv/HeaderDiv.tsx'
import ListDevices from './components/listdevices/ListDevices.tsx'

function App() {
  //const [devices, setDevices] = useState(new Array<Device>());

  return (
    <div id='main-grid'>
      <HeaderDiv/>
      <ListDevices devices={[{
          device_id: 'test0',
          type: '',
          ip: '',
          port: 0,
          status: '',
          lastReading: {
              device_id: '',
              value: 0,
              timestamp: ''
          }
      }, {
          device_id: 'test1',
          type: '',
          ip: '',
          port: 0,
          status: '',
          lastReading: {
              device_id: '',
              value: 0,
              timestamp: ''
          }
      }]}/>
    </div>
  )
}

export default App
