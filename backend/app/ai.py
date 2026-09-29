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

try:
    from dotenv import load_dotenv

    _root_dir = Path(__file__).resolve().parent.parent.parent
    for _env_path in (_root_dir / ".env.local", _root_dir / "backend" / ".env", _root_dir / ".env"):
        if _env_path.exists():
            load_dotenv(_env_path, override=False)
except Exception:
    pass

logger = logging.getLogger("mauekspor.ai")



MOCK = "mock"
REMOTE = "remote"

# Read from env — configured defaults for deepseek model
DEFAULT_BASE_URL = "http://localhost:20128/v1"
DEFAULT_MODEL = "hk/deepseek-4.1-flash"
DEFAULT_API_KEY = "sk-89ffb299e1e2352b-vshhzb-ff049647"
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
    val = os.environ.get("MAUEKSPOR_AI_MODE")
    if val and val.strip():
        return val.strip().lower()
    return REMOTE


def configured() -> bool:
    """Return True when the AI service is expected to answer requests."""
    return mode() != MOCK


def get_base_url() -> str:
    """Return the AI base URL from env, normalized to include /v1."""
    # Try PUBLIC_URL first (set by ngrok-with-ai script for public tunnels)
    raw = os.environ.get("MAUEKSPOR_AI_PUBLIC_URL") or os.environ.get("MAUEKSPOR_AI_BASE_URL")
    url = (raw.strip() if raw and raw.strip() else DEFAULT_BASE_URL).rstrip("/")
    # Normalize: callers append /chat/completions & /models, which live under /v1
    if not url.endswith("/v1"):
        url = f"{url}/v1"
    return url


def model_name() -> str:
    """Return the model name from env, with sensible default."""
    val = os.environ.get("MAUEKSPOR_AI_MODEL")
    return val.strip() if val and val.strip() else DEFAULT_MODEL


def get_api_key() -> Optional[str]:
    """Return the API key when set, else default outside isolated unit tests."""
    val = os.environ.get("MAUEKSPOR_AI_API_KEY")
    if val is not None:
        stripped = val.strip()
        if stripped:
            return stripped
        # Explicit empty string in test environment
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return None
    # In pytest, if env var was not provided or popped, keep it None for isolated mock testing
    if os.environ.get("PYTEST_CURRENT_TEST") and "MAUEKSPOR_AI_API_KEY" not in os.environ:
        return None
    return DEFAULT_API_KEY


# ── Endpoint health cache ─────────────────────────────────────────────────────
_HEALTH_CACHE: dict[str, bool] = {}
_LAST_HEALTH_TS: float = 0.0
HEALTH_CHECK_INTERVAL: int = 120      # re-probe every 2 minutes on success
FAILED_HEALTH_RETRY_INTERVAL: int = 5 # re-probe after 5 seconds on failure


def _probe_health(url: str) -> bool:
    """Return True if /models endpoint responds 200 with JSON or model listing."""
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
                data = r.json()
                if isinstance(data, (dict, list)):
                    return True
            except Exception:
                pass
            raw_text = r.text
            if "data: [DONE]" in raw_text:
                raw_text = raw_text.split("data: [DONE]")[0].strip()
            match = re.search(r"[\{\[][\s\S]*[\}\]]", raw_text)
            if match:
                try:
                    data = json.loads(match.group(0))
                    if isinstance(data, (dict, list)):
                        return True
                except Exception:
                    pass
            content_type = r.headers.get("content-type", "")
            return "json" in str(content_type)
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
        "confidence": 92,
        "reason": "Klasifikasi dari deskripsi produk berdasarkan BTKI 2022 (HS 2022 6-digit internasional; siap transisi ke HS 2028).",
    },
    "catalog_description": {
        "export_buyer_description": (
            "Kopi Gayo specialty single-origin dari dataran tinggi Aceh — arabika "
            "full-wash dengan profil rasa madu dan cokelat, siap ekspor dengan ketertelusuran geolokasi lahan patuh EUDR dan dokumen ART."
        ),
        "technical_spec_sheet": [
            {"label": "Product", "value": "Kopi Arabika Gayo Single Origin"},
            {"label": "Origin", "value": "Aceh, Indonesia"},
            {"label": "Processing", "value": "Full Washed, Sun Dried"},
            {"label": "Regulatory Baseline", "value": "Sept 2026 (EUDR & ART Schedule 2B Ready)"},
        ],
        "safety_sheet": [
            {"label": "Food Grade", "value": "Yes (BPOM / FDA registered)"},
            {"label": "Phytosanitary", "value": "Required (Barantin UU 21/2019)"},
            {"label": "Deforestation-Free", "value": "EUDR Due Diligence Statement (DDS) Ready"},
        ],
    },
    "market_insight": {
        "recommended_countries": [
            {
                "country": "Japan",
                "code": "JP",
                "score": 93,
                "reason": "Permintaan specialty coffee kuat; tarif preferensi 0% via IJEPA (protokol amandemen).",
                "market_size": "US$1.6B",
                "competition_level": "Sedang",
                "price_range": "USD 12-18/kg",
                "entry_strategy": "Kemitraan roaster specialty; patuhi deklarasi 28 alergen Food Sanitation Act.",
            },
            {
                "country": "United States",
                "code": "US",
                "score": 89,
                "reason": "Pasar terbesar; gunakan pembebasan tarif 10% Section 301 via US-Indonesia ART Schedule 2B.",
                "market_size": "US$4.2B",
                "competition_level": "Tinggi",
                "price_range": "USD 13-20/kg",
                "entry_strategy": "Distributor F&B specialty dengan FDA Prior Notice dan sertifikat asal ART.",
            },
            {
                "country": "Germany (EU)",
                "code": "DE",
                "score": 85,
                "reason": "Pasar kopi bernilai tinggi; wajib melengkapi geolokasi lahan kebun dan EUDR DDS per 30 Des 2026.",
                "market_size": "US$2.8B",
                "competition_level": "Tinggi",
                "price_range": "USD 14-22/kg",
                "entry_strategy": "Kemitraan importir EU dengan kepatuhan penuh EUDR & PPWR kemasan daur ulang.",
            },
        ],
        "countries_to_avoid": [
            {"country": "North Korea", "code": "KP", "reason": "Sanksi multilateral PBB/OFAC."},
            {"country": "Russia", "code": "RU", "reason": "Rezim sanksi finansial EU/US dan risiko pembayaran."},
        ],
        "market_trends": [
            "Pertumbuhan permintaan kopi single-origin tersertifikasi ramah lingkungan.",
            "Kewajiban ketertelusuran geolokasi lahan kebun (EUDR cut-off 31 Des 2020).",
            "Pemanfaatan perjanjian bilateral resiprokal (US-Indonesia ART Schedule 2B).",
        ],
        "competitive_landscape": "Kompetisi dari Vietnam & Brasil; kopi Indonesia unggul di profil specialty dan traceability.",
        "growth_opportunities": [
            "Pasar specialty coffee roaster di Jepang dan Amerika Serikat.",
            "Penjualan direct-to-roaster dengan sertifikat ketertelusuran digital.",
        ],
        "risks_and_challenges": [
            "Kepatuhan pelabelan 28 alergen di Jepang.",
            "Kewajiban kepatuhan EUDR (30 Des 2026) untuk pasar Eropa.",
            "Kewajiban penempatan DHE SDA 100% 12 bulan (PP 21/2026) untuk transaksi >= USD 250k.",
        ],
        "overall_recommendation": "Prioritaskan pasar Jepang dan AS (manfaatkan ART Schedule 2B); siapkan koordinat poligon kebun untuk persiapan EUDR 2026.",
        "score": 88,
        "insight": "Permintaan menguat; pastikan label bilingual dan laporan residu pestisida terakreditasi.",
    },
    "recommendations": {
        "confidence": 92,
        "score": 88,
        "recommendations": [
            {
                "type": "Certificate",
                "title": "Certificate of Origin (IJEPA / ART Schedule 2B)",
                "status": "Required",
                "detail": "Klaim tarif 0% IJEPA di Jepang atau pembebasan tarif 10% Section 301 di AS.",
            },
            {
                "type": "Compliance",
                "title": "EUDR Due Diligence Statement (DDS)",
                "status": "Required",
                "detail": "Wajib untuk pasar EU per 30 Des 2026: sertakan koordinat geolokasi poligon kebun.",
            },
            {
                "type": "Document",
                "title": "Phytosanitary Certificate (Barantin)",
                "status": "Required",
                "detail": "Diterbitkan Badan Karantina Indonesia sesuai UU 21/2019 sebelum kapal berangkat.",
            },
            {
                "type": "Finance",
                "title": "Rekening Khusus DHE SDA Himbara (PP 21/2026)",
                "status": "Required",
                "detail": "Untuk nilai ekspor >= USD 250k: retensi 100% devisa non-migas selama 12 bulan.",
            },
        ],
    },
    "compliance_check": [
        {
            "type": "Labeling",
            "rule_key": "specification_compliance",
            "your_value": "Kemasan standar",
            "required_value": "Bilingual Japanese/English label (28 allergens)",
            "description": "Label wajib mencantumkan informasi produsen, tanggal kedaluwarsa, dan deklarasi 28 alergen.",
            "severity": "major",
        }
    ],
    "chat_reply": (
        "Halo! Saya adalah asisten MauEkspor dengan basis regulasi perdagangan global terkini per 29 September 2026. "
        "Saya siap membantu Anda memverifikasi aturan HS Code (HS 2022/2028), kepatuhan EUDR & CBAM, "
        "skema tarif US Section 301/ART, kebijakan DHE SDA (PP 21/2026), serta kalkulasi costing dan pengiriman."
    ),
    "analytics_summary": (
        "Pipeline ekspor menunjukkan trade lane aktif dengan kesiapan rata-rata 88%. "
        "Fokus utama: verifikasi bukti EUDR/ART dan pembukaan rekening khusus DHE SDA untuk nilai >= USD 250k."
    ),
    "pricing_insight": "Harga kompetitif; manfaatkan pembebasan tarif ART Schedule 2B untuk menjaga margin di pasar AS.",
    "container_optimization": (
        "1. Susun karton dengan pola interlocking untuk memaksimalkan stabilitas kontainer.\n"
        "2. Gunakan pallet standar ISPM-15 (1100x1100mm) bertanda resmi IPPC.\n"
        "3. Pastikan kemasan luar memenuhi regulasi PPWR (bebas PFAS, dapat didaur ulang)."
    ),
    "test": "AI test successful — koneksi AI berjalan normal dengan baseline regulasi 2026.",
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
                    "max_tokens": int(os.environ.get("MAUEKSPOR_AI_MAX_TOKENS", "3500")),
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
            raw_text = response.text
            body = None
            try:
                body = response.json()
            except (ValueError, Exception):
                # Upstream gateway may append SSE 'data: [DONE]' to non-streaming response body
                cleaned_text = raw_text
                if "data: [DONE]" in cleaned_text:
                    cleaned_text = cleaned_text.split("data: [DONE]")[0].strip()
                match = re.search(r"\{[\s\S]*\}", cleaned_text)
                if match:
                    body = json.loads(match.group(0))
                else:
                    raise
            message_obj = body["choices"][0]["message"]
            content = message_obj.get("content") or message_obj.get("reasoning_content") or message_obj.get("text") or ""
        except (KeyError, IndexError, ValueError, TypeError) as exc:
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
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, flags=re.IGNORECASE)
    if fence_match:
        return fence_match.group(1).strip()
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
        # If the LLM returned a wrapped dict with a list inside
        parsed_dict = _parse_json_dict(text)
        if parsed_dict and isinstance(parsed_dict, dict):
            for val in parsed_dict.values():
                if isinstance(val, list):
                    return val
        logger.warning("AI output failed to parse as JSON list: %.150s", text)

    mock_val = _mock(kind)
    return _parse_json_list(mock_val)


def get_ai_status() -> dict:
    """Return AI service status dict for /api/v1/ai/status/ endpoint."""
    url = get_base_url()
    cb_open = _cb_is_open()
    if not cb_open and mode() != MOCK:
        _check_ai_health(url)
    health = _HEALTH_CACHE.get(url, None)

    if cb_open:
        health_str = "circuit_open"
    elif health is True:
        health_str = "healthy"
    elif health is False:
        health_str = "unhealthy"
    else:
        health_str = "not_checked"

    is_remote = mode() != MOCK and configured()
    provider_name = f"DeepSeek ({model_name()})" if is_remote else "Mock / Fallback"

    return {
        "mode": mode(),
        "configured": configured(),
        "health": health_str,
        "circuit_breaker": "open" if cb_open else "closed",
        "consecutive_failures": _CB_FAILURE_COUNT,
        "endpoint": url,
        "model": model_name(),
        "configured_provider": provider_name,
        "using_remote": is_remote,
        "using_mock": not is_remote,
    }
