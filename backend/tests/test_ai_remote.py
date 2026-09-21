"""Test lanjutan AI service: path remote (httpx dimock) & parsing JSON."""
import json

import pytest

from app import ai


def test_configured_remote_dengan_key_true(monkeypatch):
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "remote")
    monkeypatch.setenv("MAUEKSPOR_AI_API_KEY", "sk-test")
    assert ai.configured()


def test_configured_mock_false(monkeypatch):
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "mock")
    assert not ai.configured()


def test_configured_remote_tanpa_key_masih_true(monkeypatch):
    """Remote mode without key: configured still True (anonymous AI calls are allowed).
    The old test assumed key is required; anonymous endpoints don't need one."""
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "remote")
    monkeypatch.delenv("MAUEKSPOR_AI_API_KEY", raising=False)
    # Without a key, remote calls will still be attempted (no key = anonymous)
    assert ai.configured()


def _make_healthy_probe(monkeypatch):
    """Helper: make health probe succeed so _call_remote proceeds past the probe."""
    import httpx as _httpx

    class FakeGetResp:
        status_code = 200
        def json(self): return {"data": []}

    monkeypatch.setattr(_httpx, "get", lambda *a, **k: FakeGetResp())
    # Reset circuit breaker state
    ai._CB_FAILURE_COUNT = 0
    ai._CB_LAST_FAILURE_TIME = 0.0
    # Reset health cache so probe runs fresh
    ai._HEALTH_CACHE.clear()
    ai._LAST_HEALTH_TS = 0.0


def test_remote_success(monkeypatch):
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "remote")
    monkeypatch.setenv("MAUEKSPOR_AI_API_KEY", "sk-test")
    _make_healthy_probe(monkeypatch)

    class FakePostResp:
        text = ""
        status_code = 200
        def json(self):
            return {"choices": [{"message": {"content": '{"hsCode": "0901.21", "confidence": 90}'}}]}

    import httpx as _httpx
    monkeypatch.setattr(_httpx, "post", lambda *a, **k: FakePostResp())
    text = ai.complete("system", "user", kind="classify")
    assert text is not None
    assert "0901.21" in text


def test_remote_http_error_returns_mock(monkeypatch):
    """When remote call fails, should fall back to mock (not None)."""
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "remote")
    monkeypatch.setenv("MAUEKSPOR_AI_API_KEY", "sk-test")
    _make_healthy_probe(monkeypatch)
    ai._CB_FAILURE_COUNT = 0  # reset circuit breaker

    import httpx as _httpx

    def boom(*a, **k):
        raise RuntimeError("network")

    monkeypatch.setattr(_httpx, "post", boom)
    # Should fall back to mock, not return None
    result = ai.complete("s", "u", kind="classify")
    # Mock returns the canned classify dict
    assert result is not None


def test_remote_parse_error_returns_mock(monkeypatch):
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "remote")
    monkeypatch.setenv("MAUEKSPOR_AI_API_KEY", "sk-test")
    _make_healthy_probe(monkeypatch)
    ai._CB_FAILURE_COUNT = 0

    class FakeResp:
        text = ""
        status_code = 200
        def json(self): raise ValueError("bad json")

    import httpx as _httpx
    monkeypatch.setattr(_httpx, "post", lambda *a, **k: FakeResp())
    result = ai.complete("s", "u", kind="classify")
    assert result is not None  # mock fallback


def test_remote_empty_choices_returns_mock(monkeypatch):
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "remote")
    monkeypatch.setenv("MAUEKSPOR_AI_API_KEY", "sk-test")
    _make_healthy_probe(monkeypatch)
    ai._CB_FAILURE_COUNT = 0

    class FakeResp:
        text = ""
        status_code = 200
        def json(self): return {"choices": []}

    import httpx as _httpx
    monkeypatch.setattr(_httpx, "post", lambda *a, **k: FakeResp())
    result = ai.complete("s", "u", kind="classify")
    assert result is not None  # mock fallback


def test_ask_json_parses_json_didalam_teks():
    result = ai.ask_json("s", "u", kind="classify")
    assert isinstance(result, dict)
    assert result["hsCode"] == "0901.21"


def test_ask_json_teks_tanpa_braces_none():
    assert ai.ask_json("s", "u", kind="chat_reply") is None


def test_ask_json_braces_tapi_bukan_json_none(monkeypatch):
    def fake_complete(system, user, kind=""):
        return "ini {bukan json}"

    monkeypatch.setattr(ai, "complete", fake_complete)
    assert ai.ask_json("s", "u", kind="x") is None


def test_ask_json_parsed_bukan_dict_none(monkeypatch):
    def fake_complete(system, user, kind=""):
        return "[1, 2, 3]"

    monkeypatch.setattr(ai, "complete", fake_complete)
    assert ai.ask_json("s", "u", kind="x") is None


def test_mock_kind_tidak_dikenal_none(monkeypatch):
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "mock")
    assert ai.complete("s", "u", kind="tidak-ada") is None


def test_circuit_breaker_opens_after_threshold(monkeypatch):
    """Circuit breaker should open after CB_FAILURE_THRESHOLD failures."""
    import httpx as _httpx

    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "remote")
    monkeypatch.setenv("MAUEKSPOR_AI_API_KEY", "sk-test")

    # Reset state
    ai._CB_FAILURE_COUNT = 0
    ai._CB_LAST_FAILURE_TIME = 0.0
    ai._HEALTH_CACHE.clear()
    ai._LAST_HEALTH_TS = 0.0

    # Make health probe fail → triggers circuit breaker increments
    class FailResp:
        status_code = 503

    monkeypatch.setattr(_httpx, "get", lambda *a, **k: FailResp())

    # Each call triggers a health probe failure
    for _ in range(ai.CB_FAILURE_THRESHOLD):
        # Force health re-check each time
        ai._LAST_HEALTH_TS = 0.0
        ai.complete("s", "u", kind="classify")

    assert ai._cb_is_open(), "Circuit breaker should be open after threshold failures"


def test_circuit_breaker_resets_after_cooldown(monkeypatch):
    """Circuit breaker should auto-reset after cooldown period."""
    import time

    # Simulate open state well past cooldown
    ai._CB_FAILURE_COUNT = ai.CB_FAILURE_THRESHOLD
    ai._CB_LAST_FAILURE_TIME = time.monotonic() - ai.CB_COOLDOWN_SECONDS - 1

    assert not ai._cb_is_open(), "Circuit breaker should be closed after cooldown"
    assert ai._CB_FAILURE_COUNT == 0, "Failure count should be reset"
