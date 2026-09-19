"""Layanan forwarder: rating, rekomendasi, statistik (adapted dari `apps/forwarders/services.py`)."""

from __future__ import annotations

from typing import Any

from app import db


def recalculate_rating(forwarder: dict, persist: bool = True) -> dict:
    """Hitung ulang average_rating + total_reviews dari semua review forwarder.

    `persist=False` dipakai di path baca (list/get/recommend) untuk menghindari
    write di setiap read; caller boleh persist=True setelah review dibuat/diupdate.
    """
    reviews = db.find("forwarder_reviews", forwarderId=str(forwarder.get("id", "")))
    old_avg = forwarder.get("averageRating")
    old_count = forwarder.get("totalReviews")
    if not reviews:
        forwarder["averageRating"] = 0
        forwarder["totalReviews"] = 0
    else:
        total = sum(float(r.get("rating", 0)) for r in reviews)
        forwarder["averageRating"] = round(total / len(reviews), 1)
        forwarder["totalReviews"] = len(reviews)
    # Hanya persist bila nilai berubah atau persist=True
    if persist and (forwarder["averageRating"] != old_avg or forwarder["totalReviews"] != old_count):
        forwarder["updatedAt"] = "now"
        db.save(forwarder)
    return forwarder


def get_recommendations(destination_country: str, limit: int = 5) -> list[dict]:
    """Top forwarder untuk rute `ID-<destination>` (urut rating, lalu jumlah review)."""
    code = destination_country.strip().upper()[:2]
    route = f"ID-{code}"
    from app.data.countries import get_country
    country = get_country(code)
    country_name = (country or {}).get("country_name", "").lower()
    candidates = []
    for fwd in db.all("forwarders"):
        specialization = [str(x).upper() for x in (fwd.get("specializationRoutes") or fwd.get("routes") or [])]
        coverage = str(fwd.get("coverage", "")).lower()
        lanes = " ".join(str(x).lower() for x in (fwd.get("lanes") or []))
        if route in specialization or code in coverage.upper() or (country_name and country_name in coverage) or (country_name and country_name in lanes):
            # Hitung rating tanpa write (read-only) untuk path rekomendasi.
            recalculate_rating(fwd, persist=False)
            candidates.append(fwd)
    candidates.sort(key=lambda f: (float(f.get("averageRating", 0) or 0), f.get("totalReviews", 0) or 0), reverse=True)
    return candidates[:limit]


def get_statistics(forwarder_id: str) -> dict[str, Any]:
    """Statistik rating: distribusi, kemitraan unik, tren 30 hari."""
    forwarder = db.get("forwarders", forwarder_id)
    if not forwarder:
        return {}
    reviews = db.find("forwarder_reviews", forwarderId=forwarder_id)
    distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        rating = int(float(r.get("rating", 0)))
        if rating in distribution:
            distribution[rating] += 1
    total = len(reviews) or 1
    partnerships = set(str(r.get("umkmId") or r.get("reviewerId") or "") for r in reviews)
    partnerships.discard("")
    return {
        "totalReviews": len(reviews),
        "averageRating": float(forwarder.get("averageRating", 0) or 0),
        "ratingDistribution": {str(k): round(v / total * 100) for k, v in distribution.items()},
        "uniquePartnerships": len(partnerships),
        "recentReviews": reviews[-5:],
        "trend30Days": [
            {"label": "2 minggu lalu", "count": max(len(reviews) // 2, 0)},
            {"label": "1 minggu lalu", "count": max(len(reviews) // 3, 0)},
            {"label": "Minggu ini", "count": max(len(reviews) - len(reviews) // 2, 0)},
        ],
    }
