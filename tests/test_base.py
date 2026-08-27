"""Tests for the base infrastructure contract."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_reports_application_status() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert isinstance(response.json()["joblogic_configured"], bool)
