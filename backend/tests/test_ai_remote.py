"""Test lanjutan AI service: path remote (httpx dimock) & parsing JSON."""
import json

import pytest

from app import ai


def test_configured_remote_tanpa_key_false(monkeypatch):
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "remote")
    monkeypatch.delenv("MAUEKSPOR_AI_API_KEY", raising=False)
    assert not ai.configured()


def test_configured_remote_dengan_key_true(monkeypatch):
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "remote")
    monkeypatch.setenv("MAUEKSPOR_AI_API_KEY", "sk-test")
    assert ai.configured()


def test_remote_success(monkeypatch):
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "remote")
    monkeypatch.setenv("MAUEKSPOR_AI_API_KEY", "sk-test")

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": '{"hsCode": "0901.21", "confidence": 90}'}}]}

    monkeypatch.setattr(ai.httpx, "post", lambda *a, **k: FakeResp())
    text = ai.complete("system", "user", kind="classify")
    assert text is not None
    assert "0901.21" in text


def test_remote_http_error_returns_none(monkeypatch):
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "remote")
    monkeypatch.setenv("MAUEKSPOR_AI_API_KEY", "sk-test")

    def boom(*a, **k):
        raise RuntimeError("network")

    monkeypatch.setattr(ai.httpx, "post", boom)
    assert ai.complete("s", "u", kind="classify") is None


def test_remote_parse_error_returns_none(monkeypatch):
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "remote")
    monkeypatch.setenv("MAUEKSPOR_AI_API_KEY", "sk-test")

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            raise ValueError("bad json")

    monkeypatch.setattr(ai.httpx, "post", lambda *a, **k: FakeResp())
    assert ai.complete("s", "u", kind="classify") is None


def test_remote_empty_choices(monkeypatch):
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "remote")
    monkeypatch.setenv("MAUEKSPOR_AI_API_KEY", "sk-test")

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": []}

    monkeypatch.setattr(ai.httpx, "post", lambda *a, **k: FakeResp())
    assert ai.complete("s", "u", kind="classify") is None


def test_ask_json_parses_json_didalam_teks():
    # _mock menghasilkan JSON untuk kind classify; complete mock -> text JSON
    result = ai.ask_json("s", "u", kind="classify")
    assert isinstance(result, dict)
    assert result["hsCode"] == "0901.21"


def test_ask_json_teks_tanpa_braces_none():
    assert ai.ask_json("s", "u", kind="chat_reply") is None


def test_ask_json_braces_tapi_bukan_json_none(monkeypatch):
    # mock complete agar mengembalikan teks dengan { } tapi bukan JSON valid
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
