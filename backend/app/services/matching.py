"""Layanan matching buyer request -> katalog UMKM (adapted dari `buyer_requests/services.py`).

Strategi default: kategori produk (seperti `_match_category_only` di referensi).
Strategi lanjutan (digunakan untuk skor akhir bila data tersedia):
- kecocokan HS code (exact/6-digit)
- kecocokan spesifikasi (keyword overlap)
- kapabilitas (sertifikasi + export analysis)
- volume & bonus buyer.
"""

from __future__ import annotations

import re
from typing import Any

from app import db, ai

# Pemetaan nama kategori -> id (konsisten dengan seed/UI)
CATEGORY_IDS = {
    "makanan olahan": 1,
    "food & beverage": 1,
    "processed food": 1,
    "kerajinan": 2,
    "craft": 2,
    "furniture & craft": 2,
    "furniture": 2,
    "tekstil": 3,
    "textile": 3,
    "furniture/mebel": 4,
}


def _category_id(name: str) -> int:
    return CATEGORY_IDS.get((name or "").strip().lower(), 0)


def _extract_keywords(text: str, max_words: int = 20) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text or "")
    stop = {"the", "and", "for", "with", "dari", "yang", "untuk", "dengan", "dan"}
    return [w.lower() for w in words if w.lower() not in stop][:max_words]


def _catalog_text(catalog: dict, product: dict | None) -> str:
    parts = [
        catalog.get("title", ""),
        catalog.get("description", ""),
        str(catalog.get("specifications", "")),
        " ".join(catalog.get("tags", []) or []),
    ]
    if product:
        parts.extend([product.get("name", ""), product.get("description", "")])
    return " ".join(parts).lower()


def match_buyer_request(request: dict) -> list[dict]:
    """Kembalikan daftar katalog yang cocok untuk satu buyer request.

    Strategi utama: kategori produk dari `product_category` / `requirements` /
    `subject` request dibandingkan dengan katalog yang statusnya `Published`.
    Skor akhir menggabungkan: kategori (35%), HS code (30%), spesifikasi (25%),
    kapabilitas (5%), volume (5%).
    """
    catalogs = [c for c in db.all("catalogs") if str(c.get("status", "")).lower() in {"published", "published"}]
    # Fallback: katalog dengan status apa pun bila tidak ada yang published
    if not catalogs:
        catalogs = db.all("catalogs")

    category_text = " ".join([
        request.get("product_category", ""),
        request.get("subject", ""),
        " ".join(request.get("requirements", []) or []),
    ])
    req_category_id = _category_id(category_text)
    hs_target = str(request.get("hs_code_target") or "").strip() or str(request.get("hsCode") or "").strip()
    req_keywords = _extract_keywords(
        " ".join([request.get("spec_requirements", ""), request.get("subject", ""), category_text])
    )
    try:
        target_volume = float(request.get("target_volume") or 0)
    except (TypeError, ValueError):
        target_volume = 0.0
    if not target_volume:
        qty = request.get("quantity") or request.get("targetVolume") or 0
        try:
            target_volume = float(str(qty).replace(",", "").replace(".", "")) if isinstance(qty, str) and qty.replace(",", "").replace(".", "").isdigit() else float(qty or 0)
        except (TypeError, ValueError):
            target_volume = 0.0

    matches: list[dict] = []
    for catalog in catalogs:
        product = db.get("products", str(catalog.get("productId", ""))) if catalog.get("productId") else None
        cat_score = _category_match(req_category_id, catalog, product)
        if cat_score <= 0:
            continue
        hs_score = _hs_match(hs_target, product, catalog)
        spec_score = _spec_match(req_keywords, catalog, product)
        cap_score = _capability_match(catalog, product, request)
        vol_score = _volume_match(target_volume, catalog, product)
        final = round(
            cat_score * 0.35 + hs_score * 0.30 + spec_score * 0.25 + cap_score * 0.05 + vol_score * 0.05
        )
        reasons: list[str] = []
        if cat_score >= 100:
            reasons.append("Kategori produk cocok")
        if hs_score >= 100:
            reasons.append("HS code cocok")
        elif hs_score >= 75:
            reasons.append("HS code 6-digit cocok")
        if spec_score >= 60:
            reasons.append("Spesifikasi mendukung")
        if cap_score >= 80:
            reasons.append("Kapabilitas terverifikasi")
        if vol_score >= 60:
            reasons.append("Volume sesuai")
        matches.append({
            "catalog": catalog,
            "catalogId": catalog.get("id"),
            "productId": catalog.get("productId"),
            "product": product.get("name") if product else catalog.get("title"),
            "match_score": final,
            "match_reasons": reasons,
            "umkm_id": catalog.get("owner", ""),
            "umkm_name": catalog.get("owner", ""),
        })
    matches.sort(key=lambda m: m["match_score"], reverse=True)
    return matches


def _category_match(req_category_id: int, catalog: dict, product: dict | None) -> float:
    if req_category_id <= 0:
        return 50
    cat_name = (catalog.get("category") or (product or {}).get("category") or "").lower()
    cat_id = _category_id(cat_name)
    if cat_id == req_category_id:
        return 100
    return 25


def _hs_match(hs_target: str, product: dict | None, catalog: dict) -> float:
    if not hs_target:
        return 50
    prod_hs = str((product or {}).get("hs") or catalog.get("hs") or "").replace(".", "")
    target = str(hs_target).replace(".", "")
    if prod_hs == target:
        return 100
    if prod_hs[:6] == target[:6] and len(prod_hs) >= 6:
        return 75
    return 25


def _spec_match(req_keywords: list[str], catalog: dict, product: dict | None) -> float:
    if not req_keywords:
        return 50
    text = _catalog_text(catalog, product)
    hits = sum(1 for k in req_keywords if k in text)
    ratio = hits / len(req_keywords)
    if ratio >= 0.5:
        return 100
    if ratio >= 0.25:
        return 70
    return 40 if ratio > 0 else 25


def _capability_match(catalog: dict, product: dict | None, request: dict) -> float:
    certs = (product or {}).get("certificates", []) or []
    score = min(len(certs) * 10, 20)
    if (product or {}).get("readiness", 0) >= 80:
        score += 30
    if (product or {}).get("status") == "Enriched":
        score += 20
    analyses = db.find("export_analyses", productId=str((product or {}).get("id", "")))
    if analyses:
        score += 20
    return min(score, 100)


def _volume_match(target_volume: float, catalog: dict, product: dict | None) -> float:
    if target_volume <= 0:
        return 50
    stock = float((catalog or {}).get("availableStock") or (product or {}).get("stock") or 0)
    if stock <= 0:
        return 40
    if stock >= target_volume:
        return 100
    return 60 if stock >= target_volume * 0.5 else 30
