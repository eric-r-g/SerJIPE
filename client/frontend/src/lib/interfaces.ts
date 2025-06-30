export interface DeviceInfo{
    deviceId: string,
    type: string,
    ip: string,
    port: number,
    data: DeviceData
}

export interface DeviceData{
    deviceId: string,
    status: string,
    valueNameList: Array<string>,
    valueList: Array<string>,
    timestamp: string
}

export interface Command{
    deviceId: string,
    action: string,
    parameter: string
}