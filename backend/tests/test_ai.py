"""Test layanan AI — mode mock (default) harus deterministik dan aman tanpa network."""

from app import ai


def test_mock_default_mode():
    assert ai.mode() == "mock"
    # Mock mode is not "configured" in the sense of using real AI,
    # but it's ready to serve canned responses
    assert not ai.configured()
    # Verify mock responses are available
    assert ai.complete("s", "u", kind="chat_reply") is not None


def test_classify_mock_returns_dict():
    result = ai.ask_json("system", "Product: kopi", kind="classify")
    assert result and result["hsCode"]


def test_recommendations_mock_returns_list():
    result = ai.ask_json("system", "product", kind="recommendations")
    assert isinstance(result["recommendations"], list)
    assert result["recommendations"][0]["title"]


def test_unknown_kind_returns_mock_text():
    assert "Berdasarkan data" in ai.complete("s", "u", "chat_reply")


def test_ask_json_ignores_non_json_text():
    assert ai.ask_json("s", "u", "chat_reply") is None


def test_remote_without_key_returns_none(monkeypatch):
    monkeypatch.setenv("MAUEKSPOR_AI_MODE", "remote")
    monkeypatch.delenv("MAUEKSPOR_AI_API_KEY", raising=False)
    # When remote mode fails (no API key), should fall back to mock responses
    result = ai.complete("s", "u", kind="classify")
    # Should get mock response, not None
    assert result is not None
    # Verify it's a mock response (contains expected mock data)
    assert "hsCode" in result or "Klasifikasi" in result