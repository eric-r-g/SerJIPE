export interface DeviceInfo{
    device_id: string,
    status: string,
    value_name: Array<string>,
    value: Array<string>
}

export interface Command{
    deviceId: string,
    action: string,
    parameter: string
}