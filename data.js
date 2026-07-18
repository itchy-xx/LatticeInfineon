// Grounded reference data for the Infineon Supply Chain Command Center prototype.
// Derived from IFX_LOG_Master_Data (anonymised student dataset): real hub cities,
// coordinates, material families, lead times, costs and disruption scenarios.

export const STAGE_LABEL = { FE: 'Front-End Fab', Backend: 'Backend Assembly', OSAT: 'OSAT Test', SIFO: 'Ship-From/DC' };

// Equirectangular projection helper: lat/long -> 0..1000 x 0..520 map space
export function project(lat, lon) {
  const x = ((lon + 180) / 360) * 1000;
  const y = ((90 - lat) / 180) * 520;
  return { x, y };
}

export const HUBS = [
  { id: 'FE_LOC_001', stage: 'FE', city: 'Regensburg', country: 'Germany', cluster: 'Europe', lat: 49.0134, lon: 12.1016, capacity: 47000, util: 0.42, disruption: 'None' },
  { id: 'FE_LOC_016', stage: 'FE', city: 'Dresden', country: 'Germany', cluster: 'Europe', lat: 51.0504, lon: 13.7373, capacity: 89000, util: 0.63, disruption: 'None' },
  { id: 'FE_LOC_011', stage: 'FE', city: 'Hsinchu', country: 'Taiwan', cluster: 'East Asia', lat: 24.8138, lon: 120.9675, capacity: 75000, util: 0.56, disruption: 'None' },
  { id: 'FE_LOC_006', stage: 'FE', city: 'Austin', country: 'United States', cluster: 'North America', lat: 30.2672, lon: -97.7431, capacity: 61000, util: 0.49, disruption: 'None' },
  { id: 'FE_LOC_046', stage: 'FE', city: 'Austin', country: 'United States', cluster: 'North America', lat: 30.2672, lon: -97.7431, capacity: 93000, util: 0.63, disruption: 'Labor shortage', reduction: 0.25 },
  { id: 'BE_LOC_001', stage: 'Backend', city: 'Manila', country: 'Philippines', cluster: 'Southeast Asia', lat: 14.5995, lon: 120.9842, capacity: 15000, util: 0.42, disruption: 'Port congestion', reduction: 0.35 },
  { id: 'BE_LOC_030', stage: 'Backend', city: 'Bangkok', country: 'Thailand', cluster: 'Southeast Asia', lat: 13.7563, lon: 100.5018, capacity: 93000, util: 0.77, disruption: 'None' },
  { id: 'BE_LOC_058', stage: 'Backend', city: 'Wuxi', country: 'China', cluster: 'East Asia', lat: 31.4912, lon: 120.3119, capacity: 91000, util: 0.70, disruption: 'None' },
  { id: 'OSAT_LOC_065', stage: 'OSAT', city: 'Cebu', country: 'Philippines', cluster: 'Southeast Asia', lat: 10.3157, lon: 123.8854, capacity: 79000, util: 0.42, disruption: 'None' },
  { id: 'OSAT_LOC_011', stage: 'OSAT', city: 'Shanghai', country: 'China', cluster: 'East Asia', lat: 31.2304, lon: 121.4737, capacity: 21000, util: 0.63, disruption: 'Weather disruption', reduction: 0.20 },
  { id: 'SIFO_LOC_049', stage: 'SIFO', city: 'Amsterdam', country: 'Netherlands', cluster: 'Europe', lat: 52.3676, lon: 4.9041, capacity: 67000, util: 0.70, disruption: 'None' },
  { id: 'SIFO_LOC_001', stage: 'SIFO', city: 'Singapore', country: 'Singapore', cluster: 'Southeast Asia', lat: 1.3521, lon: 103.8198, capacity: 31000, util: 0.56, disruption: 'None' },
  { id: 'SIFO_LOC_011', stage: 'SIFO', city: 'Dubai', country: 'United Arab Emirates', cluster: 'Middle East', lat: 25.2048, lon: 55.2708, capacity: 73000, util: 0.77, disruption: 'None' },
];

export const EDGES = [
  { id: 'E1', from: 'FE_LOC_001', to: 'BE_LOC_001', family: 'GIP-14-SenseLink', mode: 'Air', leadDays: 2, costEur: 509 },
  { id: 'E2', from: 'FE_LOC_016', to: 'BE_LOC_001', family: 'OOS-50-SenseLink', mode: 'Air', leadDays: 3, costEur: 521 },
  { id: 'E3', from: 'FE_LOC_011', to: 'BE_LOC_030', family: 'PSS-39-SenseLink', mode: 'Air', leadDays: 2, costEur: 485 },
  { id: 'E4', from: 'FE_LOC_006', to: 'BE_LOC_058', family: 'PSS-32-SenseLink', mode: 'Ocean', leadDays: 12, costEur: 306 },
  { id: 'E5', from: 'FE_LOC_046', to: 'BE_LOC_058', family: 'CSS-80-SenseLink', mode: 'Air', leadDays: 4, costEur: 557 },
  { id: 'E6', from: 'BE_LOC_001', to: 'OSAT_LOC_065', family: 'PSS-32-SenseLink', mode: 'Air', leadDays: 3, costEur: 557, disrupted: true },
  { id: 'E7', from: 'BE_LOC_001', to: 'SIFO_LOC_049', family: 'GIP-14-SenseLink', mode: 'Air', leadDays: 2, costEur: 509, disrupted: true },
  { id: 'E8', from: 'BE_LOC_030', to: 'OSAT_LOC_011', family: 'PSS-39-SenseLink', mode: 'Air', leadDays: 2, costEur: 328 },
  { id: 'E9', from: 'BE_LOC_058', to: 'SIFO_LOC_001', family: 'CSS-80-SenseLink', mode: 'Air', leadDays: 4, costEur: 557 },
  { id: 'E10', from: 'OSAT_LOC_065', to: 'SIFO_LOC_011', family: 'PSS-32-SenseLink', mode: 'Air', leadDays: 2, costEur: 292 },
  { id: 'E11', from: 'SIFO_LOC_049', to: 'CUST_DE', family: 'GIP-14-SenseLink', mode: 'Road', leadDays: 1, costEur: 49 },
  { id: 'E12', from: 'SIFO_LOC_001', to: 'CUST_IN', family: 'PSS-55-SenseLink', mode: 'Air', leadDays: 2, costEur: 19 },
];

export const INCIDENT = {
  id: 'INC-2447',
  hubId: 'BE_LOC_001',
  title: 'Port congestion — Manila Backend hub',
  scenario: 'Port congestion',
  severity: 'Critical',
  detected: '2026-07-17 06:20 SGT',
  summary: 'Backend assembly capacity at Manila (BE_LOC_001) cut 35% by port congestion. Two lanes downstream to Cebu OSAT and Amsterdam SIFO are affected, holding shipments for three SenseLink material families feeding automotive and industrial customers in Germany, France and Italy.',
  capacityReductionPct: 0.35,
  affectedShipments: [
    { id: 'SIM-00065', family: 'GIP-14-SenseLink', lane: 'BE_LOC_001 → SIFO_LOC_049', status: 'Quality Hold', qty: 1100, delayDays: 0 },
    { id: 'SIM-00145', family: 'OOS-50-SenseLink', lane: 'BE_LOC_001 → SIFO_LOC_049', status: 'Delayed', qty: 100, delayDays: 3 },
    { id: 'SIM-00225', family: 'CSS-80-SenseLink', lane: 'BE_LOC_001 → SIFO_LOC_049', status: 'Quality Hold', qty: 153000, delayDays: 1 },
  ],
  exposureEur: 214600,
  exposureDays: 3,
  ordersAtRisk: 6,
  customersAtRisk: 3,
  trace: [
    { stage: 'Event', label: 'Port congestion declared', detail: 'Manila port authority — 35% capacity reduction, Backend hub BE_LOC_001', time: '06:20 SGT' },
    { stage: 'Site', label: 'BE_LOC_001 · Manila, Philippines', detail: 'Backend assembly — 15,000 units/wk capacity, 42% utilised, cold-chain capable', time: '06:24 SGT' },
    { stage: 'Product', label: 'GIP-14 / OOS-50 / CSS-80 SenseLink', detail: '3 material families, ESD-sensitive, Expedite & Standard priority class', time: '06:31 SGT' },
    { stage: 'Open orders', label: '6 open orders, 153,100 units in transit', detail: 'Lanes to SIFO_LOC_049 (Amsterdam) held at hub', time: '06:40 SGT' },
    { stage: 'Customers', label: '3 named accounts exposed', detail: 'Automotive Tier-1 (DE), Industrial Controls (FR), Sensor Systems (IT)', time: '06:45 SGT' },
  ],
  options: [
    {
      id: 'A', name: 'Expedite via Bangkok Backend',
      desc: 'Reroute held lots through BE_LOC_030 (Bangkok) with priority air uplift to Amsterdam.',
      costEur: 68400, costDeltaPct: 0.22, days: 2, daysSaved: 4, risk: 1.6, co2Kg: 610,
      constraints: { qualification: true, dieBankDepth: true, waferStarts: true, exportCompliance: true },
    },
    {
      id: 'B', name: 'Split lot — partial air, partial ocean',
      desc: 'Air-freight the 1,100-unit expedite-class lot only; hold remainder for next scheduled ocean lane.',
      costEur: 31200, costDeltaPct: 0.06, days: 5, daysSaved: 1, risk: 1.2, co2Kg: 340,
      constraints: { qualification: true, dieBankDepth: true, waferStarts: true, exportCompliance: true },
    },
    {
      id: 'C', name: 'Hold and absorb at hub',
      desc: 'Keep lots at Manila, resume standard lane once port clears; notify customers of revised ETA.',
      costEur: 4200, costDeltaPct: 0.01, days: 9, daysSaved: -3, risk: 3.4, co2Kg: 120,
      constraints: { qualification: true, dieBankDepth: false, waferStarts: true, exportCompliance: true },
    },
  ],
};

export const AUSTIN_INCIDENT = {
  id: 'INC-2461',
  hubId: 'FE_LOC_046',
  title: 'Labor shortage — Austin Front-End fab',
  scenario: 'Labor shortage',
  severity: 'Medium',
  detected: '2026-07-17 14:02 CST',
  summary: 'A skilled-technician shortage at the Austin front-end fab (FE_LOC_046) has cut wafer-start capacity by 25%. Two downstream lanes to Wuxi backend assembly are running behind schedule, affecting one automotive material family with orders booked through August.',
  capacityReductionPct: 0.25,
  affectedShipments: [
    { id: 'SIM-00312', family: 'CSS-80-SenseLink', lane: 'FE_LOC_046 → BE_LOC_058', status: 'Delayed', qty: 8600, delayDays: 2 },
    { id: 'SIM-00318', family: 'CSS-80-SenseLink', lane: 'FE_LOC_046 → BE_LOC_058', status: 'At Risk', qty: 4200, delayDays: 1 },
  ],
  exposureEur: 42800,
  exposureDays: 2,
  ordersAtRisk: 2,
  customersAtRisk: 1,
  trace: [
    { stage: 'Event', label: 'Labor shortage declared', detail: 'Austin fab — 25% wafer-start capacity reduction, FE_LOC_046', time: '14:02 CST' },
    { stage: 'Site', label: 'FE_LOC_046 · Austin, United States', detail: 'Front-end fab — 93,000 units/wk capacity, 63% utilised', time: '14:08 CST' },
    { stage: 'Product', label: 'CSS-80-SenseLink', detail: '1 material family, automotive priority class', time: '14:15 CST' },
    { stage: 'Open orders', label: '2 open orders, 12,800 units affected', detail: 'Lanes to BE_LOC_058 (Wuxi) running behind', time: '14:20 CST' },
    { stage: 'Customers', label: '1 named account exposed', detail: 'Automotive Tier-1 (DE)', time: '14:25 CST' },
  ],
  options: [
    { id: 'A', name: 'Shift wafer starts to Dresden FE', desc: 'Reallocate affected lots to FE_LOC_016 (Dresden) with spare capacity.', costEur: 26400, costDeltaPct: 0.09, days: 3, daysSaved: 3, risk: 1.4, co2Kg: 210, constraints: { qualification: true, dieBankDepth: true, waferStarts: true, exportCompliance: true } },
    { id: 'B', name: 'Contract temp technicians', desc: 'Bring in contract technicians to restore Austin capacity within the week.', costEur: 18900, costDeltaPct: 0.04, days: 5, daysSaved: 1, risk: 2.0, co2Kg: 40, constraints: { qualification: true, dieBankDepth: true, waferStarts: false, exportCompliance: true } },
    { id: 'C', name: 'Hold and absorb', desc: 'Run at reduced capacity, notify customers of a modest schedule slip.', costEur: 2100, costDeltaPct: 0.01, days: 8, daysSaved: -2, risk: 2.8, co2Kg: 15, constraints: { qualification: true, dieBankDepth: false, waferStarts: true, exportCompliance: true } },
  ],
};

export const SHANGHAI_INCIDENT = {
  id: 'INC-2455',
  hubId: 'OSAT_LOC_011',
  title: 'Weather disruption — Shanghai OSAT',
  scenario: 'Weather disruption',
  severity: 'Low',
  detected: '2026-07-17 09:47 CST',
  summary: 'A tropical storm advisory has reduced test-floor capacity at the Shanghai OSAT site (OSAT_LOC_011) by 20% for up to 48 hours. Impact is currently contained to one lane and one order.',
  capacityReductionPct: 0.20,
  affectedShipments: [
    { id: 'SIM-00401', family: 'PSS-39-SenseLink', lane: 'BE_LOC_030 → OSAT_LOC_011', status: 'At Risk', qty: 1900, delayDays: 1 },
  ],
  exposureEur: 9100,
  exposureDays: 1,
  ordersAtRisk: 1,
  customersAtRisk: 1,
  trace: [
    { stage: 'Event', label: 'Weather advisory issued', detail: 'Shanghai OSAT — 20% test-floor capacity reduction, 48h forecast', time: '09:47 CST' },
    { stage: 'Site', label: 'OSAT_LOC_011 · Shanghai, China', detail: 'OSAT test — 21,000 units/wk capacity, 63% utilised', time: '09:52 CST' },
    { stage: 'Product', label: 'PSS-39-SenseLink', detail: '1 material family, standard priority class', time: '09:58 CST' },
    { stage: 'Open orders', label: '1 open order, 1,900 units in test queue', detail: 'Lane from BE_LOC_030 (Bangkok) running slightly behind', time: '10:04 CST' },
    { stage: 'Customers', label: '1 named account exposed', detail: 'Automotive Tier-1 (DE)', time: '10:10 CST' },
  ],
  options: [
    { id: 'A', name: 'Reroute to Cebu OSAT', desc: 'Divert the affected lot to OSAT_LOC_065 (Cebu) for test.', costEur: 6300, costDeltaPct: 0.05, days: 1, daysSaved: 1, risk: 1.2, co2Kg: 55, constraints: { qualification: true, dieBankDepth: true, waferStarts: true, exportCompliance: true } },
    { id: 'B', name: 'Prioritise queue slot', desc: 'Hold position and prioritise this lot once the storm clears.', costEur: 900, costDeltaPct: 0.01, days: 2, daysSaved: 0, risk: 1.6, co2Kg: 5, constraints: { qualification: true, dieBankDepth: true, waferStarts: true, exportCompliance: true } },
    { id: 'C', name: 'Hold and absorb', desc: 'No action — resume standard schedule once advisory lifts.', costEur: 0, costDeltaPct: 0, days: 3, daysSaved: -1, risk: 2.1, co2Kg: 0, constraints: { qualification: true, dieBankDepth: false, waferStarts: true, exportCompliance: true } },
  ],
};

export const ALERTS = [
  { id: 'AL-1', severity: 'Critical', title: 'Port congestion — Manila Backend hub', hubId: 'BE_LOC_001', exposureEur: 214600, time: '06:20 SGT', muted: false, linkedIncident: 'INC-2447' },
  { id: 'AL-2', severity: 'Medium', title: 'Labor shortage — Austin FE (FE_LOC_046)', hubId: 'FE_LOC_046', exposureEur: 42800, time: 'Yesterday 14:02 CST', muted: false, linkedIncident: 'INC-2461' },
  { id: 'AL-3', severity: 'Low', title: 'Weather disruption — Shanghai OSAT (OSAT_LOC_011)', hubId: 'OSAT_LOC_011', exposureEur: 9100, time: 'Yesterday 09:47 CST', muted: false, linkedIncident: 'INC-2455' },
  { id: 'AL-4', severity: 'Low', title: 'Utilisation approaching cap — Dubai SIFO (77%)', hubId: 'SIFO_LOC_011', exposureEur: 3200, time: '2 days ago', muted: true },
  { id: 'AL-5', severity: 'Medium', title: 'Forwarder capacity tight — FWD-030 Amsterdam lane', hubId: 'SIFO_LOC_049', exposureEur: 18700, time: '2 days ago', muted: false },
];

export const AUDIT_LOG = [
  { id: 'AUD-1', time: '2026-07-15 11:02', actor: 'M. Bauer (Supply Planning)', action: 'Approved recommended option', incident: 'INC-2401', recommended: 'Option A — Expedite via alt forwarder', chosen: 'Option A — Expedite via alt forwarder', match: true },
  { id: 'AUD-2', time: '2026-07-12 09:41', actor: 'S. Tan (Logistics Control Tower)', action: 'Chose alternative to recommendation', incident: 'INC-2388', recommended: 'Option A — Full air uplift', chosen: 'Option B — Split lot', match: false },
  { id: 'AUD-3', time: '2026-07-09 16:15', actor: 'R. Okafor (Customer Ops)', action: 'Rejected all options, escalated', incident: 'INC-2371', recommended: 'Option A — Reroute via Kulim', chosen: 'Escalated to Regional Director', match: false },
];

export const COMMS_DRAFTS = [
  { id: 'CM-1', customer: 'Automotive Tier-1 (DE)', order: 'ORD-88214', tone: 'Proactive', status: 'Pending review',
    draft: 'We are writing to inform you of a 2–3 day delay affecting order ORD-88214 due to a capacity constraint at our Manila backend hub. We have activated an expedited air routing via Bangkok and expect delivery by 22 Jul 2026. We will keep you updated.',
    thread: [
      { from: 'system', text: 'Disruption INC-2447 detected — port congestion at Manila backend hub. Draft response generated for staff review.', time: '2026-07-17 08:15' },
    ] },
  { id: 'CM-2', customer: 'Industrial Controls (FR)', order: 'ORD-88301', tone: 'Proactive', status: 'Pending review',
    draft: 'Your order ORD-88301 remains on track. We identified minor congestion in our Southeast Asia network and have pre-emptively rerouted your shipment; no change to your confirmed ETA of 20 Jul 2026.',
    thread: [
      { from: 'system', text: 'Proactive notice drafted — order re-routed ahead of any customer-visible impact.', time: '2026-07-17 09:02' },
    ] },
  { id: 'CM-3', customer: 'Sensor Systems (IT)', order: 'ORD-88345', tone: 'Apologetic', status: 'Approved',
    draft: 'We regret to inform you that order ORD-88345 will arrive 3 days later than originally confirmed, now expected 24 Jul 2026, due to a port congestion event. A revised tracking link is attached.',
    thread: [
      { from: 'system', text: 'Disruption INC-2447 confirmed impacting this order. Draft apology + revised ETA generated.', time: '2026-07-16 16:05' },
      { from: 'staff', text: 'Reviewed and approved — sending revised ETA now.', time: '2026-07-16 16:20' },
    ] },
];

export const PARTNER_CLUSTERS = {
  'Sensortech Components (Partner, Kulim MY)': 'Southeast Asia',
  'Precision Substrates Ltd (Partner, Taoyuan TW)': 'East Asia',
  'Alpine Packaging Materials (Partner, Villach AT)': 'Europe',
};

export const PARTNER_HISTORY = {
  'Sensortech Components (Partner, Kulim MY)': [
    { id: 'SIM-00033', date: '2026-07-14', event: 'Lot WL-2288 shipped', lane: 'Kulim → BE_LOC_001 (Manila)', status: 'Delivered' },
    { id: 'SIM-00051', date: '2026-07-15', event: 'Wafer starts delayed 2 days', lane: 'Kulim FE stage', status: 'Delayed' },
    { id: 'SIM-00065', date: '2026-07-16', event: 'Lot WL-2291 flagged in ticket TCK-101', lane: 'Kulim → BE_LOC_001 (Manila)', status: 'Pending review' },
    { id: 'SIM-00072', date: '2026-07-17', event: 'Lot WL-2270 cleared QC', lane: 'BE_LOC_001 → SIFO_LOC_001 (Singapore)', status: 'Delivered' },
  ],
  'Precision Substrates Ltd (Partner, Taoyuan TW)': [
    { id: 'SUB-4460', date: '2026-07-11', event: 'Substrate shipment released', lane: 'Taoyuan → FE_LOC_011 (Hsinchu)', status: 'Delivered' },
    { id: 'SUB-4471', date: '2026-07-15', event: 'Export compliance hold raised', lane: 'Taoyuan → FE_LOC_011 (Hsinchu)', status: 'On hold' },
    { id: 'SUB-4480', date: '2026-07-17', event: 'Replacement lot dispatched', lane: 'Taoyuan → BE_LOC_058 (Wuxi)', status: 'In transit' },
  ],
  'Alpine Packaging Materials (Partner, Villach AT)': [
    { id: 'PKG-2201', date: '2026-07-08', event: 'Mold compound delivery', lane: 'Villach → FE_LOC_001 (Regensburg)', status: 'Delivered' },
    { id: 'PKG-2214', date: '2026-07-10', event: 'Allocation shortfall reported (ticket TCK-103)', lane: 'Villach → FE_LOC_001 (Regensburg)', status: 'Resolved' },
    { id: 'PKG-2230', date: '2026-07-16', event: 'Buffer top-up shipped', lane: 'Villach → FE_LOC_016 (Dresden)', status: 'In transit' },
  ],
};

export const TICKETS = [
  { id: 'TCK-101', partner: 'Sensortech Components (Partner, Kulim MY)', subject: 'Wafer lot delay — 2 days at FE stage', status: 'Pending', opened: '2026-07-16', priority: 'High',
    messages: [
      { from: 'partner', text: 'Our wafer starts at Kulim are running 2 days behind due to a tool qualification issue. Flagging before your next allocation run.', time: '2026-07-16 08:12' },
      { from: 'staff', text: 'Thanks for the early flag — can you confirm affected lot IDs and revised ready date?', time: '2026-07-16 10:03' },
      { from: 'partner', text: 'Lots WL-2291 through WL-2296, revised ready date 19 Jul.', time: '2026-07-16 11:47' },
    ] },
  { id: 'TCK-102', partner: 'Precision Substrates Ltd (Partner, Taoyuan TW)', subject: 'Export compliance hold on substrate shipment', status: 'Pending', opened: '2026-07-15', priority: 'Medium',
    messages: [
      { from: 'partner', text: 'Substrate shipment SUB-4471 is held at customs pending an updated export licence classification.', time: '2026-07-15 14:20' },
      { from: 'staff', text: 'Escalating to trade compliance now — will confirm timeline within 24h.', time: '2026-07-15 15:02' },
    ] },
  { id: 'TCK-103', partner: 'Alpine Packaging Materials (Partner, Villach AT)', subject: 'Mold compound allocation short by 8%', status: 'Resolved', opened: '2026-07-10', priority: 'Low',
    messages: [
      { from: 'partner', text: 'Confirming this month\'s mold compound allocation is 8% short of forecast.', time: '2026-07-10 09:00' },
      { from: 'staff', text: 'Approved a top-up from the Regensburg buffer stock, effective immediately.', time: '2026-07-11 09:30' },
      { from: 'partner', text: 'Confirmed received, closing out on our end. Thank you.', time: '2026-07-12 08:15' },
    ] },
];

export const WORLD_DOTS = [{"x":323.6,"y":53.5},{"x":339,"y":53.5},{"x":354.5,"y":53.5},{"x":369.9,"y":53.5},{"x":385.3,"y":53.5},{"x":400.7,"y":53.5},{"x":416.1,"y":53.5},{"x":431.5,"y":53.5},{"x":308.2,"y":66.9},{"x":323.6,"y":66.9},{"x":339,"y":66.9},{"x":354.5,"y":66.9},{"x":369.9,"y":66.9},{"x":385.3,"y":66.9},{"x":400.7,"y":66.9},{"x":416.1,"y":66.9},{"x":308.2,"y":80.2},{"x":323.6,"y":80.2},{"x":339,"y":80.2},{"x":354.5,"y":80.2},{"x":369.9,"y":80.2},{"x":385.3,"y":80.2},{"x":400.7,"y":80.2},{"x":416.1,"y":80.2},{"x":169.5,"y":93.6},{"x":339,"y":93.6},{"x":354.5,"y":93.6},{"x":369.9,"y":93.6},{"x":385.3,"y":93.6},{"x":400.7,"y":93.6},{"x":416.1,"y":93.6},{"x":693.5,"y":93.6},{"x":708.9,"y":93.6},{"x":724.3,"y":93.6},{"x":739.7,"y":93.6},{"x":184.9,"y":107},{"x":200.3,"y":107},{"x":231.2,"y":107},{"x":246.6,"y":107},{"x":262,"y":107},{"x":277.4,"y":107},{"x":339,"y":107},{"x":354.5,"y":107},{"x":369.9,"y":107},{"x":385.3,"y":107},{"x":400.7,"y":107},{"x":416.1,"y":107},{"x":647.3,"y":107},{"x":662.7,"y":107},{"x":678.1,"y":107},{"x":693.5,"y":107},{"x":708.9,"y":107},{"x":724.3,"y":107},{"x":739.7,"y":107},{"x":755.1,"y":107},{"x":770.5,"y":107},{"x":786,"y":107},{"x":832.2,"y":107},{"x":847.6,"y":107},{"x":61.6,"y":120.3},{"x":77.1,"y":120.3},{"x":92.5,"y":120.3},{"x":107.9,"y":120.3},{"x":123.3,"y":120.3},{"x":138.7,"y":120.3},{"x":154.1,"y":120.3},{"x":169.5,"y":120.3},{"x":184.9,"y":120.3},{"x":200.3,"y":120.3},{"x":246.6,"y":120.3},{"x":262,"y":120.3},{"x":292.8,"y":120.3},{"x":354.5,"y":120.3},{"x":369.9,"y":120.3},{"x":385.3,"y":120.3},{"x":400.7,"y":120.3},{"x":524,"y":120.3},{"x":539.4,"y":120.3},{"x":554.8,"y":120.3},{"x":585.6,"y":120.3},{"x":601,"y":120.3},{"x":616.4,"y":120.3},{"x":631.8,"y":120.3},{"x":647.3,"y":120.3},{"x":662.7,"y":120.3},{"x":678.1,"y":120.3},{"x":693.5,"y":120.3},{"x":708.9,"y":120.3},{"x":724.3,"y":120.3},{"x":739.7,"y":120.3},{"x":755.1,"y":120.3},{"x":770.5,"y":120.3},{"x":786,"y":120.3},{"x":801.4,"y":120.3},{"x":816.8,"y":120.3},{"x":832.2,"y":120.3},{"x":847.6,"y":120.3},{"x":863,"y":120.3},{"x":878.4,"y":120.3},{"x":893.8,"y":120.3},{"x":909.2,"y":120.3},{"x":924.7,"y":120.3},{"x":61.6,"y":133.7},{"x":77.1,"y":133.7},{"x":92.5,"y":133.7},{"x":107.9,"y":133.7},{"x":123.3,"y":133.7},{"x":138.7,"y":133.7},{"x":154.1,"y":133.7},{"x":169.5,"y":133.7},{"x":184.9,"y":133.7},{"x":200.3,"y":133.7},{"x":215.8,"y":133.7},{"x":231.2,"y":133.7},{"x":246.6,"y":133.7},{"x":277.4,"y":133.7},{"x":292.8,"y":133.7},{"x":354.5,"y":133.7},{"x":369.9,"y":133.7},{"x":508.6,"y":133.7},{"x":524,"y":133.7},{"x":539.4,"y":133.7},{"x":554.8,"y":133.7},{"x":585.6,"y":133.7},{"x":601,"y":133.7},{"x":616.4,"y":133.7},{"x":631.8,"y":133.7},{"x":647.3,"y":133.7},{"x":662.7,"y":133.7},{"x":678.1,"y":133.7},{"x":693.5,"y":133.7},{"x":708.9,"y":133.7},{"x":724.3,"y":133.7},{"x":739.7,"y":133.7},{"x":755.1,"y":133.7},{"x":770.5,"y":133.7},{"x":786,"y":133.7},{"x":801.4,"y":133.7},{"x":816.8,"y":133.7},{"x":832.2,"y":133.7},{"x":847.6,"y":133.7},{"x":863,"y":133.7},{"x":878.4,"y":133.7},{"x":893.8,"y":133.7},{"x":909.2,"y":133.7},{"x":924.7,"y":133.7},{"x":940.1,"y":133.7},{"x":61.6,"y":147.1},{"x":77.1,"y":147.1},{"x":92.5,"y":147.1},{"x":107.9,"y":147.1},{"x":123.3,"y":147.1},{"x":138.7,"y":147.1},{"x":154.1,"y":147.1},{"x":169.5,"y":147.1},{"x":184.9,"y":147.1},{"x":200.3,"y":147.1},{"x":215.8,"y":147.1},{"x":231.2,"y":147.1},{"x":277.4,"y":147.1},{"x":354.5,"y":147.1},{"x":493.2,"y":147.1},{"x":508.6,"y":147.1},{"x":539.4,"y":147.1},{"x":554.8,"y":147.1},{"x":570.2,"y":147.1},{"x":585.6,"y":147.1},{"x":601,"y":147.1},{"x":616.4,"y":147.1},{"x":631.8,"y":147.1},{"x":647.3,"y":147.1},{"x":662.7,"y":147.1},{"x":678.1,"y":147.1},{"x":693.5,"y":147.1},{"x":708.9,"y":147.1},{"x":724.3,"y":147.1},{"x":739.7,"y":147.1},{"x":755.1,"y":147.1},{"x":770.5,"y":147.1},{"x":786,"y":147.1},{"x":801.4,"y":147.1},{"x":816.8,"y":147.1},{"x":832.2,"y":147.1},{"x":847.6,"y":147.1},{"x":863,"y":147.1},{"x":878.4,"y":147.1},{"x":893.8,"y":147.1},{"x":909.2,"y":147.1},{"x":77.1,"y":160.5},{"x":138.7,"y":160.5},{"x":154.1,"y":160.5},{"x":169.5,"y":160.5},{"x":184.9,"y":160.5},{"x":200.3,"y":160.5},{"x":215.8,"y":160.5},{"x":231.2,"y":160.5},{"x":277.4,"y":160.5},{"x":292.8,"y":160.5},{"x":308.2,"y":160.5},{"x":493.2,"y":160.5},{"x":508.6,"y":160.5},{"x":539.4,"y":160.5},{"x":554.8,"y":160.5},{"x":570.2,"y":160.5},{"x":585.6,"y":160.5},{"x":601,"y":160.5},{"x":616.4,"y":160.5},{"x":631.8,"y":160.5},{"x":647.3,"y":160.5},{"x":662.7,"y":160.5},{"x":678.1,"y":160.5},{"x":693.5,"y":160.5},{"x":708.9,"y":160.5},{"x":724.3,"y":160.5},{"x":739.7,"y":160.5},{"x":755.1,"y":160.5},{"x":770.5,"y":160.5},{"x":786,"y":160.5},{"x":801.4,"y":160.5},{"x":816.8,"y":160.5},{"x":878.4,"y":160.5},{"x":154.1,"y":173.8},{"x":169.5,"y":173.8},{"x":184.9,"y":173.8},{"x":200.3,"y":173.8},{"x":215.8,"y":173.8},{"x":231.2,"y":173.8},{"x":246.6,"y":173.8},{"x":262,"y":173.8},{"x":277.4,"y":173.8},{"x":292.8,"y":173.8},{"x":308.2,"y":173.8},{"x":323.6,"y":173.8},{"x":524,"y":173.8},{"x":539.4,"y":173.8},{"x":554.8,"y":173.8},{"x":570.2,"y":173.8},{"x":585.6,"y":173.8},{"x":601,"y":173.8},{"x":616.4,"y":173.8},{"x":631.8,"y":173.8},{"x":647.3,"y":173.8},{"x":662.7,"y":173.8},{"x":678.1,"y":173.8},{"x":693.5,"y":173.8},{"x":708.9,"y":173.8},{"x":724.3,"y":173.8},{"x":739.7,"y":173.8},{"x":755.1,"y":173.8},{"x":770.5,"y":173.8},{"x":786,"y":173.8},{"x":801.4,"y":173.8},{"x":863,"y":173.8},{"x":878.4,"y":173.8},{"x":154.1,"y":187.2},{"x":169.5,"y":187.2},{"x":184.9,"y":187.2},{"x":200.3,"y":187.2},{"x":215.8,"y":187.2},{"x":231.2,"y":187.2},{"x":246.6,"y":187.2},{"x":262,"y":187.2},{"x":277.4,"y":187.2},{"x":292.8,"y":187.2},{"x":308.2,"y":187.2},{"x":477.7,"y":187.2},{"x":493.2,"y":187.2},{"x":508.6,"y":187.2},{"x":524,"y":187.2},{"x":539.4,"y":187.2},{"x":554.8,"y":187.2},{"x":570.2,"y":187.2},{"x":585.6,"y":187.2},{"x":601,"y":187.2},{"x":616.4,"y":187.2},{"x":631.8,"y":187.2},{"x":647.3,"y":187.2},{"x":662.7,"y":187.2},{"x":678.1,"y":187.2},{"x":693.5,"y":187.2},{"x":708.9,"y":187.2},{"x":724.3,"y":187.2},{"x":739.7,"y":187.2},{"x":755.1,"y":187.2},{"x":770.5,"y":187.2},{"x":786,"y":187.2},{"x":801.4,"y":187.2},{"x":816.8,"y":187.2},{"x":832.2,"y":187.2},{"x":169.5,"y":200.6},{"x":184.9,"y":200.6},{"x":200.3,"y":200.6},{"x":215.8,"y":200.6},{"x":231.2,"y":200.6},{"x":246.6,"y":200.6},{"x":262,"y":200.6},{"x":277.4,"y":200.6},{"x":292.8,"y":200.6},{"x":308.2,"y":200.6},{"x":477.7,"y":200.6},{"x":493.2,"y":200.6},{"x":508.6,"y":200.6},{"x":524,"y":200.6},{"x":539.4,"y":200.6},{"x":554.8,"y":200.6},{"x":570.2,"y":200.6},{"x":585.6,"y":200.6},{"x":601,"y":200.6},{"x":616.4,"y":200.6},{"x":631.8,"y":200.6},{"x":647.3,"y":200.6},{"x":662.7,"y":200.6},{"x":678.1,"y":200.6},{"x":693.5,"y":200.6},{"x":708.9,"y":200.6},{"x":724.3,"y":200.6},{"x":739.7,"y":200.6},{"x":755.1,"y":200.6},{"x":770.5,"y":200.6},{"x":786,"y":200.6},{"x":801.4,"y":200.6},{"x":816.8,"y":200.6},{"x":169.5,"y":213.9},{"x":184.9,"y":213.9},{"x":200.3,"y":213.9},{"x":215.8,"y":213.9},{"x":231.2,"y":213.9},{"x":246.6,"y":213.9},{"x":262,"y":213.9},{"x":277.4,"y":213.9},{"x":292.8,"y":213.9},{"x":462.3,"y":213.9},{"x":477.7,"y":213.9},{"x":493.2,"y":213.9},{"x":508.6,"y":213.9},{"x":524,"y":213.9},{"x":539.4,"y":213.9},{"x":554.8,"y":213.9},{"x":570.2,"y":213.9},{"x":585.6,"y":213.9},{"x":601,"y":213.9},{"x":616.4,"y":213.9},{"x":631.8,"y":213.9},{"x":647.3,"y":213.9},{"x":662.7,"y":213.9},{"x":678.1,"y":213.9},{"x":693.5,"y":213.9},{"x":708.9,"y":213.9},{"x":724.3,"y":213.9},{"x":739.7,"y":213.9},{"x":755.1,"y":213.9},{"x":770.5,"y":213.9},{"x":786,"y":213.9},{"x":169.5,"y":227.3},{"x":184.9,"y":227.3},{"x":200.3,"y":227.3},{"x":215.8,"y":227.3},{"x":231.2,"y":227.3},{"x":246.6,"y":227.3},{"x":262,"y":227.3},{"x":277.4,"y":227.3},{"x":462.3,"y":227.3},{"x":477.7,"y":227.3},{"x":493.2,"y":227.3},{"x":508.6,"y":227.3},{"x":524,"y":227.3},{"x":539.4,"y":227.3},{"x":554.8,"y":227.3},{"x":570.2,"y":227.3},{"x":585.6,"y":227.3},{"x":601,"y":227.3},{"x":616.4,"y":227.3},{"x":631.8,"y":227.3},{"x":647.3,"y":227.3},{"x":662.7,"y":227.3},{"x":678.1,"y":227.3},{"x":693.5,"y":227.3},{"x":708.9,"y":227.3},{"x":724.3,"y":227.3},{"x":739.7,"y":227.3},{"x":755.1,"y":227.3},{"x":770.5,"y":227.3},{"x":786,"y":227.3},{"x":184.9,"y":240.7},{"x":200.3,"y":240.7},{"x":215.8,"y":240.7},{"x":231.2,"y":240.7},{"x":246.6,"y":240.7},{"x":262,"y":240.7},{"x":462.3,"y":240.7},{"x":477.7,"y":240.7},{"x":493.2,"y":240.7},{"x":508.6,"y":240.7},{"x":524,"y":240.7},{"x":539.4,"y":240.7},{"x":554.8,"y":240.7},{"x":570.2,"y":240.7},{"x":585.6,"y":240.7},{"x":601,"y":240.7},{"x":616.4,"y":240.7},{"x":631.8,"y":240.7},{"x":647.3,"y":240.7},{"x":662.7,"y":240.7},{"x":678.1,"y":240.7},{"x":693.5,"y":240.7},{"x":708.9,"y":240.7},{"x":724.3,"y":240.7},{"x":739.7,"y":240.7},{"x":755.1,"y":240.7},{"x":770.5,"y":240.7},{"x":184.9,"y":254.1},{"x":200.3,"y":254.1},{"x":215.8,"y":254.1},{"x":446.9,"y":254.1},{"x":462.3,"y":254.1},{"x":477.7,"y":254.1},{"x":493.2,"y":254.1},{"x":508.6,"y":254.1},{"x":524,"y":254.1},{"x":539.4,"y":254.1},{"x":554.8,"y":254.1},{"x":570.2,"y":254.1},{"x":585.6,"y":254.1},{"x":616.4,"y":254.1},{"x":631.8,"y":254.1},{"x":647.3,"y":254.1},{"x":662.7,"y":254.1},{"x":678.1,"y":254.1},{"x":693.5,"y":254.1},{"x":708.9,"y":254.1},{"x":724.3,"y":254.1},{"x":739.7,"y":254.1},{"x":755.1,"y":254.1},{"x":770.5,"y":254.1},{"x":215.8,"y":267.4},{"x":431.5,"y":267.4},{"x":446.9,"y":267.4},{"x":462.3,"y":267.4},{"x":477.7,"y":267.4},{"x":493.2,"y":267.4},{"x":508.6,"y":267.4},{"x":524,"y":267.4},{"x":539.4,"y":267.4},{"x":554.8,"y":267.4},{"x":570.2,"y":267.4},{"x":585.6,"y":267.4},{"x":601,"y":267.4},{"x":616.4,"y":267.4},{"x":647.3,"y":267.4},{"x":662.7,"y":267.4},{"x":678.1,"y":267.4},{"x":693.5,"y":267.4},{"x":708.9,"y":267.4},{"x":724.3,"y":267.4},{"x":739.7,"y":267.4},{"x":755.1,"y":267.4},{"x":231.2,"y":280.8},{"x":246.6,"y":280.8},{"x":431.5,"y":280.8},{"x":446.9,"y":280.8},{"x":462.3,"y":280.8},{"x":477.7,"y":280.8},{"x":493.2,"y":280.8},{"x":508.6,"y":280.8},{"x":524,"y":280.8},{"x":539.4,"y":280.8},{"x":554.8,"y":280.8},{"x":570.2,"y":280.8},{"x":585.6,"y":280.8},{"x":601,"y":280.8},{"x":662.7,"y":280.8},{"x":678.1,"y":280.8},{"x":708.9,"y":280.8},{"x":724.3,"y":280.8},{"x":739.7,"y":280.8},{"x":262,"y":294.2},{"x":431.5,"y":294.2},{"x":446.9,"y":294.2},{"x":462.3,"y":294.2},{"x":477.7,"y":294.2},{"x":493.2,"y":294.2},{"x":508.6,"y":294.2},{"x":524,"y":294.2},{"x":539.4,"y":294.2},{"x":554.8,"y":294.2},{"x":570.2,"y":294.2},{"x":662.7,"y":294.2},{"x":724.3,"y":294.2},{"x":739.7,"y":294.2},{"x":277.4,"y":307.5},{"x":292.8,"y":307.5},{"x":308.2,"y":307.5},{"x":323.6,"y":307.5},{"x":446.9,"y":307.5},{"x":462.3,"y":307.5},{"x":477.7,"y":307.5},{"x":493.2,"y":307.5},{"x":508.6,"y":307.5},{"x":524,"y":307.5},{"x":539.4,"y":307.5},{"x":554.8,"y":307.5},{"x":570.2,"y":307.5},{"x":585.6,"y":307.5},{"x":724.3,"y":307.5},{"x":277.4,"y":320.9},{"x":292.8,"y":320.9},{"x":308.2,"y":320.9},{"x":323.6,"y":320.9},{"x":339,"y":320.9},{"x":508.6,"y":320.9},{"x":524,"y":320.9},{"x":539.4,"y":320.9},{"x":554.8,"y":320.9},{"x":570.2,"y":320.9},{"x":724.3,"y":320.9},{"x":277.4,"y":334.3},{"x":292.8,"y":334.3},{"x":308.2,"y":334.3},{"x":323.6,"y":334.3},{"x":339,"y":334.3},{"x":354.5,"y":334.3},{"x":369.9,"y":334.3},{"x":508.6,"y":334.3},{"x":524,"y":334.3},{"x":539.4,"y":334.3},{"x":554.8,"y":334.3},{"x":570.2,"y":334.3},{"x":277.4,"y":347.7},{"x":292.8,"y":347.7},{"x":308.2,"y":347.7},{"x":323.6,"y":347.7},{"x":339,"y":347.7},{"x":354.5,"y":347.7},{"x":369.9,"y":347.7},{"x":508.6,"y":347.7},{"x":524,"y":347.7},{"x":539.4,"y":347.7},{"x":554.8,"y":347.7},{"x":570.2,"y":347.7},{"x":292.8,"y":361},{"x":308.2,"y":361},{"x":323.6,"y":361},{"x":339,"y":361},{"x":354.5,"y":361},{"x":369.9,"y":361},{"x":508.6,"y":361},{"x":524,"y":361},{"x":539.4,"y":361},{"x":554.8,"y":361},{"x":570.2,"y":361},{"x":786,"y":361},{"x":801.4,"y":361},{"x":832.2,"y":361},{"x":308.2,"y":374.4},{"x":323.6,"y":374.4},{"x":339,"y":374.4},{"x":354.5,"y":374.4},{"x":369.9,"y":374.4},{"x":508.6,"y":374.4},{"x":524,"y":374.4},{"x":539.4,"y":374.4},{"x":554.8,"y":374.4},{"x":585.6,"y":374.4},{"x":770.5,"y":374.4},{"x":786,"y":374.4},{"x":801.4,"y":374.4},{"x":816.8,"y":374.4},{"x":832.2,"y":374.4},{"x":292.8,"y":387.8},{"x":308.2,"y":387.8},{"x":323.6,"y":387.8},{"x":339,"y":387.8},{"x":508.6,"y":387.8},{"x":524,"y":387.8},{"x":539.4,"y":387.8},{"x":554.8,"y":387.8},{"x":585.6,"y":387.8},{"x":755.1,"y":387.8},{"x":770.5,"y":387.8},{"x":786,"y":387.8},{"x":801.4,"y":387.8},{"x":816.8,"y":387.8},{"x":832.2,"y":387.8},{"x":847.6,"y":387.8},{"x":292.8,"y":401.1},{"x":308.2,"y":401.1},{"x":323.6,"y":401.1},{"x":339,"y":401.1},{"x":524,"y":401.1},{"x":539.4,"y":401.1},{"x":770.5,"y":401.1},{"x":786,"y":401.1},{"x":801.4,"y":401.1},{"x":816.8,"y":401.1},{"x":832.2,"y":401.1},{"x":847.6,"y":401.1},{"x":292.8,"y":414.5},{"x":308.2,"y":414.5},{"x":323.6,"y":414.5},{"x":816.8,"y":414.5},{"x":832.2,"y":414.5},{"x":847.6,"y":414.5},{"x":292.8,"y":427.9},{"x":308.2,"y":427.9},{"x":292.8,"y":441.3},{"x":292.8,"y":454.6}];
export const CONTINENT_OUTLINES = [
  { name: 'AfroEurasia', d: 'M 727.7,78.7 C 732.6,80.5 742.9,89.9 751.7,93.6 C 760.6,97.3 771.4,98.3 780.8,101.0 C 790.2,103.8 797.7,109.2 808.2,109.9 C 818.8,110.7 831.9,104.2 844.2,105.5 C 856.4,106.7 869.3,115.4 881.8,117.4 C 894.4,119.4 908.1,114.9 919.5,117.4 C 930.9,119.8 950.1,128.5 950.3,132.2 C 950.6,135.9 929.5,135.4 921.2,139.7 C 913.0,143.9 907.5,151.5 900.7,157.5 C 893.8,163.4 886.7,172.6 880.1,175.3 C 873.6,178.0 861.6,177.5 861.3,173.8 C 861.0,170.1 880.7,155.5 878.4,153.0 C 876.1,150.6 858.2,155.8 847.6,159.0 C 837.0,162.2 817.4,166.9 815.1,172.3 C 812.8,177.8 833.0,187.0 833.9,191.7 C 834.8,196.4 826.5,195.6 820.2,200.6 C 813.9,205.5 802.2,216.7 796.2,221.4 C 790.2,226.1 787.7,225.3 784.2,228.8 C 780.8,232.3 780.0,235.5 775.7,242.2 C 771.4,248.9 763.7,261.5 758.6,268.9 C 753.4,276.3 750.3,282.0 744.9,286.7 C 739.4,291.4 728.0,291.4 726.0,297.1 C 724.0,302.8 732.6,314.2 732.9,320.9 C 733.2,327.6 731.4,339.0 727.7,337.3 C 724.0,335.5 712.3,316.0 710.6,310.5 C 708.9,305.1 718.6,310.5 717.5,304.6 C 716.3,298.6 710.3,278.1 703.8,274.9 C 697.2,271.6 684.9,281.8 678.1,285.3 C 671.2,288.7 668.1,298.4 662.7,295.7 C 657.2,292.9 654.4,275.1 645.5,268.9 C 636.7,262.7 616.4,259.5 609.6,258.5 C 602.7,257.5 603.0,259.8 604.5,263.0 C 605.9,266.2 621.6,272.9 618.2,277.8 C 614.7,282.8 587.3,287.7 583.9,292.7 C 580.5,297.6 599.3,301.1 597.6,307.5 C 595.9,314.0 577.9,321.7 573.6,331.3 C 569.3,341.0 575.1,355.3 571.9,365.5 C 568.8,375.6 561.9,384.6 554.8,392.2 C 547.7,399.9 536.8,411.8 529.1,411.5 C 521.4,411.3 512.3,399.9 508.6,390.7 C 504.9,381.6 508.8,367.7 506.8,356.6 C 504.9,345.4 502.6,331.1 496.6,323.9 C 490.6,316.7 480.6,317.0 470.9,313.5 C 461.2,310.0 445.2,310.5 438.4,303.1 C 431.5,295.7 428.1,279.3 429.8,268.9 C 431.5,258.5 445.5,249.4 448.6,240.7 C 451.8,232.0 446.1,224.1 448.6,216.9 C 451.2,209.7 457.8,204.0 464.0,197.6 C 470.3,191.2 480.0,182.2 486.3,178.3 C 492.6,174.3 494.6,176.6 501.7,173.8 C 508.8,171.1 523.7,168.6 529.1,161.9 C 534.5,155.3 536.0,134.2 534.2,133.7 C 532.5,133.2 524.8,154.8 518.8,159.0 C 512.8,163.2 502.6,161.7 498.3,159.0 C 494.0,156.2 490.6,149.3 493.2,142.6 C 495.7,135.9 504.6,124.3 513.7,118.9 C 522.8,113.4 537.4,108.2 547.9,109.9 C 558.5,111.7 572.8,125.0 577.1,129.3 C 581.3,133.5 571.1,135.4 573.6,135.2 C 576.2,135.0 584.5,130.7 592.5,127.8 C 600.5,124.8 613.3,119.6 621.6,117.4 C 629.9,115.1 636.1,114.2 642.1,114.4 C 648.1,114.6 654.7,119.8 657.5,118.9 C 660.4,117.9 654.1,111.9 659.2,108.5 C 664.4,105.0 677.8,102.3 688.4,98.1 C 698.9,93.8 716.0,86.4 722.6,83.2 C 729.2,80.0 722.9,77.0 727.7,78.7 Z' },
  { name: 'Americas', d: 'M 159.2,93.6 C 164.7,94.3 182.9,99.8 191.8,102.5 C 200.6,105.2 207.8,106.5 212.3,109.9 C 216.9,113.4 216.0,123.6 219.2,123.3 C 222.3,123.1 225.7,108.2 231.2,108.5 C 236.6,108.7 249.1,125.5 251.7,124.8 C 254.3,124.1 243.2,107.5 246.6,104.0 C 250.0,100.5 262.8,102.3 272.3,104.0 C 281.7,105.7 296.5,109.2 303.1,114.4 C 309.6,119.6 311.9,129.5 311.6,135.2 C 311.4,140.9 306.8,148.8 301.4,148.6 C 295.9,148.3 282.2,138.4 279.1,133.7 C 276.0,129.0 284.2,121.8 282.5,120.3 C 280.8,118.9 271.4,121.1 268.8,124.8 C 266.3,128.5 270.8,139.9 267.1,142.6 C 263.4,145.4 250.6,137.7 246.6,141.1 C 242.6,144.6 239.2,156.5 243.2,163.4 C 247.1,170.4 265.4,183.2 270.5,182.7 C 275.7,182.2 269.7,165.7 274.0,160.5 C 278.3,155.3 289.1,151.3 296.2,151.5 C 303.4,151.8 311.1,156.5 316.8,161.9 C 322.5,167.4 328.8,178.3 330.5,184.2 C 332.2,190.2 330.8,196.9 327.1,197.6 C 323.3,198.3 309.4,187.7 308.2,188.7 C 307.1,189.7 322.5,199.6 320.2,203.5 C 317.9,207.5 301.9,207.0 294.5,212.5 C 287.1,217.9 280.5,228.6 275.7,236.2 C 270.8,243.9 272.0,256.3 265.4,258.5 C 258.8,260.7 241.2,246.4 236.3,249.6 C 231.4,252.8 233.7,272.6 236.3,277.8 C 238.9,283.0 245.7,277.1 251.7,280.8 C 257.7,284.5 264.3,297.6 272.3,300.1 C 280.3,302.6 289.4,294.2 299.7,295.7 C 309.9,297.1 324.5,303.8 333.9,309.0 C 343.3,314.2 347.6,321.4 356.2,326.9 C 364.7,332.3 382.4,334.3 385.3,341.7 C 388.1,349.1 379.0,362.5 373.3,371.4 C 367.6,380.3 358.7,388.0 351.0,395.2 C 343.3,402.4 333.9,408.6 327.1,414.5 C 320.2,420.5 313.9,423.9 309.9,430.9 C 305.9,437.8 305.1,448.4 303.1,456.1 C 301.1,463.8 301.7,477.2 297.9,476.9 C 294.2,476.7 282.8,463.8 280.8,454.6 C 278.8,445.5 284.0,433.6 286.0,421.9 C 288.0,410.3 293.9,395.7 292.8,384.8 C 291.7,373.9 283.4,366.2 279.1,356.6 C 274.8,346.9 269.4,335.3 267.1,326.9 C 264.8,318.4 270.3,312.7 265.4,306.1 C 260.6,299.4 248.0,292.4 238.0,286.7 C 228.0,281.0 212.9,276.8 205.5,271.9 C 198.1,266.9 197.2,260.2 193.5,257.0 C 189.8,253.8 188.4,257.5 183.2,252.6 C 178.1,247.6 167.2,237.2 162.7,227.3 C 158.1,217.4 159.8,202.1 155.8,193.1 C 151.8,184.2 146.4,180.0 138.7,173.8 C 131.0,167.6 118.4,158.2 109.6,156.0 C 100.7,153.8 92.5,158.5 85.6,160.5 C 78.8,162.4 73.9,169.6 68.5,167.9 C 63.1,166.2 56.2,155.8 53.1,150.1 C 49.9,144.4 49.7,138.7 49.7,133.7 C 49.7,128.8 46.8,124.3 53.1,120.3 C 59.4,116.4 75.1,110.2 87.3,109.9 C 99.6,109.7 114.4,118.1 126.7,118.9 C 139.0,119.6 152.7,115.6 161.0,114.4 C 169.2,113.2 176.7,114.2 176.4,111.4 C 176.1,108.7 162.1,101.0 159.2,98.1 C 156.4,95.1 153.8,92.9 159.2,93.6 Z' },
  { name: 'Greenland', d: 'M 380.1,43.1 C 381.8,43.1 387.0,43.1 390.4,43.1 C 393.8,43.1 397.8,42.6 400.7,43.1 C 403.5,43.6 405.0,45.3 407.5,46.1 C 410.1,46.8 414.1,46.3 416.1,47.5 C 418.1,48.8 417.8,52.0 419.5,53.5 C 421.2,55.0 424.1,56.5 426.4,56.5 C 428.7,56.5 430.9,54.0 433.2,53.5 C 435.5,53.0 438.6,52.7 440.1,53.5 C 441.5,54.2 442.6,56.7 441.8,57.9 C 440.9,59.2 437.2,59.9 434.9,60.9 C 432.6,61.9 430.1,62.6 428.1,63.9 C 426.1,65.1 424.1,66.9 422.9,68.3 C 421.8,69.8 420.9,71.1 421.2,72.8 C 421.5,74.5 424.4,77.0 424.7,78.7 C 424.9,80.5 423.2,82.0 422.9,83.2 C 422.7,84.4 422.7,84.9 422.9,86.2 C 423.2,87.4 424.7,89.1 424.7,90.6 C 424.7,92.1 423.5,93.6 422.9,95.1 C 422.4,96.6 422.7,98.8 421.2,99.5 C 419.8,100.3 415.5,98.6 414.4,99.5 C 413.2,100.5 413.5,103.8 414.4,105.5 C 415.2,107.2 419.2,108.2 419.5,109.9 C 419.8,111.7 417.5,114.2 416.1,115.9 C 414.7,117.6 413.0,119.1 411.0,120.3 C 409.0,121.6 407.0,122.8 404.1,123.3 C 401.3,123.8 396.1,122.3 393.8,123.3 C 391.6,124.3 392.1,127.8 390.4,129.3 C 388.7,130.7 386.1,131.5 383.6,132.2 C 381.0,133.0 377.0,132.5 375.0,133.7 C 373.0,135.0 372.7,137.7 371.6,139.7 C 370.4,141.6 369.0,143.4 368.2,145.6 C 367.3,147.8 367.6,151.5 366.4,153.0 C 365.3,154.5 363.6,154.5 361.3,154.5 C 359.0,154.5 355.0,154.0 352.7,153.0 C 350.5,152.0 349.0,150.3 347.6,148.6 C 346.2,146.8 345.3,144.6 344.2,142.6 C 343.0,140.6 341.9,138.7 340.8,136.7 C 339.6,134.7 337.9,132.7 337.3,130.7 C 336.8,128.8 336.5,126.5 337.3,124.8 C 338.2,123.1 341.6,121.6 342.5,120.3 C 343.3,119.1 343.6,117.9 342.5,117.4 C 341.3,116.9 336.2,118.4 335.6,117.4 C 335.0,116.4 339.0,112.9 339.0,111.4 C 339.0,109.9 336.5,110.2 335.6,108.5 C 334.8,106.7 334.8,103.3 333.9,101.0 C 333.0,98.8 331.9,96.8 330.5,95.1 C 329.1,93.4 327.3,91.9 325.3,90.6 C 323.3,89.4 321.1,88.4 318.5,87.7 C 315.9,86.9 312.8,86.2 309.9,86.2 C 307.1,86.2 303.7,88.2 301.4,87.7 C 299.1,87.2 297.4,84.7 296.2,83.2 C 295.1,81.7 295.4,80.5 294.5,78.7 C 293.7,77.0 290.5,74.3 291.1,72.8 C 291.7,71.3 295.4,70.6 297.9,69.8 C 300.5,69.1 305.4,69.3 306.5,68.3 C 307.6,67.4 304.2,65.4 304.8,63.9 C 305.4,62.4 307.6,60.4 309.9,59.4 C 312.2,58.4 316.2,58.9 318.5,57.9 C 320.8,57.0 321.6,54.7 323.6,53.5 C 325.6,52.2 328.2,50.5 330.5,50.5 C 332.8,50.5 335.3,53.2 337.3,53.5 C 339.3,53.7 340.8,52.5 342.5,52.0 C 344.2,51.5 345.3,50.5 347.6,50.5 C 349.9,50.5 354.2,51.8 356.2,52.0 C 358.2,52.2 359.3,52.7 359.6,52.0 C 359.9,51.3 356.7,48.5 357.9,47.5 C 359.0,46.6 363.6,46.6 366.4,46.1 C 369.3,45.6 372.7,45.1 375.0,44.6 C 377.3,44.1 379.3,43.3 380.1,43.1 C 381.0,42.8 378.4,43.1 380.1,43.1 Z' },
  { name: 'Australia', d: 'M 827.1,352.1 C 827.9,352.4 829.6,353.8 830.5,355.1 C 831.3,356.3 831.3,358.3 832.2,359.5 C 833.0,360.8 834.8,361.3 835.6,362.5 C 836.5,363.8 836.8,365.5 837.3,367.0 C 837.9,368.5 838.2,370.2 839.0,371.4 C 839.9,372.7 841.3,373.4 842.5,374.4 C 843.6,375.4 845.0,376.1 845.9,377.4 C 846.7,378.6 846.7,380.6 847.6,381.8 C 848.5,383.1 849.9,383.8 851.0,384.8 C 852.2,385.8 853.6,386.5 854.5,387.8 C 855.3,389.0 855.6,390.7 856.2,392.2 C 856.7,393.7 857.9,395.2 857.9,396.7 C 857.9,398.2 856.4,399.4 856.2,401.1 C 855.9,402.9 856.7,405.6 856.2,407.1 C 855.6,408.6 853.6,408.8 852.7,410.1 C 851.9,411.3 851.9,413.3 851.0,414.5 C 850.2,415.8 848.2,416.0 847.6,417.5 C 847.0,419.0 848.5,422.2 847.6,423.4 C 846.7,424.7 844.2,424.4 842.5,424.9 C 840.8,425.4 839.0,426.4 837.3,426.4 C 835.6,426.4 833.9,424.9 832.2,424.9 C 830.5,424.9 828.8,426.4 827.1,426.4 C 825.3,426.4 823.1,425.9 821.9,424.9 C 820.8,423.9 821.1,421.7 820.2,420.5 C 819.3,419.2 817.6,418.7 816.8,417.5 C 815.9,416.2 815.9,413.3 815.1,413.0 C 814.2,412.8 812.8,416.0 811.6,416.0 C 810.5,416.0 809.1,414.3 808.2,413.0 C 807.4,411.8 807.6,409.6 806.5,408.6 C 805.4,407.6 803.4,407.3 801.4,407.1 C 799.4,406.8 796.5,406.8 794.5,407.1 C 792.5,407.3 791.1,408.1 789.4,408.6 C 787.7,409.1 785.7,409.3 784.2,410.1 C 782.8,410.8 782.2,412.3 780.8,413.0 C 779.4,413.8 777.4,414.5 775.7,414.5 C 774.0,414.5 772.0,412.8 770.5,413.0 C 769.1,413.3 768.8,415.5 767.1,416.0 C 765.4,416.5 761.7,416.7 760.3,416.0 C 758.8,415.3 758.8,413.3 758.6,411.5 C 758.3,409.8 758.8,407.3 758.6,405.6 C 758.3,403.9 757.4,402.6 756.8,401.1 C 756.3,399.7 755.7,398.2 755.1,396.7 C 754.6,395.2 753.7,394.0 753.4,392.2 C 753.1,390.5 753.1,388.0 753.4,386.3 C 753.7,384.6 754.3,383.1 755.1,381.8 C 756.0,380.6 757.4,379.8 758.6,378.9 C 759.7,377.9 760.6,376.6 762.0,375.9 C 763.4,375.1 765.4,374.9 767.1,374.4 C 768.8,373.9 770.8,373.7 772.3,372.9 C 773.7,372.2 774.8,371.2 775.7,369.9 C 776.5,368.7 776.5,366.2 777.4,365.5 C 778.3,364.7 779.7,366.0 780.8,365.5 C 782.0,365.0 783.1,363.5 784.2,362.5 C 785.4,361.5 786.2,359.8 787.7,359.5 C 789.1,359.3 791.4,361.3 792.8,361.0 C 794.2,360.8 795.1,359.0 796.2,358.1 C 797.4,357.1 798.2,355.8 799.7,355.1 C 801.1,354.3 802.8,353.8 804.8,353.6 C 806.8,353.4 809.9,353.1 811.6,353.6 C 813.4,354.1 815.1,355.6 815.1,356.6 C 815.1,357.6 811.9,358.3 811.6,359.5 C 811.4,360.8 812.2,363.0 813.4,364.0 C 814.5,365.0 817.1,364.7 818.5,365.5 C 819.9,366.2 820.8,368.5 821.9,368.5 C 823.1,368.5 824.8,367.0 825.3,365.5 C 825.9,364.0 825.3,361.5 825.3,359.5 C 825.3,357.6 825.1,354.8 825.3,353.6 C 825.6,352.4 826.2,351.9 827.1,352.1 Z' },
  { name: 'Madagascar', d: 'M 594.2,353.6 C 594.5,353.6 595.6,353.4 595.9,353.6 C 596.2,353.8 595.6,354.8 595.9,355.1 C 596.2,355.3 597.3,354.8 597.6,355.1 C 597.9,355.3 597.6,356.1 597.6,356.6 C 597.6,357.1 597.3,357.8 597.6,358.1 C 597.9,358.3 599.0,357.8 599.3,358.1 C 599.6,358.3 599.3,359.0 599.3,359.5 C 599.3,360.0 599.3,360.5 599.3,361.0 C 599.3,361.5 599.6,362.3 599.3,362.5 C 599.0,362.8 597.9,362.3 597.6,362.5 C 597.3,362.8 597.6,363.5 597.6,364.0 C 597.6,364.5 597.6,365.0 597.6,365.5 C 597.6,366.0 597.9,366.7 597.6,367.0 C 597.3,367.2 596.2,366.7 595.9,367.0 C 595.6,367.2 595.9,368.0 595.9,368.5 C 595.9,369.0 595.9,369.4 595.9,369.9 C 595.9,370.4 595.9,370.9 595.9,371.4 C 595.9,371.9 595.9,372.4 595.9,372.9 C 595.9,373.4 596.2,374.2 595.9,374.4 C 595.6,374.6 594.5,374.2 594.2,374.4 C 593.9,374.6 594.2,375.4 594.2,375.9 C 594.2,376.4 594.2,376.9 594.2,377.4 C 594.2,377.9 594.5,378.6 594.2,378.9 C 593.9,379.1 592.8,378.6 592.5,378.9 C 592.2,379.1 592.5,379.8 592.5,380.3 C 592.5,380.8 592.5,381.3 592.5,381.8 C 592.5,382.3 592.8,383.1 592.5,383.3 C 592.2,383.6 591.0,383.1 590.8,383.3 C 590.5,383.6 590.8,384.3 590.8,384.8 C 590.8,385.3 591.0,386.0 590.8,386.3 C 590.5,386.5 589.3,386.0 589.0,386.3 C 588.8,386.5 589.0,387.3 589.0,387.8 C 589.0,388.3 589.3,389.0 589.0,389.3 C 588.8,389.5 587.6,389.0 587.3,389.3 C 587.0,389.5 587.6,390.5 587.3,390.7 C 587.0,391.0 586.2,390.7 585.6,390.7 C 585.0,390.7 584.2,391.0 583.9,390.7 C 583.6,390.5 584.2,389.5 583.9,389.3 C 583.6,389.0 582.5,389.5 582.2,389.3 C 581.9,389.0 582.2,388.3 582.2,387.8 C 582.2,387.3 582.5,386.5 582.2,386.3 C 581.9,386.0 580.8,386.5 580.5,386.3 C 580.2,386.0 580.5,385.3 580.5,384.8 C 580.5,384.3 580.8,383.6 580.5,383.3 C 580.2,383.1 579.1,383.6 578.8,383.3 C 578.5,383.1 578.8,382.3 578.8,381.8 C 578.8,381.3 578.8,380.8 578.8,380.3 C 578.8,379.8 578.8,379.4 578.8,378.9 C 578.8,378.4 578.5,377.6 578.8,377.4 C 579.1,377.1 580.2,377.6 580.5,377.4 C 580.8,377.1 580.5,376.4 580.5,375.9 C 580.5,375.4 580.2,374.6 580.5,374.4 C 580.8,374.2 581.9,374.6 582.2,374.4 C 582.5,374.2 582.2,373.4 582.2,372.9 C 582.2,372.4 582.5,371.7 582.2,371.4 C 581.9,371.2 580.8,371.7 580.5,371.4 C 580.2,371.2 580.5,370.4 580.5,369.9 C 580.5,369.4 580.5,369.0 580.5,368.5 C 580.5,368.0 580.5,367.5 580.5,367.0 C 580.5,366.5 580.5,366.0 580.5,365.5 C 580.5,365.0 580.2,364.2 580.5,364.0 C 580.8,363.8 581.9,364.2 582.2,364.0 C 582.5,363.8 581.9,362.8 582.2,362.5 C 582.5,362.3 583.3,362.5 583.9,362.5 C 584.5,362.5 585.0,362.5 585.6,362.5 C 586.2,362.5 587.0,362.8 587.3,362.5 C 587.6,362.3 587.0,361.3 587.3,361.0 C 587.6,360.8 588.5,361.0 589.0,361.0 C 589.6,361.0 590.5,361.3 590.8,361.0 C 591.0,360.8 590.8,360.0 590.8,359.5 C 590.8,359.0 590.5,358.3 590.8,358.1 C 591.0,357.8 592.2,358.3 592.5,358.1 C 592.8,357.8 592.2,356.8 592.5,356.6 C 592.8,356.3 593.9,356.8 594.2,356.6 C 594.5,356.3 594.2,355.6 594.2,355.1 C 594.2,354.6 594.2,353.8 594.2,353.6 C 594.2,353.4 593.9,353.6 594.2,353.6 Z' },
  { name: 'Philippines', d: 'M 834.7,206.6 C 835.8,205.3 838.8,204.8 839.7,206.0 C 840.6,207.2 840.6,211.5 840.3,213.8 C 839.9,216.0 836.9,218.4 837.5,219.6 C 838.1,220.8 842.3,219.3 843.9,221.0 C 845.5,222.7 847.6,227.5 847.2,229.7 C 846.9,231.8 842.8,232.3 841.7,234.0 C 840.5,235.7 841.6,238.2 840.3,239.8 C 839.0,241.3 835.4,243.5 833.9,243.2 C 832.4,243.0 831.7,240.4 831.1,238.3 C 830.5,236.3 829.9,233.8 830.3,231.1 C 830.6,228.5 832.8,225.3 833.3,222.4 C 833.8,219.6 833.1,216.4 833.3,213.8 C 833.6,211.1 833.7,207.9 834.7,206.6 Z' },
  { name: 'Taiwan', d: 'M 837.5,186.9 C 838.3,186.9 838.8,188.1 838.9,189.2 C 838.9,190.3 838.4,192.3 837.8,193.6 C 837.2,194.8 836.0,196.7 835.3,196.7 C 834.6,196.7 833.8,194.8 833.6,193.6 C 833.4,192.3 833.2,190.3 833.9,189.2 C 834.5,188.1 836.7,186.9 837.5,186.9 Z' },
];

export const ORDERS = [
  { id: 'ORD-88214', customer: 'Automotive Tier-1 (DE)', material: 'GIP-14-SenseLink', qty: 1100, status: 'At risk',
    originalEta: '2026-07-20', updatedEta: '2026-07-22', cause: 'A port congestion event at our Manila backend assembly hub (BE_LOC_001) has cut processing capacity by 35%. Your shipment was queued for assembly there and is now running 2–3 days behind schedule.',
    recovery: 'Expedited air routing via Bangkok Backend hub activated — new lane in transit.', carrier: 'FWD-030', tracking: 'FWD030-AMS-88214' },
  { id: 'ORD-88301', customer: 'Automotive Tier-1 (DE)', material: 'PSS-39-SenseLink', qty: 4200, status: 'On track',
    originalEta: '2026-07-24', updatedEta: '2026-07-24', cause: '—', recovery: '—', carrier: 'FWD-018', tracking: 'FWD018-FRA-88301' },
  { id: 'ORD-88345', customer: 'Automotive Tier-1 (DE)', material: 'CSS-80-SenseLink', qty: 153000, status: 'Disrupted',
    originalEta: '2026-07-21', updatedEta: '2026-07-24', cause: 'A labor shortage at our Austin front-end fab (FE_LOC_046) has cut wafer-start capacity by 25%. This is a large lot (153,000 units), so it is taking longer to reallocate and is now expected 3 days later than planned.',
    recovery: 'Wafer starts for this lot are being shifted to our Dresden fab, which has spare capacity — new lane in transit.', carrier: 'FWD-015', tracking: 'FWD015-AMS-88345' },
  { id: 'ORD-88402', customer: 'Automotive Tier-1 (DE)', material: 'PSS-55-SenseLink', qty: 620, status: 'On track',
    originalEta: '2026-07-29', updatedEta: '2026-07-29', cause: '—', recovery: '—', carrier: 'FWD-009', tracking: 'FWD009-BLR-88402' },
  { id: 'ORD-88190', customer: 'Automotive Tier-1 (DE)', material: 'GIP-14-SenseLink', qty: 2100, status: 'Completed',
    originalEta: '2026-07-05', updatedEta: '2026-07-05', cause: '—', recovery: '—', carrier: 'FWD-030', tracking: 'FWD030-AMS-88190' },
];
