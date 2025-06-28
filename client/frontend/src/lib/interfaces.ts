export interface DeviceInfo{
    device_id: string,
    type: string,
    ip: string,
    port: number,
    status: string,
    lastReading: SensorData
}

export interface SensorData{
    device_id: string,
    value: number,
    timestamp: string
}

export interface Command{
    device_id: string,
    action: string,
    parameter: string
}