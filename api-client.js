// Typed frontend API client for the Lattice optimizer backend. Plain JS (JSDoc-typed)
// rather than TypeScript, matching this prototype's existing no-build-step setup (see
// data.js, imported the same way from index.html's componentDidMount).
//
// @typedef {{name:string,type:string,label:string,required:boolean,source?:string,min?:number,max?:number,step?:number}} ScenarioParameterSchema
// @typedef {{id:string,label:string,description:string,supported:boolean,parameterSchema:ScenarioParameterSchema[],scenarioType:string,implementationStatus:string}} ScenarioDefinition
// @typedef {{scenarioId:string,parameters:Object}} ScenarioRunRequest
// @typedef {Object} ScenarioRunResult

const API_BASE = (window.__LATTICE_API_BASE__ || 'http://localhost:8000/api/v1');

async function request(path, options) {
  const res = await fetch(API_BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch (_e) { /* non-JSON error body */ }
    const err = new Error(detail);
    err.status = res.status;
    throw err;
  }
  return res.json();
}

/** @returns {Promise<ScenarioDefinition[]>} */
export function fetchScenarios() {
  return request('/scenarios');
}

/**
 * @param {string} scenarioId
 * @param {Object} parameters
 * @returns {Promise<ScenarioRunResult>}
 */
export function runScenario(scenarioId, parameters) {
  return request('/scenarios/run', {
    method: 'POST',
    body: JSON.stringify({ scenarioId, parameters: parameters || {} }),
  });
}

/**
 * Real hub list from Hub_Constraints -- backs Run Scenario's hub-selection parameter
 * controls, so options come from the workbook, not a hardcoded frontend list.
 * @param {boolean} coldChainOnly
 * @returns {Promise<Array<{hubId:string,stage:string,city:string,country:string,coldChainAvailable:boolean}>>}
 */
export function fetchHubs(coldChainOnly) {
  return request(`/hubs${coldChainOnly ? '?cold_chain_only=true' : ''}`);
}
