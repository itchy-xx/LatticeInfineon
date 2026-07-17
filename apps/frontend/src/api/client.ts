import type{Overview,SupplyChainRecord}from'./types';
const base=import.meta.env.VITE_API_BASE_URL??'http://localhost:8000/api/v1';
async function get<T>(path:string):Promise<T>{const response=await fetch(`${base}${path}`);if(!response.ok)throw new Error(`API request failed: ${response.status}`);return response.json() as Promise<T>}
export const api={overview:()=>get<Overview>('/overview'),partners:()=>get<SupplyChainRecord[]>('/partners'),shipments:()=>get<SupplyChainRecord[]>('/shipments'),productionEvents:()=>get<SupplyChainRecord[]>('/production-events'),alerts:()=>get<SupplyChainRecord[]>('/alerts')};
