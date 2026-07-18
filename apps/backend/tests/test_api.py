from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_starter_endpoints()->None:
    for path in ("health","overview","partners","shipments","production-events","alerts"):
        assert client.get(f"/api/v1/{path}").status_code==200

def test_scenario_registry()->None:
    resp = client.get("/api/v1/scenarios")
    assert resp.status_code == 200
    ids = {s["id"] for s in resp.json()}
    assert {"primary_hub_down", "air_capacity_reduced", "port_congestion",
            "cold_chain_restriction", "expedited_priority", "normal_operations"} <= ids

def test_run_primary_hub_down_scenario()->None:
    payload = {"scenarioId": "primary_hub_down", "parameters": {}}
    resp = client.post("/api/v1/scenarios/run", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["scenario"]["id"] == "primary_hub_down"
    assert body["status"] == "completed"

def test_run_unsupported_scenario_returns_400()->None:
    payload = {"scenarioId": "not_a_real_scenario", "parameters": {}}
    resp = client.post("/api/v1/scenarios/run", json=payload)
    assert resp.status_code == 400

def test_run_scenario_with_list_valued_parameters()->None:
    payload = {"scenarioId": "cold_chain_restriction", "parameters": {"affectedHubIds": ["SIFO_LOC_001"]}}
    resp = client.post("/api/v1/scenarios/run", json=payload)
    assert resp.status_code == 200
    resp2 = client.post("/api/v1/scenarios/run", json=payload)
    assert resp2.status_code == 200

def test_hubs_endpoint_returns_real_workbook_hubs()->None:
    resp = client.get("/api/v1/hubs")
    assert resp.status_code == 200
    all_hubs = resp.json()
    assert len(all_hubs) > 100
    resp_cc = client.get("/api/v1/hubs?cold_chain_only=true")
    assert resp_cc.status_code == 200
    cc_hubs = resp_cc.json()
    assert len(cc_hubs) < len(all_hubs)
    assert all(h["coldChainAvailable"] for h in cc_hubs)
