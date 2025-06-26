from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_audit_endpoint():
    response = client.post(
        "/audit",
        json={
            "code": "import os\ndef insecure():\n    os.system('echo $USER')",
            "language": "python"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "scan_results" in data
    assert "vulnerabilities" in data
    assert len(data["vulnerabilities"]) > 0

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}

def test_invalid_request():
    response = client.post("/audit", json={"code": "", "language": ""})
    assert response.status_code == 400