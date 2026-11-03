from unittest.mock import MagicMock

from sqlalchemy.exc import OperationalError

from app.routers import ops


def test_healthz_returns_ok(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_returns_ready_when_database_is_reachable(client, monkeypatch):
    monkeypatch.setattr(ops, "engine", MagicMock())

    response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readyz_returns_503_when_database_is_unreachable(client, monkeypatch):
    engine = MagicMock()
    engine.connect.side_effect = OperationalError("SELECT 1", {}, Exception("db down"))
    monkeypatch.setattr(ops, "engine", engine)

    response = client.get("/readyz")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
