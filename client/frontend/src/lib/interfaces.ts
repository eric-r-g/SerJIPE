export interface DeviceInfo{
    device_id: string,
    type: string,
    ip: string,
    port: number,
    status: string,
    lastReading: DeviceData
}

export interface DeviceData{
    device_id: string,
    status: string,
    value_name: Array<string>,
    value: Array<string>,
    timestamp: string
}

export interface Command{
    device_id: string,
    action: string,
    parameter: string
}