import type { AxiosRequestConfig } from "axios";

export function getAxiosConfig(data: any, url: string, method: string): AxiosRequestConfig  {
    return {
        data: data,
        url: url,
        method: method,
        maxBodyLength: 1000,
    } as AxiosRequestConfig;
}