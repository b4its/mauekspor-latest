"""Kontrak endpoint portal pembeli ekspor: /buyers/portal/.

Portal menyesuaikan katalog Published dengan negara asal pembeli:
- `?country=` (kode ISO atau nama) dipakai Admin / eksplisit
- `?buyer_id=` memakai field `country` pada record buyers
- profil Buyer milik user login (sourceCountries) dipakai otomatis
"""
from fastapi.testclient import TestClient

from app.main import app
from app import db  # noqa: F401

ADMIN = ("admin@mauekspor.example", "admin123")
BUYER = ("aya@hikari.example", "buyer123")


def _login(c: TestClient, creds: tuple[str, str] = ADMIN) -> str:
    res = c.post("/api/v1/auth/login/", json={"email": creds[0], "password": creds[1]})
    assert res.status_code == 200, res.text
    return res.json()["meta"]["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _publish(c: TestClient, token: str, title: str, target_market: str) -> str:
    created = c.post(
        "/api/v1/catalogs/",
        json={"title": title, "productId": "PRD-COF-001", "targetMarket": target_market, "moq": "100"},
        headers=_auth(token),
    )
    assert created.status_code == 200, created.text
    cid = created.json()["data"]["id"]
    pub = c.post(f"/api/v1/catalogs/{cid}/publish/", headers=_auth(token))
    assert pub.status_code == 200, pub.text
    return cid


def test_portal_hanya_menampilkan_katalog_published():
    with TestClient(app) as c:
        token = _login(c)
        published = _publish(c, token, "Katalog Portal Published", "Japan specialty importers")
        draft = c.post(
            "/api/v1/catalogs/",
            json={"title": "Katalog Draft Portal", "productId": "PRD-COF-001", "targetMarket": "Japan", "moq": "10"},
            headers=_auth(token),
        ).json()["data"]["id"]

        res = c.get("/api/v1/buyers/portal/?country=JP", headers=_auth(token))
        assert res.status_code == 200, res.text
        ids = [x["id"] for x in res.json()["data"]]
        assert published in ids
        assert draft not in ids


def test_portal_menyesuaikan_negara_dari_query_country():
    with TestClient(app) as c:
        token = _login(c)
        jp = _publish(c, token, "Catalog JP", "Japan specialty importers")
        de = _publish(c, token, "Catalog DE", "Germany retail chain")

        res = c.get("/api/v1/buyers/portal/?country=JP", headers=_auth(token))
        assert res.status_code == 200, res.text
        body = res.json()
        ids = [x["id"] for x in body["data"]]
        assert jp in ids
        assert de not in ids
        assert body["meta"]["detectedCountry"] == "Japan"
        assert body["data"][0]["relevanceScore"] >= body["data"][-1]["relevanceScore"]


def test_portal_negara_dari_record_buyer_id():
    with TestClient(app) as c:
        token = _login(c)
        jp = _publish(c, token, "Catalog Buyer JP", "Japan specialty importers")
        de = _publish(c, token, "Catalog Buyer DE", "Germany retail chain")

        res = c.get("/api/v1/buyers/portal/?buyer_id=BUY-HIKARI-JP", headers=_auth(token))
        assert res.status_code == 200, res.text
        body = res.json()
        ids = [x["id"] for x in body["data"]]
        assert jp in ids
        assert de not in ids
        assert body["meta"]["countries"] == ["Japan"]


def test_portal_negara_dari_profil_buyer_login():
    with TestClient(app) as c:
        buyer_token = _login(c, BUYER)
        # trigger seeding lalu pastikan profil buyer (U-003) berbunyi Jepang.
        # Seed dasar mungkin sudah punya profil utk U-003 dengan negara lain,
        # jadi update IN-PLACE agar deterministik (hindari profil bayangan).
        assert db.get("users", "U-003"), "seed user Buyer harus ada"
        existing = db.get_by("buyer_profiles", userId="U-003")
        if existing:
            existing["sourceCountries"] = ["Japan"]
            existing["source_countries"] = ["Japan"]
        else:
            db.insert("buyer_profiles", {
                "id": "BYP-TEST-U003",
                "userId": "U-003",
                "company_name": "Hikari Foods Co.",
                "source_countries": ["Japan"],
                "sourceCountries": ["Japan"],
            })

        res = c.get("/api/v1/buyers/portal/", headers=_auth(buyer_token))
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["meta"]["detectedCountry"] == "Japan"
        # katalog target Japan harus relevan
        assert len(body["data"]) >= 1
        assert all(x["matchedCountry"] == "Japan" for x in body["data"])


def test_portal_menyertakan_nama_produk():
    with TestClient(app) as c:
        token = _login(c)
        cid = _publish(c, token, "Catalog Produk", "Japan specialty importers")
        res = c.get("/api/v1/buyers/portal/?country=JP", headers=_auth(token))
        item = next(x for x in res.json()["data"] if x["id"] == cid)
        assert item["productName"] == "Gayo Arabica Coffee Beans"
        assert item["productOrigin"]


def test_portal_tanpa_negara_menampilkan_semua_published():
    with TestClient(app) as c:
        token = _login(c)
        a = _publish(c, token, "Catalog All A", "Japan specialty importers")
        b = _publish(c, token, "Catalog All B", "Germany retail chain")

        res = c.get("/api/v1/buyers/portal/", headers=_auth(token))
        assert res.status_code == 200, res.text
        ids = [x["id"] for x in res.json()["data"]]
        assert a in ids and b in ids
        assert res.json()["meta"]["detectedCountry"] == ""


def test_portal_search_memfilter_judul():
    with TestClient(app) as c:
        token = _login(c)
        keep = _publish(c, token, "Unique Kopi Gayo", "Japan specialty importers")
        drop = _publish(c, token, "Other Furniture", "Japan specialty importers")
        res = c.get("/api/v1/buyers/portal/?country=JP&search=kopi", headers=_auth(token))
        ids = [x["id"] for x in res.json()["data"]]
        assert keep in ids
        assert drop not in ids
