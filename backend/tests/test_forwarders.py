"""Test layanan forwarder (app/services/forwarders.py)."""
import pytest

from app import db
from app.services import forwarders


@pytest.fixture(autouse=True)
def fresh_store():
    db.reset_store()
    yield
    db.reset_store()


def _seed_forwarders():
    db.insert("forwarders", {
        "id": "FWD-1", "name": "NGL", "averageRating": 4.8, "totalReviews": 10,
        "specializationRoutes": ["ID-JP"], "coverage": "Japan and North Asia",
    })
    db.insert("forwarders", {
        "id": "FWD-2", "name": "AFN", "averageRating": 4.2, "totalReviews": 5,
        "specializationRoutes": ["ID-DE"], "coverage": "Europe",
    })
    db.insert("forwarders", {
        "id": "FWD-3", "name": "MPE", "averageRating": 0, "totalReviews": 0,
        "specializationRoutes": [], "coverage": "Singapore and Malaysia",
    })


def test_recalculate_rating_tanpa_review():
    fwd = db.insert("forwarders", {"id": "FWD-X", "name": "X"})
    result = forwarders.recalculate_rating(fwd)
    assert result["averageRating"] == 0
    assert result["totalReviews"] == 0


def test_recalculate_rating_dengan_review():
    fwd = db.insert("forwarders", {"id": "FWD-1", "name": "NGL"})
    # id unik per review — insert() kini idempotent per id (duplikat id = update)
    for i, rating in enumerate([5, 5, 4], start=1):
        db.insert("forwarder_reviews", {"id": f"RV-RATE-{i}", "forwarderId": "FWD-1", "rating": rating})
    result = forwarders.recalculate_rating(fwd)
    assert result["totalReviews"] == 3
    assert result["averageRating"] == round(14 / 3, 1)


def test_insert_idempotent_update_bukan_duplikat():
    """insert() dengan id yang sama harus update, bukan membuat record dobel."""
    fwd = db.insert("forwarders", {"id": "FWD-IDEM", "name": "A"})
    db.insert("forwarder_reviews", {"id": "RV-IDEM-1", "forwarderId": "FWD-IDEM", "rating": 5})
    db.insert("forwarder_reviews", {"id": "RV-IDEM-1", "forwarderId": "FWD-IDEM", "rating": 3})
    reviews = [r for r in db.all("forwarder_reviews") if r["forwarderId"] == "FWD-IDEM"]
    assert len(reviews) == 1, "duplikat id harus update-in-place"
    assert reviews[0]["rating"] == 3


def test_get_recommendations_berdasarkan_rute_dan_rating():
    _seed_forwarders()
    recs = forwarders.get_recommendations("JP")
    assert recs[0]["id"] == "FWD-1"  # rating tertinggi untuk rute ID-JP
    assert all(f["id"] == "FWD-1" for f in recs)


def test_get_recommendations_by_country_name():
    _seed_forwarders()
    # "ID" -> get_country("ID") = Indonesia; coverage "Indonesia" cocok
    db.insert("forwarders", {"id": "FWD-ID", "name": "Lokal", "averageRating": 4.0, "totalReviews": 2, "coverage": "Indonesia"})
    recs = forwarders.get_recommendations("ID")
    assert any(f["id"] == "FWD-ID" for f in recs)


def test_get_recommendations_limit():
    _seed_forwarders()
    recs = forwarders.get_recommendations("JP", limit=1)
    assert len(recs) == 1


def test_get_recommendations_tanpa_match():
    _seed_forwarders()
    recs = forwarders.get_recommendations("XY")
    assert recs == []


def test_get_statistics():
    fwd = db.insert("forwarders", {"id": "FWD-1", "name": "NGL", "averageRating": 4.0})
    db.insert("forwarder_reviews", {"id": "RV-1", "forwarderId": "FWD-1", "rating": 5, "umkmId": "U-1"})
    db.insert("forwarder_reviews", {"id": "RV-2", "forwarderId": "FWD-1", "rating": 4, "umkmId": "U-1"})
    db.insert("forwarder_reviews", {"id": "RV-3", "forwarderId": "FWD-1", "rating": 3, "umkmId": "U-2"})
    stats = forwarders.get_statistics("FWD-1")
    assert stats["totalReviews"] == 3
    assert stats["uniquePartnerships"] == 2
    assert stats["ratingDistribution"]["5"] == 33
    assert stats["ratingDistribution"]["4"] == 33
    assert len(stats["recentReviews"]) == 3
    assert len(stats["trend30Days"]) == 3


def test_get_statistics_forwarder_tidak_ada():
    assert forwarders.get_statistics("FWD-TIDAK") == {}
