"""AI service untuk MauEkspor API.

Dua mode:
- "mock" (default): jawaban canned deterministik per jenis tugas,
  dipakai untuk demo dan test tanpa memanggil model nyata.
- "remote": memanggil endpoint OpenAI-compatible /chat/completions
  (`.env` -> MAUEKSPOR_AI_API_KEY, MAUEKSPOR_AI_BASE_URL, MAUEKSPOR_AI_MODEL).

Semua fungsi mengembalikan None bila tidak tersedia, sehingga pemanggil
mampu jatuh-kembali ke behaviour statis lama.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
from dotenv import load_dotenv

# Muat .env ke environment sebelum membaca konfigurasi AI.
# Contekan: nilai di env OS tidak akan ditimpa (override tetap env OS menang).
load_dotenv()

MOCK = "mock"
REMOTE = "remote"

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
TIMEOUT_SECONDS = 60


def mode() -> str:
    return os.environ.get("MAUEKSPOR_AI_MODE", MOCK).strip().lower()


def configured() -> bool:
    if mode() == REMOTE:
        return bool(os.environ.get("MAUEKSPOR_AI_API_KEY", "").strip())
    return True


# ---------------------------------------------------------------------------
# Mock provider (deterministik per jenis tugas)
# ---------------------------------------------------------------------------
_MOCK_OUTPUTS: dict[str, Any] = {
    "classify": {
        "hsCode": "0901.21",
        "confidence": 88,
        "reason": "Klasifikasi dari deskripsi produk berdasarkan HS 2022 (contoh).",
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
            {"type": "Certificate", "title": "Certificate of Origin", "status": "Required", "detail": "Confirm rules-of-origin."},
            {"type": "Document", "title": "Packing list", "status": "Required", "detail": "Match weights against invoice."},
        ],
    },
    "chat_reply": (
        "Berdasarkan data workspace Anda, langkah berikutnya adalah memastikan "
        "bukti label dan dokumen pelaporan sudah lengkap sebelum quote dikirim. "
        "Ada hal lain yang ingin Anda tanya?"
    ),
}


def _mock(kind: str) -> str | None:
    output = _MOCK_OUTPUTS.get(kind)
    if output is None:
        return None
    if isinstance(output, str):
        return output
    return json.dumps(output, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Remote provider (OpenAI-compatible)
# ---------------------------------------------------------------------------
def _remote(system: str, user: str) -> str | None:
    api_key = os.environ.get("MAUEKSPOR_AI_API_KEY", "").strip()
    if not api_key:
        return None
    base_url = os.environ.get("MAUEKSPOR_AI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    model = os.environ.get("MAUEKSPOR_AI_MODEL", DEFAULT_MODEL)
    try:
        response = httpx.post(
            f"{base_url}/chat/completions",
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
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        body = response.json()
        return body["choices"][0]["message"]["content"]
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def complete(system: str, user: str, kind: str = "") -> str | None:
    """Kembalikan teks hasil AI, atau None bila mode remote gagal/tak terkonfigurasi."""
    if mode() == REMOTE:
        return _remote(system, user)
    return _mock(kind)


def ask_json(system: str, user: str, kind: str = "") -> dict | None:
    """Jalankan AI dan kembalikan teks hasil sebagai dict JSON (atau None bila gagal)."""
    text = complete(system, user, kind)
    if not text:
        return None
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None