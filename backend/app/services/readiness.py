"""Scoring kesiapan ekspor yang dihitung dari data profil, bukan input manual.

Dua skor utama:
- `product_readiness`: kelengkapan master data produk (dipakai di modul produk).
- `profile_readiness`: kelengkapan profil bisnis/desa (nama, alamat, kapasitas,
  tahun berdiri, pemilik, status, dan sertifikasi berbukti).

Kesiapan desa **selalu diturunkan** dari profil bisnis yang tertaut (BUMDes /
koperasi) supaya angka di UI konsisten dengan data yang benar-benar dimiliki
entitas tersebut. Tidak ada lagi `readiness` yang diisi manual di form desa.
"""
from __future__ import annotations

from typing import Any

# Sertifikasi yang dianggap "berbukti" bila tercatat di profil bisnis/desa.
PROFILE_CERTIFICATIONS: tuple[str, ...] = (
    "Halal", "ISO 22000", "ISO 9001", "HACCP", "SVLK", "Organic",
    "Origin declaration", "GAP", "GlobalGAP", "BPOM", "SNI",
)

_BASE = 20
_NAME_ADDRESS = 20
_CAPACITY = 10
_YEAR = 10
_OWNER = 10
_STATUS = 10
_CERT_MAX = 20


def _text(value: Any) -> str:
    return str(value or "").strip()


def _has(value: Any) -> bool:
    return bool(_text(value))


def profile_readiness(profile: dict[str, Any] | None) -> int:
    """Skor 0-100 dari kelengkapan data profil bisnis."""
    if not profile:
        return 0
    score = _BASE
    if _has(profile.get("companyName")) and _has(profile.get("address")):
        score += _NAME_ADDRESS
    if _has(profile.get("productionCapacity")):
        score += _CAPACITY
    if profile.get("yearEstablished"):
        score += _YEAR
    if _has(profile.get("owner")):
        score += _OWNER
    if _has(profile.get("status")) and _text(profile.get("status")).lower() not in {"draft", ""}:
        score += _STATUS
    # Sertifikasi hanya menambah skor bila ADA BUKTI berkasnya. Klaim tanpa
    # dokumen/gambar tidak dipercaya (klaim kosong tidak mengangkat kesiapan).
    certified = evidenced_certification_count(profile)
    if certified:
        score += min(certified * 5, _CERT_MAX)
    return max(0, min(100, score))


def evidenced_certification_count(profile: dict[str, Any] | None) -> int:
    """Jumlah sertifikasi yang punya bukti berkas nyata.

    - Bentuk baru: `certificationItems` dengan `verified` True / ada `evidenceFileId`.
    - Bentuk lama: `certifications` dianggap **tanpa bukti** (0), agar tidak ada
      klaim terhitung tanpa dokumen.
    """
    if not profile:
        return 0
    items = profile.get("certificationItems")
    if isinstance(items, list) and items:
        return sum(
            1 for i in items
            if isinstance(i, dict) and (i.get("verified") or i.get("evidenceFileId"))
        )
    return 0


def product_readiness(product: dict[str, Any] | None) -> int:
    """Skor 0-100 dari kelengkapan master data produk."""
    if not product:
        return 0
    score = _BASE
    name = _text(product.get("name"))
    category = _text(product.get("category"))
    if name and category:
        score += 15
    if product.get("description") or product.get("quality_specs") or product.get("material_composition"):
        score += 10
    if _has(product.get("packaging")):
        score += 10
    if product.get("netWeight") or product.get("weight_net"):
        score += 5
    if product.get("grossWeight") or product.get("weight_gross"):
        score += 5
    if _has(product.get("moq")) or product.get("min_order_quantity"):
        score += 5
    if _has(product.get("leadTime")) or product.get("lead_time_days"):
        score += 5
    certs = product.get("certificates")
    if isinstance(certs, list) and certs:
        score += min(len(certs) * 5, 15)
    if product.get("status") == "Enriched" and product.get("hs") not in (None, "", "TBD"):
        score += 10
    return max(0, min(100, score))


def village_status(readiness: int) -> str:
    return "Siap Ekspor" if int(readiness or 0) >= 80 else "Butuh Pendampingan"


def business_profile_for_village(village: dict[str, Any], profiles: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
    """Cari profil bisnis pengelola desa.

    Prioritas: `businessProfileId` eksplisit → kecocokan nama organization →
    kecocokan address yang memuat nama desa.
    """
    if not village:
        return None
    profiles = profiles if profiles is not None else []
    explicit = _text(village.get("businessProfileId"))
    if explicit:
        for profile in profiles:
            if _text(profile.get("id")) == explicit:
                return profile
    org = _text(village.get("organization")).lower()
    if org:
        for profile in profiles:
            if _text(profile.get("companyName")).lower() == org:
                return profile
    name = _text(village.get("name")).lower()
    if name:
        for profile in profiles:
            if name and name in _text(profile.get("address")).lower():
                return profile
    return None


def with_village_readiness(
    village: dict[str, Any],
    profiles: list[dict[str, Any]] | None = None,
    computed_at: str = "",
) -> dict[str, Any]:
    """Kembalikan salinan village dengan `readiness`/`status` hasil hitung profil.

    Bila profil pengelola belum ada, desa dianggap belum punya data kesiapan
    (0 / "Butuh Pendampingan") dan ditandai `readinessSource="unlinked"` supaya
    UI bisa meminta pengguna melengkapi profil bisnis alih-alih mengisi angka.
    """
    out = dict(village)
    profile = business_profile_for_village(village, profiles)
    if profile is None:
        out["readiness"] = 0
        out["status"] = village_status(0)
        out["readinessSource"] = "unlinked"
        out["businessProfile"] = None
    else:
        readiness = profile_readiness(profile)
        out["readiness"] = readiness
        out["status"] = village_status(readiness)
        out["readinessSource"] = "profile"
        out["businessProfile"] = {
            "id": profile.get("id"),
            "companyName": profile.get("companyName", ""),
            "status": profile.get("status", ""),
            "certifications": profile.get("certifications", []),
        }
    if computed_at:
        out["readinessComputedAt"] = computed_at
    return out
