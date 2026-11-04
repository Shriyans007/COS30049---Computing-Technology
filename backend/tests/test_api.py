import json


def assert_safe_error(response, status, code):
    assert response.status_code == status
    assert response.json()["error"]["code"] == code
    rendered = response.text.lower()
    assert "traceback" not in rendered
    assert "/workspace/" not in rendered


def test_health_and_model_info(client):
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "model_ready": True}
    info = client.get("/api/v1/model-info")
    assert info.status_code == 200
    assert info.json()["class_mapping"] == {"0": "human", "1": "ai"}
    assert info.json()["limits"]["maximum_characters"] == 10_000


def test_prediction_contract_and_real_probabilities(client, valid_text):
    response = client.post("/api/v1/predict", json={"text": valid_text})
    assert response.status_code == 200
    body = response.json()
    assert body["prediction"] in {"human", "ai"}
    assert 0 <= body["ai_probability"] <= 1
    assert 0.5 <= body["confidence"] <= 1
    assert len(body["sentence_results"]) == 2
    assert all(0 <= row["ai_probability"] <= 1 for row in body["sentence_results"])


def test_empty_short_and_oversized_input(client):
    assert_safe_error(client.post("/api/v1/predict", json={"text": "   "}), 400, "EMPTY_TEXT")
    assert_safe_error(client.post("/api/v1/predict", json={"text": "Too short"}), 400, "TEXT_TOO_SHORT")
    assert_safe_error(
        client.post("/api/v1/predict", json={"text": "a" * 10_001}), 413, "TEXT_TOO_LARGE"
    )


def test_sentence_limit(client):
    text = " ".join(f"Sentence number {number}." for number in range(101))
    assert_safe_error(client.post("/api/v1/predict", json={"text": text}), 413, "TOO_MANY_SENTENCES")


def test_malformed_json_wrong_content_type_and_missing_route(client):
    malformed = client.post(
        "/api/v1/predict", content=b'{"text":', headers={"Content-Type": "application/json"}
    )
    assert_safe_error(malformed, 422, "INVALID_REQUEST")
    wrong_type = client.post(
        "/api/v1/predict", content="plain text", headers={"Content-Type": "text/plain"}
    )
    assert_safe_error(wrong_type, 415, "UNSUPPORTED_MEDIA_TYPE")
    assert_safe_error(client.get("/api/v1/missing"), 404, "NOT_FOUND")


def test_unicode_attack_is_normalised_without_echoing_as_html(client):
    attacked = "Furthеrmоre, this comprehensіve analysis contains <script>alert(1)</script>."
    response = client.post("/api/v1/predict", json={"text": attacked})
    assert response.status_code == 200
    body = response.json()
    assert body["normalisation_applied"] is True
    assert "<script>" in body["sentence_results"][0]["text"]


def test_control_character_rejected(client):
    assert_safe_error(
        client.post("/api/v1/predict", json={"text": "Normal words followed by a bad control.\u0000"}),
        400,
        "UNSAFE_CONTROL_CHARACTER",
    )


def test_cors_allows_configured_origin_and_not_unapproved_origin(client):
    allowed = client.options(
        "/api/v1/predict",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"
    denied = client.options(
        "/api/v1/predict",
        headers={"Origin": "https://attacker.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in denied.headers


def test_rate_limit_endpoint_returns_consistent_429(monkeypatch, valid_text):
    from fastapi.testclient import TestClient

    from backend.app.config import get_settings
    from backend.app.main import create_app

    monkeypatch.setenv("A3_RATE_LIMIT_REQUESTS", "1")
    get_settings.cache_clear()
    with TestClient(create_app()) as limited_client:
        assert limited_client.post("/api/v1/predict", json={"text": valid_text}).status_code == 200
        assert_safe_error(
            limited_client.post("/api/v1/predict", json={"text": valid_text}),
            429,
            "RATE_LIMITED",
        )
    get_settings.cache_clear()


def test_unexpected_model_error_is_safe_500(valid_text, monkeypatch):
    from fastapi.testclient import TestClient

    from backend.app.config import get_settings
    from backend.app.main import create_app

    def fail_safely(_):
        raise RuntimeError("private path /workspace/secret and internal details")

    monkeypatch.setenv("A3_RATE_LIMIT_REQUESTS", "1000")
    get_settings.cache_clear()
    with TestClient(create_app(), raise_server_exceptions=False) as error_client:
        monkeypatch.setattr(error_client.app.state.model_service, "predict", fail_safely)
        assert_safe_error(
            error_client.post("/api/v1/predict", json={"text": valid_text}),
            500,
            "INTERNAL_ERROR",
        )
    get_settings.cache_clear()
