"""Test layanan market intelligence & catalog description (app/services/market_intel.py)."""
import pytest

from app import db
from app.services import market_intel


@pytest.fixture(autouse=True)
def fresh_store():
    db.reset_store()
    yield
    db.reset_store()


def test_is_food_product_berbagai_keyword():
    assert market_intel.is_food_product({"name": "Kopi Gayo", "category": "F&B"})
    assert market_intel.is_food_product({"name": "Chips", "description": "cassava snack"})
    assert market_intel.is_food_product({"name": "Teh", "category": "Beverage"})
    assert not market_intel.is_food_product({"name": "Rattan Chair", "category": "Furniture"})


def test_fallback_market_intelligence_deterministik():
    product = {"id": "P-1", "name": "Kopi", "category": "Food & Beverage"}
    result = market_intel._fallback_market_intelligence(product)
    assert result["productId"] == "P-1"
    assert len(result["recommendedCountries"]) == 5
    assert result["recommendedCountries"][0]["code"] == "JP"
    assert result["countriesToAvoid"][0]["code"] == "KP"
    assert result["overallRecommendation"]


def test_generate_market_intelligence_fallback_saat_ai_tidak_menghasilkan(monkeypatch):
    monkeypatch.setattr(market_intel.ai, "ask_json", lambda *a, **k: None)
    product = {"id": "P-1", "name": "Kopi", "category": "Food & Beverage"}
    result = market_intel.generate_market_intelligence(product)
    assert result["productId"] == "P-1"
    assert len(result["recommendedCountries"]) == 5  # fallback


def test_generate_market_intelligence_dari_ai(monkeypatch):
    ai_result = {
        "recommended_countries": [{"country": "Japan", "code": "JP", "score": 90, "reason": "r"}],
        "countries_to_avoid": [],
        "market_trends": ["t1"],
        "competitive_landscape": "c",
        "growth_opportunities": ["g"],
        "risks_and_challenges": ["r"],
        "overall_recommendation": "o",
    }
    monkeypatch.setattr(market_intel.ai, "ask_json", lambda *a, **k: ai_result)
    product = {"id": "P-1", "name": "Kopi", "category": "Food & Beverage"}
    result = market_intel.generate_market_intelligence(product)
    assert result["recommendedCountries"][0]["code"] == "JP"
    assert result["marketTrends"] == ["t1"]
    # forwarders diisi dari rekomendasi (kosong tanpa seed forwarder)
    assert "forwarders" in result["recommendedCountries"][0]


def test_generate_product_pricing():
    product = {"id": "P-1", "name": "Kopi"}
    result = market_intel.generate_product_pricing(product, cogs_per_unit_idr=10000, target_margin_percent=20, target_country_code="JP")
    assert result["productId"] == "P-1"
    assert result["targetCountryCode"] == "JP"
    assert result["exwPrice"] > 0
    assert result["fobPrice"] > result["exwPrice"]
    assert result["cifPrice"] > result["fobPrice"]
    assert "pricingBreakdown" in result
    assert result["pricingInsight"]  # fallback insight dari ai.complete mock


def test_generate_catalog_description_fallback():
    product = {"id": "P-1", "name": "Kopi Gayo", "category": "Food & Beverage", "origin": "Aceh",
               "packaging": "250g", "moq": "1000", "leadTime": "21d", "certificates": ["Halal"]}
    result = market_intel.generate_catalog_description(product)
    assert result["export_description"]
    assert any(s["label"] == "Product" for s in result["technical_specs"])
    assert any(s["label"] == "Food grade" for s in result["safety_info"])
    assert result["safety_info"][1]["value"] == "Yes"  # food


def test_generate_catalog_description_non_food():
    product = {"name": "Rattan Chair", "category": "Furniture", "certificates": []}
    result = market_intel.generate_catalog_description(product)
    assert result["safety_info"][1]["value"] == "N/A"


def test_generate_catalog_description_save_ke_catalog():
    catalog = {"id": "CAT-1", "title": "Katalog"}
    db.insert("catalogs", catalog)
    product = {"name": "Kopi", "category": "Food & Beverage"}
    result = market_intel.generate_catalog_description(product, save_to_catalog=True, catalog=catalog)
    assert result["export_description"]
    assert catalog["exportDescription"] == result["export_description"]
    assert catalog["status"] == "Needs Review"
