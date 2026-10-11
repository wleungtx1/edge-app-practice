from fastapi.testclient import TestClient

ALPHA = {"name": "alpha", "url": "https://alpha.example.test", "enabled": True}
BETA = {"name": "beta", "url": "https://beta.example.test", "enabled": False}


def test_list_is_empty_initially(client: TestClient) -> None:
    assert client.get("/api/providers").json() == []


def test_create_and_get(client: TestClient) -> None:
    created = client.post("/api/providers", json=ALPHA)

    assert created.status_code == 201
    body = created.json()
    assert body == {"id": body["id"], **ALPHA}
    assert client.get(f"/api/providers/{body['id']}").json() == body


def test_list_returns_providers_in_id_order(client: TestClient) -> None:
    client.post("/api/providers", json=ALPHA)
    client.post("/api/providers", json=BETA)

    names = [p["name"] for p in client.get("/api/providers").json()]

    assert names == ["alpha", "beta"]


def test_create_duplicate_name_conflicts(client: TestClient) -> None:
    client.post("/api/providers", json=ALPHA)

    assert client.post("/api/providers", json=ALPHA).status_code == 409


def test_create_rejects_empty_name(client: TestClient) -> None:
    assert client.post("/api/providers", json={**ALPHA, "name": ""}).status_code == 422


def test_update(client: TestClient) -> None:
    provider_id = client.post("/api/providers", json=ALPHA).json()["id"]

    updated = client.put(f"/api/providers/{provider_id}", json={**ALPHA, "enabled": False})

    assert updated.status_code == 200
    assert updated.json()["enabled"] is False


def test_update_to_existing_name_conflicts(client: TestClient) -> None:
    client.post("/api/providers", json=ALPHA)
    beta_id = client.post("/api/providers", json=BETA).json()["id"]

    response = client.put(f"/api/providers/{beta_id}", json={**BETA, "name": "alpha"})

    assert response.status_code == 409


def test_delete(client: TestClient) -> None:
    provider_id = client.post("/api/providers", json=ALPHA).json()["id"]

    assert client.delete(f"/api/providers/{provider_id}").status_code == 204
    assert client.get(f"/api/providers/{provider_id}").status_code == 404


def test_missing_provider_is_404(client: TestClient) -> None:
    assert client.get("/api/providers/999").status_code == 404
    assert client.put("/api/providers/999", json=ALPHA).status_code == 404
    assert client.delete("/api/providers/999").status_code == 404
