"""
tests/test_app.py — SepsisGuard Flask Application Tests
=========================================================
Validates the API endpoints, input validation, and response shapes.
These tests use Flask''s built-in test client and do NOT require the
server to be running.

Run with:
    pytest tests/ -v
"""

import json
import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, FEATURES, FEATURE_RANGES, PRESETS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def client():
    """Return a Flask test client with testing mode enabled."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _valid_payload(**overrides):
    """Return a valid prediction payload (uses the ''healthy'' preset values)."""
    payload = dict(PRESETS["healthy"])
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        res = client.get("/health")
        assert res.status_code == 200

    def test_health_response_schema(self, client):
        data = res = client.get("/health").get_json()
        assert "status" in data
        assert data["status"] == "ok"
        assert "model_loaded" in data


# ---------------------------------------------------------------------------
# Index route
# ---------------------------------------------------------------------------
class TestIndexRoute:
    def test_index_returns_200(self, client):
        res = client.get("/")
        assert res.status_code == 200

    def test_index_returns_html(self, client):
        res = client.get("/")
        assert b"SepsisGuard" in res.data


# ---------------------------------------------------------------------------
# Predict endpoint — happy path
# ---------------------------------------------------------------------------
class TestPredictHappyPath:
    def test_healthy_preset_returns_200(self, client):
        res = client.post(
            "/predict",
            data=json.dumps(_valid_payload()),
            content_type="application/json",
        )
        assert res.status_code == 200

    def test_response_contains_prediction_and_probability(self, client):
        res = client.post(
            "/predict",
            data=json.dumps(_valid_payload()),
            content_type="application/json",
        )
        data = res.get_json()
        assert "prediction" in data
        assert "probability" in data

    def test_prediction_is_binary(self, client):
        data = client.post(
            "/predict",
            data=json.dumps(_valid_payload()),
            content_type="application/json",
        ).get_json()
        assert data["prediction"] in (0, 1)

    def test_probability_is_percentage(self, client):
        data = client.post(
            "/predict",
            data=json.dumps(_valid_payload()),
            content_type="application/json",
        ).get_json()
        assert 0.0 <= data["probability"] <= 100.0

    @pytest.mark.parametrize("preset_name", ["healthy", "warning", "critical"])
    def test_all_presets_return_200(self, client, preset_name):
        payload = dict(PRESETS[preset_name])
        res = client.post(
            "/predict",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert res.status_code == 200


# ---------------------------------------------------------------------------
# Predict endpoint — error cases
# ---------------------------------------------------------------------------
class TestPredictValidation:
    def test_missing_field_returns_400(self, client):
        payload = _valid_payload()
        del payload["HR"]
        res = client.post(
            "/predict",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert res.status_code == 400

    def test_non_numeric_field_returns_400(self, client):
        res = client.post(
            "/predict",
            data=json.dumps(_valid_payload(HR="not-a-number")),
            content_type="application/json",
        )
        assert res.status_code == 400

    def test_out_of_range_heart_rate_returns_400(self, client):
        # HR upper bound is 300
        res = client.post(
            "/predict",
            data=json.dumps(_valid_payload(HR=500)),
            content_type="application/json",
        )
        assert res.status_code == 400

    def test_empty_body_returns_400(self, client):
        res = client.post("/predict", data="", content_type="application/json")
        assert res.status_code == 400

    def test_non_json_content_type_returns_400(self, client):
        res = client.post(
            "/predict",
            data="HR=72",
            content_type="application/x-www-form-urlencoded",
        )
        assert res.status_code == 400

    @pytest.mark.parametrize("feature,bad_value", [
        ("O2Sat", 110),       # > 100
        ("Temp", 20.0),       # < 30
        ("Age", -5),          # negative
        ("Gender", 2),        # must be 0 or 1
    ])
    def test_specific_range_violations(self, client, feature, bad_value):
        res = client.post(
            "/predict",
            data=json.dumps(_valid_payload(**{feature: bad_value})),
            content_type="application/json",
        )
        assert res.status_code == 400


# ---------------------------------------------------------------------------
# Feature configuration
# ---------------------------------------------------------------------------
class TestConfiguration:
    def test_all_features_have_range_definitions(self):
        for f in FEATURES:
            assert f in FEATURE_RANGES, f"No range defined for feature '{f}'"

    def test_all_presets_have_all_features(self):
        for name, preset in PRESETS.items():
            for f in FEATURES:
                assert f in preset, f"Preset '{name}' missing feature '{f}'"

    def test_preset_values_within_ranges(self):
        for name, preset in PRESETS.items():
            for f, value in preset.items():
                if f in FEATURE_RANGES:
                    lo, hi = FEATURE_RANGES[f]
                    assert lo <= value <= hi, (
                        f"Preset ''{name}'' value {value} for ''{f}'' outside range ({lo}–{hi})"
                    )
