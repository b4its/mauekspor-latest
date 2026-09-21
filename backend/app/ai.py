"""AI Service untuk MauEkspor API - Enhanced with circuit breaker, health checks & multi-mode.

Mode Deployment:
- remote: calls actual AI endpoint (MAUEKSPOR_AI_BASE_URL)
- mock: deterministic canned responses (fallback, no AI)

Circuit Breaker:
- After N consecutive failures, stop trying AI for M seconds
- Auto-resets after cooldown period
- Prevents log flooding & latency spikes from repeated timeouts
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Optional

import httpx
from dotenv import load_dotenv

logger = logging.getLogger("mauekspor.ai")

# Load .env secara eksplisit dari direktori backend
_BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BACKEND_DIR / ".env")

MOCK = "mock"
REMOTE = "remote"

# Read from env — no hardcoded defaults in source
DEFAULT_BASE_URL = "http://localhost:20128/v1"
DEFAULT_MODEL = "qd/dmodel"
TIMEOUT_SECONDS = int(os.environ.get("MAUEKSPOR_AI_TIMEOUT", "60"))

# ── Circuit Breaker ──────────────────────────────────────────────────────────
_CB_FAILURE_COUNT: int = 0
_CB_LAST_FAILURE_TIME: float = 0.0
CB_FAILURE_THRESHOLD: int = 3        # open after N consecutive failures
CB_COOLDOWN_SECONDS: int = 120       # stay open for 2 minutes


def _cb_is_open() -> bool:
    """Return True if circuit breaker is open (skip AI calls)."""
    global _CB_FAILURE_COUNT, _CB_LAST_FAILURE_TIME
    if _CB_FAILURE_COUNT < CB_FAILURE_THRESHOLD:
        return False
    if time.monotonic() - _CB_LAST_FAILURE_TIME > CB_COOLDOWN_SECONDS:
        # Cooldown passed — reset and allow one probe
        logger.info("AI circuit breaker: cooldown elapsed, resetting")
        _CB_FAILURE_COUNT = 0
        _CB_LAST_FAILURE_TIME = 0.0
        return False
    return True


def _cb_record_failure() -> None:
    global _CB_FAILURE_COUNT, _CB_LAST_FAILURE_TIME
    _CB_FAILURE_COUNT += 1
    _CB_LAST_FAILURE_TIME = time.monotonic()
    if _CB_FAILURE_COUNT == CB_FAILURE_THRESHOLD:
        logger.warning(
            "AI circuit breaker OPEN after %d consecutive failures — skipping AI for %ds",
            CB_FAILURE_THRESHOLD, CB_COOLDOWN_SECONDS,
        )


def _cb_record_success() -> None:
    global _CB_FAILURE_COUNT, _CB_LAST_FAILURE_TIME
    if _CB_FAILURE_COUNT > 0:
        logger.info("AI circuit breaker: call succeeded, resetting failure count")
        _CB_FAILURE_COUNT = 0
        _CB_LAST_FAILURE_TIME = 0.0


# ── Mode helpers ──────────────────────────────────────────────────────────────
def mode() -> str:
    """Return current AI mode from environment (default: remote)."""
    return os.environ.get("MAUEKSPOR_AI_MODE", REMOTE).strip().lower()


def configured() -> bool:
    """Return True when the AI service is expected to answer requests."""
    if mode() == MOCK:
        return False
    return True


def get_base_url() -> str:
    """Return the AI base URL from env, with sensible default."""
    return os.environ.get("MAUEKSPOR_AI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def model_name() -> str:
    """Return the model name from env, with sensible default."""
    return os.environ.get("MAUEKSPOR_AI_MODEL", DEFAULT_MODEL)


def get_api_key() -> Optional[str]:
    """Return the API key when set, else None (anonymous calls allowed)."""
    return os.environ.get("MAUEKSPOR_AI_API_KEY") or None


# ── Endpoint health cache ─────────────────────────────────────────────────────
_HEALTH_CACHE: dict[str, bool] = {}
_LAST_HEALTH_TS: float = 0.0
HEALTH_CHECK_INTERVAL: int = 300   # re-probe every 5 minutes


def _probe_health(url: str) -> bool:
    """Return True if /models endpoint responds 200."""
    try:
        r = httpx.get(f"{url}/models", timeout=3, follow_redirects=True)
        return r.status_code == 200
    except Exception:
        return False


def _check_ai_health(url: str) -> bool:
    """Cached health check — re-probes at most every HEALTH_CHECK_INTERVAL seconds."""
    global _LAST_HEALTH_TS
    now = time.monotonic()
    if now - _LAST_HEALTH_TS < HEALTH_CHECK_INTERVAL:
        return _HEALTH_CACHE.get(url, False)
    _LAST_HEALTH_TS = now
    healthy = _probe_health(url)
    _HEALTH_CACHE[url] = healthy
    if healthy:
        logger.info("✅ AI health probe OK: %s", url)
    else:
        logger.warning("❌ AI health probe FAILED: %s", url)
    return healthy


# ── Mock provider ─────────────────────────────────────────────────────────────
_MOCK_OUTPUTS: dict[str, Any] = {
    "classify": {
        "hsCode": "0901.21",
        "confidence": 88,
        "reason": "Klasifikasi dari deskripsi produk berdasarkan HS 2022.",
    },
    "catalog_description": (
        "Kopi Gayo specialty single-origin dari dataran tinggi Aceh — arabika "
        "full-wash dengan profil rasa madu dan cokelat, cocok untuk pasar Jepang."
    ),
    "market_insight": {
        "score": 82,
        "insight": "Permintaan menguat menjelang musim libur; perhatikan label bilingual.",
    },
    "recommendations": {
        "confidence": 88,
        "score": 80,
        "recommendations": [
            {"type": "Certificate", "title": "Certificate of Origin", "status": "Required",
             "detail": "Confirm rules-of-origin."},
            {"type": "Document", "title": "Packing list", "status": "Required",
             "detail": "Match weights against invoice."},
        ],
    },
    "chat_reply": (
        "Maaf, layanan AI sedang tidak tersedia saat ini. "
        "Silakan coba lagi dalam beberapa menit atau hubungi administrator."
    ),
    "analytics_summary": (
        "Pipeline ekspor menunjukkan 3 trade lane aktif dengan readiness rata-rata 82%. "
        "Fokus utama: selesaikan compliance blocker critical."
    ),
    "pricing_insight": "Harga kompetitif untuk pasar target; pantau kurs dan freight.",
}


def _mock(kind: str) -> Optional[str]:
    """Return canned mock output for the given task type."""
    output = _MOCK_OUTPUTS.get(kind)
    if output is None:
        return None
    if isinstance(output, str):
        return output
    return json.dumps(output, ensure_ascii=False)


def fallback(kind: str) -> Optional[str]:
    """Public alias — callers use this when remote AI is unavailable."""
    return _mock(kind)


# ── Error pattern detection ───────────────────────────────────────────────────
_ERROR_PATTERNS = (
    "[qoder error", "[error", "error 401", "error 402", "error 403",
    "error 429", "insufficient_quota", "invalid api key", "rate limit",
    "timed out", "unavailable",
)


def _looks_like_error(content: str) -> bool:
    lowered = content.lower()
    return any(p in lowered for p in _ERROR_PATTERNS)


# ── Remote provider ────────────────────────────────────────────────────────────
def _call_remote(system: str, user: str) -> Optional[str]:
    """Call the AI API. Returns content string or None on any failure."""
    url = get_base_url()
    api_key_value = get_api_key()

    # Fast-path: circuit breaker open
    if _cb_is_open():
        logger.debug("AI circuit breaker open — skipping remote call")
        return None

    # Probe health (cached)
    if not _check_ai_health(url):
        _cb_record_failure()
        return None

    headers: dict[str, str] = {}
    if api_key_value:
        headers["Authorization"] = f"Bearer {api_key_value}"

    try:
        response = httpx.post(
            f"{url}/chat/completions",
            json={
                "model": model_name(),
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                "stream": False,
                "temperature": float(os.environ.get("MAUEKSPOR_AI_TEMPERATURE", "0.3")),
                "max_tokens": int(os.environ.get("MAUEKSPOR_AI_MAX_TOKENS", "1000")),
            },
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
    except httpx.ConnectTimeout:
        logger.warning("AI connect timeout (%s)", url)
        _cb_record_failure()
        return None
    except httpx.ConnectError:
        logger.warning("AI connection refused (%s)", url)
        _cb_record_failure()
        return None
    except httpx.TimeoutException:
        logger.warning("AI request timeout (%s)", url)
        _cb_record_failure()
        return None
    except Exception as exc:
        logger.warning("AI unexpected error (%s): %s", type(exc).__name__, str(exc)[:120])
        _cb_record_failure()
        return None

    if response.status_code != 200:
        logger.error("AI API returned HTTP %d for %s", response.status_code, url)
        _cb_record_failure()
        return None

    try:
        body = response.json()
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as exc:
        logger.error("AI response parse error: %s — body: %.200s", exc, response.text)
        _cb_record_failure()
        return None

    if not content or not str(content).strip():
        logger.warning("AI returned empty content")
        _cb_record_failure()
        return None

    if _looks_like_error(str(content)):
        logger.warning("AI returned error-like content: %.120s", str(content))
        _cb_record_failure()
        return None

    _cb_record_success()
    return str(content)


# ── Public API ────────────────────────────────────────────────────────────────
def complete(system: str, user: str, kind: str = "") -> Optional[str]:
    """Return AI-generated text, falling back to mock on any failure.

    Args:
        system: System instruction / context
        user:   User message / request
        kind:   Task type identifier for targeted mock fallback

    Returns:
        AI response string, or mock string, or None if both unavailable
    """
    if mode() == MOCK:
        return _mock(kind)

    result = _call_remote(system, user)
    if result:
        return result

    logger.info("AI remote unavailable — returning mock for kind=%r", kind)
    return _mock(kind)


def ask_json(system: str, user: str, kind: str = "") -> Optional[dict]:
    """Run AI and return parsed JSON dict, or None on failure."""
    text = complete(system, user, kind)
    if not text:
        return None
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        result = json.loads(match.group(0))
        return result if isinstance(result, dict) else None
    except json.JSONDecodeError as exc:
        logger.warning("AI JSON parse failed: %s", exc)
        return None


def get_ai_status() -> dict:
    """Return AI service status dict for /api/v1/ai/status/ endpoint."""
    url = get_base_url()
    cb_open = _cb_is_open()
    health = _HEALTH_CACHE.get(url, None)

    if cb_open:
        health_str = "circuit_open"
    elif health is True:
        health_str = "healthy"
    elif health is False:
        health_str = "unhealthy"
    else:
        health_str = "not_checked"

    return {
        "mode": mode(),
        "configured": configured(),
        "health": health_str,
        "circuit_breaker": "open" if cb_open else "closed",
        "consecutive_failures": _CB_FAILURE_COUNT,
        "endpoint": url,
        "model": model_name(),
    }
