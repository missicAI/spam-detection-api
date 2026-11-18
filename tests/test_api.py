import joblib
import pytest
from fastapi.testclient import TestClient

from spamguard.service import create_app
from spamguard.training import make_pipeline


@pytest.fixture
def client(tmp_path):
    pipeline = make_pipeline()
    pipeline.fit(
        ["hello friend lunch", "hello friend meet", "free prize win", "free prize cash"],
        ["ham", "ham", "spam", "spam"],
    )
    path = tmp_path / "model.joblib"
    joblib.dump({"pipeline": pipeline, "metadata": {"created_at_utc": "test-only"}}, path)
    with TestClient(create_app(path)) as test_client:
        yield test_client


def test_health_and_prediction_response(client):
    assert client.get("/health").status_code == 200
    response = client.post("/predict", json={"text": "free prize"})
    assert response.status_code == 200
    assert response.json()["label"] == "spam"
    assert 0 <= response.json()["spam_probability"] <= 1


@pytest.mark.parametrize(
    "payload",
    [
        {"text": ""},
        {"text": "   "},
        {"text": "x" * 5001},
        {"text": 42},
        {},
        {"text": "hello", "unknown": True},
    ],
)
def test_invalid_requests_return_422(client, payload):
    assert client.post("/predict", json=payload).status_code == 422


def test_missing_model_returns_503(tmp_path):
    with TestClient(create_app(tmp_path / "missing.joblib")) as client:
        assert client.get("/health").status_code == 503
        assert client.post("/predict", json={"text": "hello"}).status_code == 503
