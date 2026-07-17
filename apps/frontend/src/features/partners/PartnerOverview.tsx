import type{SupplyChainRecord}from'../../api/types';import{Panel}from'../../components/Panel';
export function PartnerOverview({items}:{items:SupplyChainRecord[]}){return <Panel title="Partner overview"><ul>{items.map(x=><li key={x.id}>{String(x.attributes.display_name??x.id)} <span>{x.status}</span></li>)}</ul></Panel>}
