export interface DeviceInfo{
    device_id: string,
    status: string,
    type: string,
    value_name: Array<string>,
    value: Array<string>
}

export interface Command{
    device_id: string,
    action: string,
    parameter: string
}