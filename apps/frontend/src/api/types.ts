// Mirrors packages/contracts. Generate this file from OpenAPI once contracts stabilize.
export interface SourceMetadata{source_system:string;observed_at:string;freshness_score?:number;confidence_score?:number}
export interface SupplyChainRecord{id:string;record_type:string;status?:string;partner_id?:string;occurred_at?:string;attributes:Record<string,unknown>;source:SourceMetadata}
export interface Overview{partners:number;shipments:number;production_events:number;open_alerts:number;data_status:string}
