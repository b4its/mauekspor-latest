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

logger = logging.getLogger("mauekspor.ai")



MOCK = "mock"
REMOTE = "remote"

# Read from env — configured defaults for deepseek model
DEFAULT_BASE_URL = "http://localhost:20128/v1"
DEFAULT_MODEL = "hk/deepseek-4.1-flash"
TIMEOUT_SECONDS = int(os.environ.get("MAUEKSPOR_AI_TIMEOUT", "60"))

# Health probe hits /models
HEALTH_TIMEOUT_SECONDS = int(os.environ.get("MAUEKSPOR_AI_HEALTH_TIMEOUT", "15"))

# ── Circuit Breaker ──────────────────────────────────────────────────────────
_CB_FAILURE_COUNT: int = 0
_CB_LAST_FAILURE_TIME: float = 0.0
CB_FAILURE_THRESHOLD: int = 5        # open after N consecutive failures
CB_COOLDOWN_SECONDS: int = 30        # stay open for 30 seconds

def _cb_is_open() -> bool:
    """Return True if circuit breaker is open (skip AI calls)."""
    global _CB_FAILURE_COUNT, _CB_LAST_FAILURE_TIME
    if _CB_FAILURE_COUNT < CB_FAILURE_THRESHOLD:
        return False
    if time.monotonic() - _CB_LAST_FAILURE_TIME > CB_COOLDOWN_SECONDS:
        # Cooldown passed — reset and allow probe
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
    """Return the AI base URL from env, normalized to include /v1."""
    # Try PUBLIC_URL first (set by ngrok-with-ai script for public tunnels)
    url = os.environ.get("MAUEKSPOR_AI_PUBLIC_URL") or \
          os.environ.get("MAUEKSPOR_AI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    # Normalize: callers append /chat/completions & /models, which live under /v1
    if not url.endswith("/v1"):
        url = f"{url}/v1"
    return url


def model_name() -> str:
    """Return the model name from env, with sensible default."""
    return os.environ.get("MAUEKSPOR_AI_MODEL", DEFAULT_MODEL)


def get_api_key() -> Optional[str]:
    """Return the API key when set, else None (anonymous calls allowed)."""
    return os.environ.get("MAUEKSPOR_AI_API_KEY") or None


# ── Endpoint health cache ─────────────────────────────────────────────────────
_HEALTH_CACHE: dict[str, bool] = {}
_LAST_HEALTH_TS: float = 0.0
HEALTH_CHECK_INTERVAL: int = 120      # re-probe every 2 minutes on success
FAILED_HEALTH_RETRY_INTERVAL: int = 5 # re-probe after 5 seconds on failure


def _probe_health(url: str) -> bool:
    """Return True if /models endpoint responds 200 with JSON."""
    headers: dict[str, str] = {"ngrok-skip-browser-warning": "true"}
    api_key_value = get_api_key()
    if api_key_value:
        headers["Authorization"] = f"Bearer {api_key_value}"
    try:
        r = httpx.get(
            f"{url}/models",
            timeout=HEALTH_TIMEOUT_SECONDS,
            follow_redirects=True,
            headers=headers,
        )
        if r.status_code == 200:
            try:
                if hasattr(r, "json") and callable(r.json):
                    data = r.json()
                    if isinstance(data, (dict, list)):
                        return True
            except Exception:
                pass
            r_headers = getattr(r, "headers", {}) or {}
            content_type = r_headers.get("content-type", "") if hasattr(r_headers, "get") else ""
            text = getattr(r, "text", "") or ""
            return "json" in str(content_type) or text.strip().startswith("{") or text.strip().startswith("[")
        return False
    except Exception as exc:
        logger.debug("Health probe exception for %s: %s", url, exc)
        return False


def _check_ai_health(url: str) -> bool:
    """Cached health check — re-probes every HEALTH_CHECK_INTERVAL (or 5s on failure)."""
    global _LAST_HEALTH_TS
    now = time.monotonic()
    cached = _HEALTH_CACHE.get(url)
    if cached is True and (now - _LAST_HEALTH_TS < HEALTH_CHECK_INTERVAL):
        return True
    if cached is False and (now - _LAST_HEALTH_TS < FAILED_HEALTH_RETRY_INTERVAL):
        return False

    healthy = _probe_health(url)
    _HEALTH_CACHE[url] = healthy
    _LAST_HEALTH_TS = now
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
    "catalog_description": {
        "export_buyer_description": (
            "Kopi Gayo specialty single-origin dari dataran tinggi Aceh — arabika "
            "full-wash dengan profil rasa madu dan cokelat, cocok untuk pasar Jepang."
        ),
        "technical_spec_sheet": [
            {"label": "Product", "value": "Kopi Arabika Gayo"},
            {"label": "Origin", "value": "Aceh, Indonesia"},
            {"label": "Processing", "value": "Full Washed"},
        ],
        "safety_sheet": [
            {"label": "Food Grade", "value": "Yes"},
            {"label": "Phytosanitary", "value": "Required"},
        ],
    },
    "market_insight": {
        "recommended_countries": [
            {
                "country": "Japan",
                "code": "JP",
                "score": 92,
                "reason": "Tingginya apresiasi kopi specialty Indonesia.",
                "market_size": "Besar",
                "competition_level": "Sedang",
                "price_range": "USD 12-18/kg",
                "entry_strategy": "Kemitraan roaster specialty.",
            },
            {
                "country": "Singapore",
                "code": "SG",
                "score": 88,
                "reason": "Hub perdagangan regional dan konsumsi specialty tinggi.",
                "market_size": "Menengah",
                "competition_level": "Tinggi",
                "price_range": "USD 11-16/kg",
                "entry_strategy": "Distributor F&B premium.",
            },
        ],
        "countries_to_avoid": [],
        "market_trends": [
            "Pertumbuhan permintaan kopi single-origin tersertifikasi.",
            "Peningkatan kesadaran direct trade.",
        ],
        "competitive_landscape": "Pasar kompetitif namun terbuka bagi kopi dengan traceability jelas.",
        "growth_opportunities": [
            "Pasar specialty coffee shop",
            "Penjualan online B2B direct to roaster",
        ],
        "risks_and_challenges": [
            "Regulasi residu pestisida ketat",
            "Fluktuasi biaya logistik laut",
        ],
        "overall_recommendation": "Prioritaskan pasar Jepang dengan sertifikasi asal dan lab test lengkap.",
        "score": 82,
        "insight": "Permintaan menguat menjelang musim libur; perhatikan label bilingual.",
    },
    "recommendations": {
        "confidence": 88,
        "score": 85,
        "recommendations": [
            {
                "type": "Certificate",
                "title": "Certificate of Origin (Form A/EPA)",
                "status": "Required",
                "detail": "Konfirmasi aturan asal barang untuk fasilitas tarif preferensi.",
            },
            {
                "type": "Document",
                "title": "Phytosanitary Certificate",
                "status": "Required",
                "detail": "Diterbitkan oleh Badan Karantina Indonesia sebelum keberangkatan.",
            },
            {
                "type": "Document",
                "title": "Packing list & Invoice",
                "status": "Required",
                "detail": "Pastikan deskripsi dan berat bersih identik dengan B/L.",
            },
        ],
    },
    "compliance_check": [
        {
            "type": "Labeling",
            "rule_key": "specification_compliance",
            "your_value": "Kemasan standar",
            "required_value": "Bilingual Japanese/English label",
            "description": "Label wajib mencantumkan informasi produsen dan tanggal kedaluwarsa.",
            "severity": "major",
        }
    ],
    "chat_reply": (
        "Halo! Saya adalah asisten MauEkspor. Saya siap membantu Anda menganalisa produk, "
        "kepatuhan regulasi, penetapan harga ekspor, serta persiapan pengiriman internasional."
    ),
    "analytics_summary": (
        "Pipeline ekspor menunjukkan trade lane aktif dengan kesiapan rata-rata 85%. "
        "Fokus utama: selesaikan verifikasi kepatuhan dan dokumen karantina."
    ),
    "pricing_insight": "Harga kompetitif untuk pasar target; pantau kurs dan freight.",
    "container_optimization": (
        "1. Susun karton dengan pola interlocking untuk memaksimalkan stabilitas.\n"
        "2. Gunakan pallet standar ISPM-15 (1100x1100mm) untuk efisiensi ruang 20ft.\n"
        "3. Pertimbangkan shrink wrap heavy-duty untuk proteksi kelembaban kontainer laut."
    ),
    "test": "AI test successful — koneksi AI berjalan normal.",
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
    """Call the AI API with retry on transient queue/rate-limits. Returns content string or None."""
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

    headers: dict[str, str] = {
        "ngrok-skip-browser-warning": "true",
    }
    if api_key_value:
        headers["Authorization"] = f"Bearer {api_key_value}"

    content = None
    for attempt in range(2):
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
                    "temperature": float(os.environ.get("MAUEKSPOR_AI_TEMPERATURE", "0.2")),
                    "max_tokens": int(os.environ.get("MAUEKSPOR_AI_MAX_TOKENS", "1500")),
                },
                headers=headers,
                timeout=TIMEOUT_SECONDS,
            )
        except httpx.ConnectTimeout:
            logger.warning("AI connect timeout (%s)", url)
            if attempt == 0:
                time.sleep(1.0)
                continue
            _cb_record_failure()
            return None
        except httpx.ConnectError:
            logger.warning("AI connection refused (%s)", url)
            _cb_record_failure()
            return None
        except httpx.TimeoutException:
            logger.warning("AI request timeout (%s)", url)
            if attempt == 0:
                time.sleep(1.0)
                continue
            _cb_record_failure()
            return None
        except Exception as exc:
            logger.warning("AI unexpected error (%s): %s", type(exc).__name__, str(exc)[:120])
            _cb_record_failure()
            return None

        if response.status_code in (429, 502, 503):
            logger.warning("AI temporary HTTP %d for %s (attempt %d)", response.status_code, url, attempt + 1)
            if attempt == 0:
                time.sleep(1.5)
                continue
            _cb_record_failure()
            return None

        if response.status_code != 200:
            logger.error("AI API returned HTTP %d for %s", response.status_code, url)
            _cb_record_failure()
            return None

        try:
            try:
                body = response.json()
            except (ValueError, Exception):
                # Upstream gateway may append SSE 'data: [DONE]' to non-streaming response body
                raw_text = response.text
                if "data: [DONE]" in raw_text:
                    raw_text = raw_text.split("data: [DONE]")[0].strip()
                match = re.search(r"\{[\s\S]*\}", raw_text)
                if match:
                    body = json.loads(match.group(0))
                else:
                    raise
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            logger.error("AI response parse error: %s — body: %.200s", exc, response.text)
            if attempt == 0:
                time.sleep(1.0)
                continue
            _cb_record_failure()
            return None

        if not content or not str(content).strip():
            logger.warning("AI returned empty content")
            if attempt == 0:
                time.sleep(1.0)
                continue
            _cb_record_failure()
            return None

        content_str = str(content)
        # Check for transient queue error in body (e.g. HolverAI error 403 / isQueued)
        if "isqueued" in content_str.lower() or "queuecount" in content_str.lower():
            logger.info("AI request was queued by provider, waiting 1.5s to retry...")
            if attempt == 0:
                time.sleep(1.5)
                continue

        if _looks_like_error(content_str):
            logger.warning("AI returned error-like content: %.120s", content_str)
            _cb_record_failure()
            return None

        _cb_record_success()
        return content_str

    _cb_record_failure()
    return None


# ── Public API ────────────────────────────────────────────────────────────────
def complete(system: str, user: str, kind: str = "") -> Optional[str]:
    """Return AI-generated text, falling back to mock on any failure."""
    if mode() == MOCK:
        return _mock(kind)

    result = _call_remote(system, user)
    if result:
        return result

    logger.info("AI remote unavailable — returning mock for kind=%r", kind)
    return _mock(kind)


def _clean_json_text(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE).strip()
    return cleaned


def _parse_json_dict(text: str | None) -> Optional[dict]:
    if not text:
        return None
    cleaned = _clean_json_text(text)
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        raw_json = match.group(0)
        try:
            data = json.loads(raw_json)
            if isinstance(data, dict):
                return data
        except Exception:
            sanitized = re.sub(r",\s*([\}\]])", r"\1", raw_json)
            try:
                data = json.loads(sanitized)
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
    return None


def _parse_json_list(text: str | None) -> Optional[list]:
    if not text:
        return None
    cleaned = _clean_json_text(text)
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
    except Exception:
        pass

    match = re.search(r"\[[\s\S]*\]", cleaned)
    if match:
        raw_json = match.group(0)
        try:
            data = json.loads(raw_json)
            if isinstance(data, list):
                return data
        except Exception:
            sanitized = re.sub(r",\s*([\}\]])", r"\1", raw_json)
            try:
                data = json.loads(sanitized)
                if isinstance(data, list):
                    return data
            except Exception:
                pass
    return None


def ask_json(system: str, user: str, kind: str = "") -> Optional[dict]:
    """Run AI and return parsed JSON dict, or mock fallback on failure."""
    if mode() == MOCK:
        mock_val = _mock(kind)
        return _parse_json_dict(mock_val)

    sys_prompt = (
        system
        + "\nYou must return ONLY a single valid JSON object. "
        "Do not include any markdown fences, comments, or conversational text outside the JSON."
    )
    usr_prompt = (
        user
        + "\n\nIMPORTANT: Respond ONLY with a valid JSON object matching the requested schema. "
        "Do not output markdown code fences, greetings, or text outside the JSON."
    )
    text = _call_remote(sys_prompt, usr_prompt)
    if text:
        parsed = _parse_json_dict(text)
        if parsed is not None:
            return parsed
        logger.warning("AI output failed to parse as JSON dict: %.150s", text)

    logger.info("AI remote JSON unavailable — returning mock for kind=%r", kind)
    mock_val = _mock(kind)
    return _parse_json_dict(mock_val)


def ask_json_list(system: str, user: str, kind: str = "") -> Optional[list]:
    """Run AI and return parsed JSON list, or None on failure."""
    if mode() == MOCK:
        mock_val = _mock(kind)
        return _parse_json_list(mock_val)

    sys_prompt = (
        system
        + "\nYou must return ONLY a single valid JSON array (list of objects). "
        "Do not include any markdown fences, comments, or conversational text outside the JSON array."
    )
    usr_prompt = (
        user
        + "\n\nIMPORTANT: Respond ONLY with a valid JSON array matching the requested schema. "
        "Do not output markdown code fences, greetings, or text outside the JSON array."
    )
    text = _call_remote(sys_prompt, usr_prompt)
    if text:
        parsed = _parse_json_list(text)
        if parsed is not None:
            return parsed
        logger.warning("AI output failed to parse as JSON list: %.150s", text)

    mock_val = _mock(kind)
    return _parse_json_list(mock_val)


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
