"""Layanan AI pasar & katalog: market intelligence, pricing per produk, deskripsi katalog.

Diadaptasi dari `core/services/ai_service.py` + `apps/catalogs/services.py` ExportReadyAI.
"""

from __future__ import annotations

from typing import Any

from app import ai, db
from app.data import countries as country_data
from app.services import pricing as pricing_svc

FOOD_KEYWORDS_ID = [
    "makanan", "pangan", "kopi", "teh", "cokelat", "keripik", "snack", "bumbu", "rempah",
    "sambal", "kripik", "roti", "kue", "manisan", "abon", "terasi", "kecap", "minuman",
    "food", "coffee", "tea", "chocolate", "chips", "snack", "spice", "sauce", "noodle",
    "beverage", "cassava", "bakery", "honey", "sugar",
]


def is_food_product(product: dict) -> bool:
    text = " ".join(str(product.get(k, "")) for k in ("name", "category", "description")).lower()
    return any(kw in text for kw in FOOD_KEYWORDS_ID)


def generate_market_intelligence(product: dict) -> dict[str, Any]:
    """Generate market intelligence untuk satu produk (1-per-produk, disimpan)."""
    name = product.get("name", "")
    cat = product.get("category", "")
    desc = product.get("description", "")
    sys_prompt = (
        "You are an international trade market intelligence analyst for Indonesian exports. "
        "Return a valid JSON object matching this schema:\n"
        "{\n"
        '  "recommended_countries": [{"country": "Japan", "code": "JP", "score": 92, "reason": "...", "market_size": "...", "competition_level": "...", "price_range": "...", "entry_strategy": "..."}],\n'
        '  "countries_to_avoid": [{"country": "...", "code": "...", "reason": "..."}],\n'
        '  "market_trends": ["..."],\n'
        '  "competitive_landscape": "...",\n'
        '  "growth_opportunities": ["..."],\n'
        '  "risks_and_challenges": ["..."],\n'
        '  "overall_recommendation": "..."\n'
        "}\n"
        "Provide 3-5 recommended countries with 2-letter ISO codes."
    )
    user_prompt = f"Analisis intelijen pasar ekspor untuk produk: {name} ({cat} - {desc})."
    parsed = ai.ask_json(sys_prompt, user_prompt, kind="market_insight")

    if parsed and isinstance(parsed, dict):
        raw_recs = (
            parsed.get("recommended_countries")
            or parsed.get("recommendedCountries")
            or parsed.get("target_markets")
            or parsed.get("targetMarkets")
            or []
        )
        recommended = []
        if isinstance(raw_recs, list) and len(raw_recs) > 0:
            from app.services.forwarders import get_recommendations
            for item in raw_recs:
                if isinstance(item, dict):
                    code = str(item.get("code") or item.get("country_code") or item.get("countryCode") or "")[:2].upper()
                    c_name = item.get("country") or item.get("country_name") or item.get("name") or code
                    score = item.get("score") if item.get("score") is not None else 88
                    entry = {
                        "country": c_name,
                        "code": code or "JP",
                        "score": score,
                        "reason": item.get("reason") or item.get("description") or "",
                        "market_size": item.get("market_size") or item.get("marketSize") or "US$1B+",
                        "competition_level": item.get("competition_level") or item.get("competitionLevel") or "Sedang",
                        "price_range": item.get("price_range") or item.get("priceRange") or "Kompetitif",
                        "entry_strategy": item.get("entry_strategy") or item.get("entryStrategy") or "Kemitraan lokal",
                    }
                    if code:
                        entry["forwarders"] = get_recommendations(code)
                    recommended.append(entry)

        if len(recommended) > 0:
            return {
                "productId": product.get("id"),
                "recommendedCountries": recommended,
                "countriesToAvoid": parsed.get("countries_to_avoid") or parsed.get("countriesToAvoid") or [],
                "marketTrends": parsed.get("market_trends") or parsed.get("marketTrends") or [],
                "competitiveLandscape": str(parsed.get("competitive_landscape") or parsed.get("competitiveLandscape") or ""),
                "growthOpportunities": parsed.get("growth_opportunities") or parsed.get("growthOpportunities") or [],
                "risksAndChallenges": parsed.get("risks_and_challenges") or parsed.get("risksAndChallenges") or [],
                "overallRecommendation": str(parsed.get("overall_recommendation") or parsed.get("overallRecommendation") or ""),
                "generatedAt": "now",
            }
    # Fallback deterministik
    return _fallback_market_intelligence(product)


def _fallback_market_intelligence(product: dict) -> dict[str, Any]:
    from app.services.forwarders import get_recommendations
    recs = []
    for code in ["JP", "SG", "US", "DE", "AE"]:
        country = country_data.get_country(code)
        recs.append({
            "country": country["country_name"] if country else code,
            "code": code,
            "score": 78,
            "reason": "Permintaan stabil untuk kategori produk; lakukan validasi regulasi.",
            "market_size": "Menengah - besar",
            "competition_level": "Sedang",
            "price_range": "Kompetitif",
            "entry_strategy": "Mulai dengan trial shipment via forwarder terverifikasi.",
            "forwarders": get_recommendations(code),
        })
    return {
        "productId": product.get("id"),
        "recommendedCountries": recs,
        "countriesToAvoid": [
            {"country": "North Korea", "code": "KP", "reason": "Sanksi perdagangan internasional."},
        ],
        "marketTrends": ["Kenaikan permintaan produk berkualitas & tersertifikasi."],
        "competitiveLandscape": "Banyak pemain lokal; diferensiasi lewat sertifikasi dan cerita asal-usul.",
        "growthOpportunities": ["Pasar specialty & premium", "Kanal e-commerce B2B"],
        "risksAndChallenges": ["Kepatuhan labeling", "Fluktuasi freight"],
        "overallRecommendation": "Fokus pada 1-2 pasar prioritas dengan kepatuhan lengkap.",
        "generatedAt": "now",
    }


# ---------------------------------------------------------------------------
# Pricing per produk (EXW/FOB/CIF + insight AI)
# ---------------------------------------------------------------------------
# Multiplier per unit (diadaptasi dari `catalogs/services.py` ExportReadyAI)
_SHIPPING_MULTIPLIER = {
    "Asia": 1.12,
    "Oceania": 1.18,
    "Europe": 1.28,
    "North America": 1.32,
    "South America": 1.36,
    "Middle East": 1.22,
    "Africa": 1.38,
}


def generate_product_pricing(
    product: dict,
    cogs_per_unit_idr: float,
    target_margin_percent: float,
    target_country_code: str = "JP",
) -> dict[str, Any]:
    fx = pricing_svc.get_exchange_rate()
    rate = float(fx.get("rate", pricing_svc.FALLBACK_RATE))
    # Per-unit: EXW = COGS*(1+margin)/kurs; FOB = EXW*1.08; CIF = FOB*multiplier region
    exw = pricing_svc.calculate_exw(cogs_per_unit_idr, 0, target_margin_percent, rate)
    fob = round(exw * 1.08, 2)
    region = country_data.region_of(target_country_code)
    cif = round(fob * _SHIPPING_MULTIPLIER.get(region, 1.12), 2)
    insight = ai.complete(
        "You are an export pricing advisor. Reply concisely in Indonesian with pricing insight.",
        f"Product {product.get('name', '')}: EXW {exw} {pricing_svc.DISPLAY_CURRENCY}, FOB {fob} {pricing_svc.DISPLAY_CURRENCY}, CIF {cif} {pricing_svc.DISPLAY_CURRENCY} to {target_country_code}.",
        kind="pricing_insight",
    )
    return {
        "productId": product.get("id"),
        "cogsPerUnitIdr": round(cogs_per_unit_idr, 2),
        "targetMarginPercent": target_margin_percent,
        "targetCountryCode": target_country_code,
        "exchangeRateUsed": rate,
        "currency": pricing_svc.DISPLAY_CURRENCY,
        "exwPrice": exw,
        "fobPrice": fob,
        "cifPrice": cif,
        "pricingInsight": insight or "Harga kompetitif untuk pasar tujuan; pantau kurs.",
        "pricingBreakdown": {
            "HPP (IDR)": cogs_per_unit_idr,
            "Margin": f"{target_margin_percent}%",
            f"EXW ({pricing_svc.DISPLAY_CURRENCY})": exw,
            f"FOB ({pricing_svc.DISPLAY_CURRENCY})": fob,
            f"CIF ({pricing_svc.DISPLAY_CURRENCY})": cif,
            "Exchange rate": rate,
        },
        "generatedAt": "now",
    }


# ---------------------------------------------------------------------------
# Deskripsi katalog AI (internasional)
# ---------------------------------------------------------------------------
def generate_catalog_description(product: dict, save_to_catalog: bool = False, catalog: dict | None = None) -> dict[str, Any]:
    """Deskripsi internasional: export_description, technical_specs, safety_info."""
    food = is_food_product(product)
    parsed = ai.ask_json(
        "You write B2B international product copy for Indonesian exports. Return JSON with keys: "
        "export_buyer_description (string), technical_spec_sheet (list of {label, value}), "
        "safety_sheet (list of {label, value}).",
        f"Product: {product.get('name', '')} ({product.get('category', '')}). Food product: {food}.",
        kind="catalog_description",
    )
    if parsed and isinstance(parsed, dict):
        result = {
            "export_description": parsed.get("export_buyer_description") or "",
            "technical_specs": parsed.get("technical_spec_sheet") or [],
            "safety_info": parsed.get("safety_sheet") or [],
        }
    else:
        result = {
            "export_description": (
                f"{product.get('name', '')} — produk Indonesia berkualitas untuk pasar ekspor B2B. "
                f"Kategori: {product.get('category', '')}. "
                "Sertifikasi dan spesifikasi tersedia berdasarkan permintaan."
            ),
            "technical_specs": [
                {"label": "Product", "value": product.get("name", "")},
                {"label": "Category", "value": product.get("category", "")},
                {"label": "Origin", "value": product.get("origin", "")},
                {"label": "Packaging", "value": product.get("packaging", "")},
                {"label": "MOQ", "value": product.get("moq", "")},
                {"label": "Lead time", "value": product.get("leadTime", "")},
            ],
            "safety_info": [
                {"label": "Certifications", "value": ", ".join(product.get("certificates", []) or [])},
                {"label": "Food grade", "value": "Yes" if food else "N/A"},
            ],
        }
    if save_to_catalog and catalog:
        catalog["exportDescription"] = result["export_description"]
        catalog["technicalSpecs"] = result["technical_specs"]
        catalog["safetyInfo"] = result["safety_info"]
        catalog["status"] = "Needs Review"
        catalog["updatedAt"] = "now"
        db.save(catalog)
    return result
