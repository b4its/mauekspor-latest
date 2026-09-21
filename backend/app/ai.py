"""AI Service untuk MauEkspor API - Enhanced with health checks & multi-mode support.

Mode Deployment:
- LOCAL (default): AI endpoint di localhost:20128 (development)
- REMOTE: External AI provider (OpenAI-compatible)
- MOCK: Deterministic canned responses (fallback/no AI)

Health Detection:
- Backend auto-detects AI availability on first request
- Stores result in cache untuk subsequent requests
- Shows status indicator dalam response meta
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
LOCALHOST = "localhost"  # Default untuk development lokal

DEFAULT_BASE_URL = "http://localhost:20128/v1"
DEFAULT_MODEL = "qd/dmodel"
TIMEOUT_SECONDS = 60

# Global cache untuk AI health status
_AI_HEALTH_CHECK_CACHE: dict[str, bool] = {}
_LAST_HEALTH_CHECK: float = 0
HEALTH_CHECK_INTERVAL = 300  # Cek setiap 5 menit


def mode() -> str:
    """Return current AI mode from environment."""
    return os.environ.get("MAUEKSPOR_AI_MODE", LOCALHOST).strip().lower()


def configured() -> bool:
    """Check if AI is properly configured."""
    ai_mode = mode()
    if ai_mode == MOCK:
        return False
    if ai_mode == REMOTE:
        return bool(os.environ.get("MAUEKSPOR_AI_API_KEY", "").strip())
    # localhost mode
    return True


def get_base_url() -> str:
    """Get AI base URL based on mode."""
    ai_mode = mode()
    
    if ai_mode == REMOTE:
        return os.environ.get("MAUEKSPOR_AI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    elif ai_mode == LOCALHOST:
        # Try multiple potential endpoints for flexibility
        potential_urls = [
            os.environ.get("MAUEKSPOR_AI_BASE_URL"),  # Explicit config
            "http://host.docker.internal:20128/v1",  # Docker
            "http://172.17.0.1:20128/v1",  # Docker bridge gateway
            "http://192.168.1.1:20128/v1",  # Common host IP
            "http://localhost:20128/v1",  # Direct localhost
        ]
        
        for url in potential_urls:
            if url:
                url = url.rstrip("/")
                try:
                    response = httpx.get(f"{url}/models", timeout=2)
                    if response.status_code == 200:
                        logger.info(f"AI endpoint detected: {url}")
                        return url
                except Exception:
                    continue
        
        logger.warning("No AI endpoint found, using localhost as fallback")
        return "http://localhost:20128/v1"
    
    return DEFAULT_BASE_URL


def model_name() -> str:
    """Get AI model name."""
    ai_mode = mode()
    if ai_mode == REMOTE:
        return os.environ.get("MAUEKSPOR_AI_MODEL", DEFAULT_MODEL)
    return DEFAULT_MODEL


def get_api_key() -> Optional[str]:
    """Get API key for remote mode."""
    if mode() == REMOTE:
        return os.environ.get("MAUEKSPOR_AI_API_KEY", "") or None
    return None


def _check_ai_health(url: str) -> bool:
    """Check if AI endpoint is healthy and accessible."""
    global _LAST_HEALTH_CHECK
    
    # Skip if checked recently
    if time.time() - _LAST_HEALTH_CHECK < HEALTH_CHECK_INTERVAL:
        return _AI_HEALTH_CHECK_CACHE.get(url, False)
    
    _LAST_HEALTH_CHECK = time.time()
    
    try:
        response = httpx.get(
            f"{url}/models",
            timeout=3,
            follow_redirects=True
        )
        is_healthy = response.status_code == 200
        _AI_HEALTH_CHECK_CACHE[url] = is_healthy
        
        if is_healthy:
            logger.info("✅ AI service is healthy and accessible")
        else:
            logger.warning(f"❌ AI endpoint returned {response.status_code}")
            
        return is_healthy
        
    except httpx.ConnectTimeout:
        logger.warning("⚠️  AI endpoint connection timeout")
        _AI_HEALTH_CHECK_CACHE[url] = False
        return False
    except httpx.ConnectError:
        logger.warning("⚠️  AI endpoint not accessible (Connection refused)")
        _AI_HEALTH_CHECK_CACHE[url] = False
        return False
    except Exception as e:
        logger.warning(f"⚠️  AI health check failed: {type(e).__name__}: {e}")
        _AI_HEALTH_CHECK_CACHE[url] = False
        return False


def _looks_like_error(content: str) -> bool:
    """Detect error patterns in AI response."""
    error_patterns = [
        "[qoder error",
        "error 401", "error 402", "error 403", "error 429",
        "insufficient_quota",
        "invalid api key",
        "rate limit",
        "timed out",
        "unavailable",
        "not found",
    ]
    lowered = content.lower()
    return any(pattern in lowered for pattern in error_patterns)


# ---------------------------------------------------------------------------
# Mock provider (deterministic per jenis tugas)
# ---------------------------------------------------------------------------
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
            {"type": "Certificate", "title": "Certificate of Origin", "status": "Required"},
            {"type": "Document", "title": "Packing list", "status": "Required"},
        ],
    },
    "chat_reply": (
        "Berdasarkan data workspace Anda, langkah berikutnya adalah memastikan "
        "bukti label dan dokumen pelaporan sudah lengkap sebelum quote dikirim. "
        "Ada hal lain yang ingin Anda tanya?"
    ),
    "analytics_summary": (
        "Pipeline ekspor menunjukkan 3 trade lane aktif dengan readiness rata-rata 82%. "
        "Fokus utama: selesaikan compliance blocker critical."
    ),
    "pricing_insight": "Harga kompetitif untuk pasar target; pantau kurs dan freight.",
}


def _mock(kind: str) -> str | None:
    """Return mock output for given task type."""
    output = _MOCK_OUTPUTS.get(kind)
    if output is None:
        return None
    if isinstance(output, str):
        return output
    return json.dumps(output, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Remote provider (OpenAI-compatible endpoints)
# ---------------------------------------------------------------------------
def _remote(system: str, user: str, kind: str = "") -> Optional[str]:
    """Call the actual AI endpoint."""
    
    # Check if we're in mock mode
    if mode() == MOCK:
        logger.warning("AI mode set to 'mock' - returning canned responses")
        return _mock(kind)
    
    url = get_base_url()
    model = model_name()
    api_key_value = get_api_key()
    
    # Check AI health before attempting request
    is_healthy = _check_ai_health(url)
    
    if not is_healthy:
        logger.warning("AI endpoint unhealthy, falling back to mock responses")
        return _mock(kind)
    
    try:
        headers = {}
        if api_key_value:
            headers["Authorization"] = f"Bearer {api_key_value}"
        
        response = httpx.post(
            f"{url}/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "temperature": 0.3,
                "max_tokens": 1000,
            },
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
        
        if response.status_code != 200:
            logger.error(f"AI API returned HTTP {response.status_code}")
            return _mock(kind)
            
        body = response.json()
        content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if not content or not str(content).strip():
            logger.warning("AI returned empty content")
            return _mock(kind)
            
        if _looks_like_error(str(content)):
            logger.warning(f"AI returned error-like content: {str(content)[:200]}")
            return _mock(kind)
            
        return str(content)
        
    except httpx.ConnectTimeout:
        logger.warning("AI request timed out")
        return _mock(kind)
    except httpx.ConnectError:
        logger.warning("AI connection refused")
        return _mock(kind)
    except Exception as exc:
        logger.warning(f"AI request failed ({type(exc).__name__}): {str(exc)[:100]}")
        return _mock(kind)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def complete(system: str, user: str, kind: str = "") -> str | None:
    """Get AI completion text or fallback to mock.
    
    Args:
        system: System instruction/context
        user: User's actual question/request  
        kind: Task type identifier for mock fallback
        
    Returns:
        AI-generated text response, or None if both remote and mock fail
    """
    
    if mode() == MOCK:
        logger.info("Using mock mode - AI disabled")
        return _mock(kind)
    
    # Try remote AI first
    response = _remote(system, user, kind)
    
    if response:
        return response
    
    # Final fallback to mock
    return _mock(kind)


def ask_json(system: str, user: str, kind: str = "") -> Optional[dict]:
    """Execute AI and return parsed JSON response, or None on failure."""
    
    text = complete(system, user, kind)
    if not text:
        return None
        
    # Extract JSON from response (handles markdown code blocks)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
        
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse AI JSON response: {e}")
        return None


def get_ai_status() -> dict:
    """Get AI service status for monitoring/debugging."""
    url = get_base_url()
    is_healthy = _AI_HEALTH_CHECK_CACHE.get(url, False)
    
    return {
        "mode": mode(),
        "configured": configured(),
        "health": "healthy" if is_healthy else "unhealthy/unreachable",
        "endpoints_used": url,
        "using_remote": mode() == REMOTE,
        "using_mock": mode() == MOCK,
    }


if __name__ == "__main__":
    # Test AI configuration
    print("=" * 60)
    print("MauEkspor AI Service Status")
    print("=" * 60)
    status = get_ai_status()
    for k, v in status.items():
        print(f"{k:20s}: {v}")
    print("=" * 60)
    
    # Test chat completion
    test_response = complete(
        "You are a helpful assistant.",
        "Hello, how are you?",
        "test"
    )
    print("\nTest Chat Response:")
    print(test_response[:200] if test_response else "NO RESPONSE")
