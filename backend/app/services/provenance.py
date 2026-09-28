"""Provenance & trust metadata untuk keluaran analisis (AI, regulasi, dokumen).

PRD §5.4 / §5.12: setiap rekomendasi regulasi dan keluaran AI wajib menyimpan
asal-usul (sumber, penerbit, tanggal berlaku, status review) dan menandai jelas
apakah hasil berasal dari AI nyata, template deterministik, atau fallback mock —
sehingga UI tidak pernah menyajikan data mock seolah analisis produksi.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app import ai

# Status review yang diizinkan untuk sebuah rekomendasi/sumber.
REVIEW_DRAFT = "Draft"
REVIEW_REVIEWED = "Reviewed"
REVIEW_DEPRECATED = "Deprecated"

# Sumber default bila tidak ada URL spesifik (selalu ditandai perlu verifikasi).
DEFAULT_SOURCE = {
    "publisher": "Perlu verifikasi",
    "url": "https://peraturan.bpk.go.id/",
    "note": "Lengkapi dengan dokumen resmi sebelum dipakai sebagai nasihat kepatuhan.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def source_block(
    *,
    publisher: str = "",
    url: str = "",
    effective_from: str = "",
    effective_to: str = "",
    jurisdiction: str = "",
    review_status: str = REVIEW_DRAFT,
) -> dict:
    """Bentuk satu blok sumber dengan field provenance yang konsisten."""
    return {
        "publisher": publisher or DEFAULT_SOURCE["publisher"],
        "url": url or DEFAULT_SOURCE["url"],
        "effectiveFrom": effective_from,
        "effectiveTo": effective_to,
        "jurisdiction": jurisdiction,
        "reviewStatus": review_status,
        "retrievedAt": _now_iso(),
    }


def ai_provenance(*, fallback: bool = False, note: str = "") -> dict:
    """Metadata provenance untuk keluaran AI.

    `fallback=True` menandai bahwa hasil berasal dari template/fallback
    deterministik, bukan model AI nyata — UI harus menampilkan ini sebagai
    *saran*, bukan analisis teknologi AI produksi.
    """
    mode = ai.mode()
    is_mock = (not ai.configured()) or mode == ai.MOCK
    return {
        "provider": "mock" if is_mock else mode,
        "model": "" if is_mock else ai.model_name(),
        "fallback": bool(fallback or is_mock),
        "advisory": True,  # semua keluaran AI bersifat saran, bukan keputusan final
        "generatedAt": _now_iso(),
        "note": note
        or (
            "Dihasilkan mode mock/template (bukan AI produksi). Gunakan sebagai saran saja."
            if is_mock
            else "Dihasilkan AI. Wajib ditinjau manusia sebelum keputusan kepatuhan."
        ),
    }


def analysis_trust(ai_sections_used: bool) -> dict:
    """Ringkasan tingkat kepercayaan sebuah analisis untuk ditampilkan di UI."""
    prov = ai_provenance(fallback=not ai_sections_used)
    return {
        "advisory": True,
        "humanReviewRequired": True,
        "ai": prov,
        "disclaimer": (
            "Materi ini bersifat indikatif dan bukan nasihat hukum. "
            "Selalu verifikasi ke sumber resmi (JDIH BPK, Bea Cukai, Barantin, Kemendag, BPOM) "
            "sebelum keputusan ekspor."
        ),
    }
