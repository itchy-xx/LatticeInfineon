import type{SupplyChainRecord}from'../../api/types';import{Panel}from'../../components/Panel';
export function AlertsPanel({items}:{items:SupplyChainRecord[]}){return <Panel title="Alerts & exceptions">{items.map(x=><article className="alert" key={x.id}><strong>{String(x.attributes.title??x.id)}</strong><p>{String(x.attributes.summary??'Details pending')}</p></article>)}</Panel>}
