from fastapi.testclient import TestClient

from app import __version__


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}


def test_index_renders_template(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "edge-app-practice" in response.text
    assert __version__ in response.text


def test_ping(client: TestClient) -> None:
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.json() == {"pong": True}
