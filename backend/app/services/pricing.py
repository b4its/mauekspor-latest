"""Layanan keuangan: exchange rate, kalkulasi EXW/FOB/CIF, optimasi kontainer, PDF costing.

Diadaptasi dari `apps/costings/services.py` + `pdf_service.py` ExportReadyAI.
"""

from __future__ import annotations

import io
import math
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app import db, ai
from app.core.config import settings

# Currency defaults dari config (base = IDR, display = IDR/USD/EUR/dll)
BASE_CURRENCY = settings.base_currency  # mata uang input biaya
DISPLAY_CURRENCY = settings.display_currency  # mata uang output harga
FALLBACK_RATE = settings.fallback_rate
RATE_STALE_HOURS = 24


# ---------------------------------------------------------------------------
# Exchange rate
# ---------------------------------------------------------------------------
def get_exchange_rate() -> dict[str, Any]:
    """Rate base→display terbaru; auto-fetch bila basi >24 jam; fallback."""
    rates = db.all("exchange_rates")
    record = rates[0] if rates else None
    now = datetime.now(timezone.utc)
    stale = True
    if record:
        try:
            updated = datetime.fromisoformat(str(record.get("updatedAt", "")).replace("Z", "+00:00"))
            stale = (now - updated) > timedelta(hours=RATE_STALE_HOURS)
        except Exception:
            stale = True
        # Treat currency pair mismatch as stale
        if record.get("baseCurrency") != BASE_CURRENCY or record.get("targetCurrency") != DISPLAY_CURRENCY:
            stale = True
    if record and not stale:
        return record
    rate = fetch_live_exchange_rate()
    if rate is None:
        rate = FALLBACK_RATE
        source = "fallback"
    else:
        source = "auto_fetched"
    if record:
        record.update({"rate": rate, "source": source, "updatedAt": now.isoformat(),
                       "baseCurrency": BASE_CURRENCY, "targetCurrency": DISPLAY_CURRENCY})
        db.save(record)
    else:
        record = db.insert("exchange_rates", {
            "id": db.gen_id("exchange_rates", "FX"),
            "rate": rate, "source": source, "updatedAt": now.isoformat(),
            "baseCurrency": BASE_CURRENCY, "targetCurrency": DISPLAY_CURRENCY,
        })
    return record


def fetch_live_exchange_rate() -> float | None:
    """Fetch live rate dari exchangerate-api (base→display)."""
    if BASE_CURRENCY == DISPLAY_CURRENCY:
        return 1.0
    try:
        resp = httpx.get(f"https://api.exchangerate-api.com/v4/latest/{BASE_CURRENCY}", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        target = data.get("rates", {}).get(DISPLAY_CURRENCY)
        return float(target) if target else None
    except Exception:
        return None


def set_exchange_rate(rate: float, source: str = "manual") -> dict[str, Any]:
    rates = db.all("exchange_rates")
    record = rates[0] if rates else None
    now = datetime.now(timezone.utc).isoformat()
    if record:
        record.update({"rate": rate, "source": source, "updatedAt": now,
                       "baseCurrency": BASE_CURRENCY, "targetCurrency": DISPLAY_CURRENCY})
        db.save(record)
    else:
        record = db.insert("exchange_rates", {
            "id": db.gen_id("exchange_rates", "FX"), "rate": rate, "source": source, "updatedAt": now,
            "baseCurrency": BASE_CURRENCY, "targetCurrency": DISPLAY_CURRENCY,
        })
    return record


# ---------------------------------------------------------------------------
# Kalkulasi harga EXW / FOB / CIF
# ---------------------------------------------------------------------------
# Tarif truk per km (USD) per jarak (referensi ExportReadyAI) — dikonversi ke display currency
_TRUCKING_BANDS = [(50, 0.50), (200, 0.40), (500, 0.30), (10_000, 0.25)]
_DOCUMENT_COST = 50.0  # USD
_INSURANCE_PERCENT = 0.005  # 0.5%

# Freight % dari FOB per region
_FREIGHT_PERCENT = {
    "Asia": 0.08,
    "Oceania": 0.10,
    "Europe": 0.14,
    "North America": 0.16,
    "South America": 0.18,
    "Middle East": 0.12,
    "Africa": 0.20,
}


def _trucking_cost(distance_km: float) -> float:
    """Trucking cost in USD (base currency for logistics costs)."""
    for band_km, per_km in _TRUCKING_BANDS:
        if distance_km <= band_km:
            return distance_km * per_km
    return distance_km * _TRUCKING_BANDS[-1][1]


def calculate_exw(cogs_idr: float, packing_cost_idr: float, margin_percent: float, rate: float) -> float:
    """Calculate EXW price in display currency.

    Args:
        cogs_idr: Cost of goods sold in base currency (IDR)
        packing_cost_idr: Packing cost in base currency (IDR)
        margin_percent: Target margin percentage (0-100)
        rate: Exchange rate (base → display). Must be > 0.

    Raises:
        ValueError: If rate is zero or negative (would cause division by zero)
    """
    if not rate or rate <= 0:
        raise ValueError(f"Exchange rate must be positive, got: {rate!r}")
    total_idr = (cogs_idr + packing_cost_idr) * (1 + margin_percent / 100.0)
    return round(total_idr / rate, 2)


def calculate_fob(exw: float, distance_km: float, rate: float) -> float:
    trucking = _trucking_cost(distance_km)
    return round(exw + trucking + _DOCUMENT_COST, 2)


def calculate_cif(fob: float, region: str) -> float:
    freight = fob * _FREIGHT_PERCENT.get(region, 0.12)
    insurance = (fob + freight) * _INSURANCE_PERCENT
    return round(fob + freight + insurance, 2)


# Biaya lokal di negara tujuan utk DAP (handling, transport darat, dst) — % dari CIF
_DAP_LOCAL_PERCENT = {
    "Asia": 0.04,
    "Oceania": 0.05,
    "Europe": 0.06,
    "North America": 0.06,
    "South America": 0.07,
    "Middle East": 0.05,
    "Africa": 0.08,
}


def calculate_dap(cif: float, region: str) -> float:
    """DAP (Delivered At Place): CIF + biaya lokal tujuan (handling & on-carriage).

    DAP TIDAK termasuk bea masuk & pajak impor (itu DDP) — sesuai Incoterms 2020.
    """
    return round(cif * (1 + _DAP_LOCAL_PERCENT.get(region, 0.05)), 2)


# ---------------------------------------------------------------------------
# Optimasi kontainer
# ---------------------------------------------------------------------------
CONTAINER_20FT = {"length": 5.9, "width": 2.35, "height": 2.39, "volume": 33.2, "weight_limit_kg": 17_500}
CONTAINER_40FT_MULTIPLIER = 2.1


def container_capacity(product_volume_m3: float, product_weight_kg: float) -> dict[str, Any]:
    """Perkiraan kapasitas kontainer 20ft (dan 40ft = 2.1x)."""
    vol_util = CONTAINER_20FT["volume"] * 0.85
    by_volume = int(vol_util / product_volume_m3) if product_volume_m3 > 0 else 0
    by_weight = int(CONTAINER_20FT["weight_limit_kg"] / product_weight_kg) if product_weight_kg > 0 else 0
    capacity = max(min(by_volume, by_weight), 0)
    tips: list[str] = []
    if product_volume_m3 <= 0:
        tips.append("Lengkapi dimensi produk untuk estimasi kapasitas kontainer.")
    elif by_weight < by_volume:
        tips.append("Kontainer dibatasi bobot; pertimbangkan palletisasi untuk stabilitas.")
    else:
        tips.append("Dimensi efisien untuk pemanfaatan volume kontainer.")
    return {
        "capacity_20ft": capacity,
        "capacity_40ft": capacity * CONTAINER_40FT_MULTIPLIER,
        "utilization_note": f"{by_volume} by volume vs {by_weight} by weight",
        "tips": tips,
    }


def calculate_container_capacity_from_dimensions(
    length_cm: float, width_cm: float, height_cm: float, weight_per_unit_kg: float | None = None
) -> dict[str, Any]:
    """Kapasitas kontainer 20ft dari dimensi produk (L×W×H cm).

    Diadaptasi dari ContainerOptimizerService ExportReadyAI (PBI-BE-M4-09):
    estimasi 3D bin packing sederhana dengan utilisasi ruang 85% + batas bobot
    kontainer 20ft (17.500 kg), plus catatan/tips optimasi.
    """
    try:
        length_cm = float(length_cm or 0)
        width_cm = float(width_cm or 0)
        height_cm = float(height_cm or 0)
    except (TypeError, ValueError):
        length_cm = width_cm = height_cm = 0

    volume_cm3 = length_cm * width_cm * height_cm
    if volume_cm3 <= 0:
        return {
            "capacity_20ft": 0,
            "capacity_40ft": 0,
            "utilization_note": "Lengkapi dimensi produk (L×W×H) untuk estimasi kapasitas kontainer.",
            "tips": ["Lengkapi dimensi produk (L×W×H) untuk estimasi kapasitas kontainer."],
        }

    # 20ft container internal: 5.90 × 2.35 × 2.39 m (dalam cm)
    container_volume_cm3 = 590 * 235 * 239
    capacity = int(container_volume_cm3 * 0.85 / volume_cm3)

    notes = ""
    if weight_per_unit_kg:
        try:
            weight = float(weight_per_unit_kg)
        except (TypeError, ValueError):
            weight = 0
        if weight > 0:
            weight_capacity = int(17500 / weight)
            if weight_capacity < capacity:
                capacity = weight_capacity
                notes = f"Dibatasi bobot: maks {capacity} unit ({weight} kg/unit)"

    if capacity < 500:
        notes += (" | " if notes else "") + "Tip: kurangi tinggi produk 1-2cm untuk +50-100 unit"
    elif capacity < 1000:
        notes += (" | " if notes else "") + "Tip: optimalkan pola susun untuk utilisasi maksimal"

    return {
        "capacity_20ft": capacity,
        "capacity_40ft": round(capacity * 2.1),
        "utilization_note": notes or "Efisiensi pengepakan baik",
        "tips": [notes] if notes else ["Dimensi efisien untuk pemanfaatan volume kontainer."],
    }


def ai_container_optimization(
    product_name: str,
    dimensions_lwh: dict | None,
    capacity: int,
    weight_per_unit: float | None = None,
) -> str:
    """Saran optimasi kontainer berbasis AI (2-3 tips praktis).

    Diadaptasi dari ContainerOptimizerService.get_ai_container_optimization
    ExportReadyAI. Mengembalikan string kosong bila AI tak tersedia.
    """
    if not product_name:
        return ""
    dims = dimensions_lwh or {}
    l = dims.get("l") or dims.get("length") or 0
    w = dims.get("w") or dims.get("width") or 0
    h = dims.get("h") or dims.get("height") or 0
    weight_info = f", berat {weight_per_unit} kg/unit" if weight_per_unit else ""
    user = (
        "PRODUK: " + str(product_name) + "\n"
        "DIMENSI: " + str(l) + "cm × " + str(w) + "cm × " + str(h) + "cm" + str(weight_info) + "\n"
        "KAPASITAS KALKULASI: " + str(capacity) + " units per 20ft container\n\n"
        "Berikan 2-3 saran PRAKTIS untuk:\n"
        "1. Optimasi packaging (cara lipat/susun yang lebih efisien)\n"
        "2. Peningkatan kapasitas (perubahan dimensi atau material)\n"
        "3. Cost saving opportunities (bulk packaging, pallet configuration)"
    )
    text = ai.complete(
        "Kamu adalah konsultan packaging & logistik ekspor untuk UMKM. "
        "Expertise: container optimization, packaging efficiency, freight cost reduction. "
        "Berikan saran realistis yang mudah diimplementasikan.",
        user,
        kind="container_optimization",
    )
    return (text or "").strip()


# ---------------------------------------------------------------------------
# Full costing
# ---------------------------------------------------------------------------
def calculate_full_costing(
    cogs_idr: float,
    packing_cost_idr: float,
    margin_percent: float,
    destination: str,
    distance_km: float = 200,
    product_volume_m3: float = 0,
    product_weight_kg: float = 0,
) -> dict[str, Any]:
    from app.data.countries import region_of

    fx = get_exchange_rate()
    rate = float(fx.get("rate", FALLBACK_RATE))
    if not rate or rate <= 0:
        rate = float(FALLBACK_RATE) if FALLBACK_RATE and FALLBACK_RATE > 0 else 1.0
    exw = calculate_exw(cogs_idr, packing_cost_idr, margin_percent, rate)
    fob = calculate_fob(exw, distance_km, rate)
    region = region_of(destination)
    cif = calculate_cif(fob, region)
    dap = calculate_dap(cif, region)
    container = container_capacity(product_volume_m3, product_weight_kg)
    return {
        "exchangeRate": rate,
        "exchangeSource": fx.get("source", "fallback"),
        "baseCurrency": BASE_CURRENCY,
        "displayCurrency": DISPLAY_CURRENCY,
        "currency": DISPLAY_CURRENCY,
        "exwPrice": exw,
        "fobPrice": fob,
        "cifPrice": cif,
        "dapPrice": dap,
        "region": region,
        "container": container,
        "lines": [
            {"category": "Production", "label": "COGS", "amount": round(cogs_idr / rate, 2)},
            {"category": "Production", "label": "Packing cost", "amount": round(packing_cost_idr / rate, 2)},
            {"category": "Margin", "label": f"Target margin {margin_percent}%", "amount": round(exw - (cogs_idr + packing_cost_idr) / rate, 2)},
            {"category": "Local logistics", "label": "Trucking to port", "amount": round(fob - exw - _DOCUMENT_COST, 2)},
            {"category": "Documents", "label": "Documentation fee", "amount": _DOCUMENT_COST},
            {"category": "Freight", "label": f"Ocean freight ({region})", "amount": round(cif - fob - (fob + (cif - fob - fob * _INSURANCE_PERCENT) / (1 + _INSURANCE_PERCENT)) * _INSURANCE_PERCENT, 2)},
            {"category": "Insurance", "label": "Cargo insurance 0.5%", "amount": round((fob + (cif - fob) * 0.9) * _INSURANCE_PERCENT, 2)},
            {"category": "Destination local", "label": f"DAP on-carriage ({region})", "amount": round(dap - cif, 2)},
        ],
    }


# ---------------------------------------------------------------------------
# PDF costing report
# ---------------------------------------------------------------------------
def build_costing_pdf(costing: dict[str, Any]) -> bytes:
    """Buat PDF sederhana (tanpa ReportLab) — plain PDF A4 dengan tabel biaya.

    Menghindari dependency tambahan; output tetap valid `application/pdf`.
    """
    lines = costing.get("lines", [])
    rows = "\n".join(
        f"{line.get('category', '')} - {line.get('label', '')}: {line.get('amount', 0)}" for line in lines
    )
    total = sum(float(line.get("amount", 0)) for line in lines)
    text = "\n".join([
        "MAUEKSPOR - COSTING REPORT",
        "=" * 60,
        f"Title       : {costing.get('title', '')}",
        f"Destination : {costing.get('destination', '')}",
        f"Incoterm    : {costing.get('incoterm', '')}",
        f"Margin      : {costing.get('margin', 0)}%",
        f"Exchange    : {costing.get('exchangeRate', '')}",
        "",
        "COST BREAKDOWN",
        "-" * 60,
        rows,
        "-" * 60,
        f"TOTAL       : {total:.2f}",
        "",
        f"EXW : {costing.get('exwPrice', 0)}",
        f"FOB : {costing.get('fobPrice', 0)}",
        f"CIF : {costing.get('cifPrice', 0)}",
        f"Landed : {costing.get('landedCost', 0)}",
        "",
        "Risks:",
        *[f"- {r}" for r in costing.get("risks", [])],
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
    ])
    content = text.encode("utf-8", errors="replace")
    return _wrap_pdf(content)


def _wrap_pdf(text_bytes: bytes) -> bytes:
    # Minimal valid PDF writer (no external deps)
    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    stream = text_bytes
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
    )
    objects.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    )
    return bytes(out)


def build_analysis_pdf(analysis: dict[str, Any]) -> bytes:
    """Buat PDF ringkasan export analysis (mirip build_costing_pdf)."""
    issues = analysis.get("complianceIssues") or []
    issue_lines = []
    for issue in issues:
        issue_lines.append(
            f"- [{issue.get('severity', 'minor')}] {issue.get('type', '')}: "
            f"{issue.get('required_value', '')}"
        )
    if not issue_lines:
        issue_lines.append("- Tidak ada isu kepatuhan ditemukan.")
    recommendations = analysis.get("recommendations") or ""
    if isinstance(recommendations, list):
        recommendations = "\n".join(f"- {r}" for r in recommendations)
    text = "\n".join([
        "MAUEKSPOR - EXPORT ANALYSIS REPORT",
        "=" * 60,
        f"Product     : {analysis.get('productName', '')}",
        f"Destination : {analysis.get('destination', '')}",
        f"HS Code     : {analysis.get('hsCode', '')}",
        f"Status      : {analysis.get('status', '')}",
        f"Score       : {analysis.get('score', 0)} / 100",
        f"Grade       : {analysis.get('statusGrade', '-')}",
        f"Confidence  : {analysis.get('confidence', 0)}%",
        "",
        "COMPLIANCE ISSUES",
        "-" * 60,
        *issue_lines,
        "",
        "RECOMMENDATIONS",
        "-" * 60,
        str(recommendations),
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
    ])
    return _wrap_pdf(text.encode("utf-8", errors="replace"))


def build_compare_pdf(product: dict[str, Any], results: list[dict[str, Any]]) -> bytes:
    """PDF perbandingan export analysis antar negara (urutan skor tertinggi dulu)."""
    lines: list[str] = [
        "MAUEKSPOR - EXPORT ANALYSIS COMPARISON",
        "=" * 60,
        f"Product : {product.get('name', '')}",
        f"HS Code : {product.get('hs', 'TBD')}",
        "",
    ]
    for idx, r in enumerate(results, start=1):
        lines.append(f"{idx}. {r.get('country', '')} - Score {r.get('score', 0)} ({r.get('grade', '-')})")
        lines.append("   Critical issues : %d" % r.get("critical_issues", 0))
        rec = r.get("recommendation") or ""
        lines.append("   Rekomendasi    : %s" % (rec[:180] + ("..." if len(rec) > 180 else "")))
        lines.append("")
    best = results[0] if results else None
    if best:
        lines += [
            "=" * 60,
            f"BEST OPTION : {best.get('country', '')}",
            f"Score       : {best.get('score', 0)} / 100",
            f"Grade       : {best.get('grade', '-')}",
        ]
    lines += ["", f"Generated: {datetime.now(timezone.utc).isoformat()}"]
    return _wrap_pdf("\n".join(lines).encode("utf-8", errors="replace"))
