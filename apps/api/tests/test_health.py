import os

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.integration
def test_health_integration():
    if not os.getenv("POSTGRES_HOST"):
        pytest.skip("POSTGRES_HOST not set")
    client = TestClient(app)
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
