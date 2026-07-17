from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_starter_endpoints()->None:
    for path in ("health","overview","partners","shipments","production-events","alerts"):
        assert client.get(f"/api/v1/{path}").status_code==200
