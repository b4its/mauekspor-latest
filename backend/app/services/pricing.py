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

FALLBACK_RATE = 15800.0
RATE_STALE_HOURS = 24


# ---------------------------------------------------------------------------
# Exchange rate
# ---------------------------------------------------------------------------
def get_exchange_rate() -> dict[str, Any]:
    """Rate IDR/USD terbaru; auto-fetch bila basi >24 jam; fallback 15800."""
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
    if record and not stale:
        return record
    rate = fetch_live_exchange_rate()
    if rate is None:
        rate = FALLBACK_RATE
        source = "fallback"
    else:
        source = "auto_fetched"
    if record:
        record.update({"rate": rate, "source": source, "updatedAt": now.isoformat()})
        db.save(record)
    else:
        record = db.insert("exchange_rates", {
            "id": db.gen_id("exchange_rates", "FX"),
            "rate": rate, "source": source, "updatedAt": now.isoformat(),
        })
    return record


def fetch_live_exchange_rate() -> float | None:
    try:
        resp = httpx.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        idr = data.get("rates", {}).get("IDR")
        return float(idr) if idr else None
    except Exception:
        return None


def set_exchange_rate(rate: float, source: str = "manual") -> dict[str, Any]:
    rates = db.all("exchange_rates")
    record = rates[0] if rates else None
    now = datetime.now(timezone.utc).isoformat()
    if record:
        record.update({"rate": rate, "source": source, "updatedAt": now})
        db.save(record)
    else:
        record = db.insert("exchange_rates", {
            "id": db.gen_id("exchange_rates", "FX"), "rate": rate, "source": source, "updatedAt": now,
        })
    return record


# ---------------------------------------------------------------------------
# Kalkulasi harga EXW / FOB / CIF
# ---------------------------------------------------------------------------
# Tarif truk per km (IDR) per jarak (referensi ExportReadyAI)
_TRUCKING_BANDS = [(50, 0.50), (200, 0.40), (500, 0.30), (10_000, 0.25)]
_DOCUMENT_COST_USD = 50.0
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


def _trucking_cost_usd(distance_km: float, rate: float) -> float:
    for band_km, usd_per_km in _TRUCKING_BANDS:
        if distance_km <= band_km:
            return distance_km * usd_per_km
    return distance_km * _TRUCKING_BANDS[-1][1]


def calculate_exw(cogs_idr: float, packing_cost_idr: float, margin_percent: float, rate: float) -> float:
    total_idr = (cogs_idr + packing_cost_idr) * (1 + margin_percent / 100.0)
    return round(total_idr / rate, 2)


def calculate_fob(exw_usd: float, distance_km: float, rate: float) -> float:
    trucking = _trucking_cost_usd(distance_km, rate)
    return round(exw_usd + trucking + _DOCUMENT_COST_USD, 2)


def calculate_cif(fob_usd: float, region: str) -> float:
    freight = fob_usd * _FREIGHT_PERCENT.get(region, 0.12)
    insurance = (fob_usd + freight) * _INSURANCE_PERCENT
    return round(fob_usd + freight + insurance, 2)


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


# ---------------------------------------------------------------------------
# Rekomendasi AI pricing
# ---------------------------------------------------------------------------
def ai_pricing_recommendation(product_name: str, exw: float, fob: float, cif: float, margin: float) -> dict[str, Any]:
    text = ai.complete(
        "You are an export pricing analyst. Return JSON with keys: recommendation (string), risk_level (Low/Medium/High), "
        "market_position (string), price_adjustment_suggestion (string), competitive_insights (string).",
        f"Product: {product_name}; EXW ${exw}, FOB ${fob}, CIF ${cif}, target margin {margin}%.",
        kind="pricing",
    )
    parsed = ai.ask_json(
        "You are an export pricing analyst. Return JSON with keys recommendation, risk_level, market_position, price_adjustment_suggestion, competitive_insights.",
        f"Product: {product_name}; EXW ${exw}, FOB ${fob}, CIF ${cif}, target margin {margin}%.",
        kind="pricing",
    )
    if parsed and isinstance(parsed, dict):
        return {
            "recommendation": str(parsed.get("recommendation", "Gunakan EXW/FOB/CIF yang dihitung.")),
            "risk_level": str(parsed.get("risk_level", "Medium")),
            "market_position": str(parsed.get("market_position", "Competitive")),
            "price_adjustment_suggestion": str(parsed.get("price_adjustment_suggestion", "Pertahankan margin target.")),
            "competitive_insights": str(parsed.get("competitive_insights", "Pantau kurs dan tarif freight.")),
            "_raw": text or "",
        }
    return {
        "recommendation": "Gunakan EXW/FOB/CIF yang dihitung sebagai patokan penawaran.",
        "risk_level": "Medium",
        "market_position": "Competitive",
        "price_adjustment_suggestion": "Pertahankan margin target dan pantau kurs.",
        "competitive_insights": "Bandingkan dengan rate freight aktual sebelum mengunci quote.",
        "_raw": text or "",
    }


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
    exw = calculate_exw(cogs_idr, packing_cost_idr, margin_percent, rate)
    fob = calculate_fob(exw, distance_km, rate)
    region = region_of(destination)
    cif = calculate_cif(fob, region)
    container = container_capacity(product_volume_m3, product_weight_kg)
    return {
        "exchangeRate": rate,
        "exchangeSource": fx.get("source", "fallback"),
        "exwPrice": exw,
        "fobPrice": fob,
        "cifPrice": cif,
        "region": region,
        "container": container,
        "lines": [
            {"category": "Production", "label": "COGS", "amount": round(cogs_idr / rate, 2)},
            {"category": "Production", "label": "Packing cost", "amount": round(packing_cost_idr / rate, 2)},
            {"category": "Margin", "label": f"Target margin {margin_percent}%", "amount": round(exw - (cogs_idr + packing_cost_idr) / rate, 2)},
            {"category": "Local logistics", "label": "Trucking to port", "amount": round(fob - exw - 50.0, 2)},
            {"category": "Documents", "label": "Documentation fee", "amount": 50.0},
            {"category": "Freight", "label": f"Ocean freight ({region})", "amount": round(cif - fob - (fob + (cif - fob - fob * _INSURANCE_PERCENT) / (1 + _INSURANCE_PERCENT)) * _INSURANCE_PERCENT, 2)},
            {"category": "Insurance", "label": "Cargo insurance 0.5%", "amount": round((fob + (cif - fob) * 0.9) * _INSURANCE_PERCENT, 2)},
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
