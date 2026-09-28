"""Validasi & penyimpanan unggahan yang aman (PRD §6 NFR-SEC-2 / G-16).

Sebelumnya unggahan hanya divalidasi berdasarkan ekstensi (bisa dipalsukan) dan
nama berkas disimpan memakai timestamp milidetik + nama asli (bisa bertabrakan
dalam satu milidetik → saling menimpa). Modul ini:

- memvalidasi magic bytes (signature) sehingga ekstensi harus cocok isi;
- membatasi ekstensi yang diizinkan;
- memakai nama penyimpanan acak (UUID) agar tidak pernah bertabrakan.
"""

from __future__ import annotations

import os
import uuid

# Ekstensi yang diizinkan (dokumen, gambar, arsip).
ALLOWED_EXTENSIONS: set[str] = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".doc", ".docx", ".xls", ".xlsx", ".csv", ".txt",
    ".zip", ".rar",
}

# Peta signature (prefix) → ekstensi yang sah untuknya. Ekstensi tanpa signature
# tegas (mis. .csv/.txt) tidak diperiksa isinya.
_SIGNATURES: dict[bytes, set[str]] = {
    b"%PDF-": {".pdf"},
    b"\x89PNG\r\n\x1a\n": {".png"},
    b"\xff\xd8\xff": {".jpg", ".jpeg"},
    b"GIF87a": {".gif"},
    b"GIF89a": {".gif"},
    b"PK\x03\x04": {".docx", ".xlsx", ".zip"},  # OOXML & zip
    b"Rar!\x1a\x07": {".rar"},
    b"RIFF": {".webp"},  # WebP = RIFF....WEBP (diperiksa lanjutan)
}

# Ekstensi yang TIDAK diperiksa isi (teks/plain, legacy OLE .doc/.xls).
_TEXT_OR_LEGACY = {".csv", ".txt", ".doc", ".xls"}


def safe_extension(filename: str) -> str:
    return os.path.splitext(os.path.basename(filename or ""))[1].lower()


def validate_upload(filename: str, content: bytes) -> str:
    """Kembalikan ekstensi tervalidasi atau raise ValueError.

    Memeriksa ekstensi ada di allowlist DAN (bila signature diketahui) isi file
    cocok dengan ekstensi tersebut.
    """
    ext = safe_extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Tipe file '{ext or 'tanpa ekstensi'}' tidak diizinkan. "
            f"Tipe yang diperbolehkan: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    if ext in _TEXT_OR_LEGACY or not content:
        return ext
    # Periksa magic bytes untuk ekstensi yang punya signature tegas.
    for signature, allowed in _SIGNATURES.items():
        if content.startswith(signature):
            if ext in allowed:
                # WebP: RIFF????WEBP
                if signature == b"RIFF" and (len(content) < 12 or content[8:12] != b"WEBP"):
                    raise ValueError("Isi file bukan WebP yang valid.")
                return ext
            raise ValueError(f"Isi file tidak cocok dengan ekstensi '{ext}'.")
    # Tidak ada signature yang cocok untuk ekstensi bergambar/dokumen tegas.
    if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".rar", ".docx", ".xlsx"}:
        raise ValueError(f"Isi file tidak dikenali sebagai '{ext}' yang valid.")
    return ext


def stored_filename(filename: str) -> str:
    """Nama penyimpanan acak (UUID) yang mempertahankan ekstensi aman."""
    ext = safe_extension(filename)
    return f"{uuid.uuid4().hex}{ext}"
