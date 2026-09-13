"""Test regresi: bug yang diperbaiki demi paritas fitur dengan referensi ExportReadyAI."""
import zipfile
from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


def _login(c: TestClient) -> str:
    res = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
    assert res.status_code == 200
    return res.json()["meta"]["access_token"]


def test_catalog_images_dibatasi_per_katalog():
    """GET /catalogs/{id}/images/ hanya mengembalikan gambar milik katalog tsb (bukan semua gambar)."""
    with TestClient(app) as c:
        token = _login(c)
        headers = {"Authorization": f"Bearer {token}"}
        a = c.post("/api/v1/catalogs/", json={
            "title": "Katalog A", "productId": "PRD-COF-001", "targetMarket": "JP", "moq": "100",
        }, headers=headers).json()["data"]["id"]
        b = c.post("/api/v1/catalogs/", json={
            "title": "Katalog B", "productId": "PRD-COF-001", "targetMarket": "JP", "moq": "100",
        }, headers=headers).json()["data"]["id"]
        c.post("/api/v1/catalogs/{}/images/".format(a), json={"image_url": "https://img/a.jpg"}, headers=headers)
        c.post("/api/v1/catalogs/{}/images/".format(b), json={"image_url": "https://img/b.jpg"}, headers=headers)

        res = c.get("/api/v1/catalogs/{}/images/".format(a), headers=headers)
        assert res.status_code == 200
        items = res.json()["data"]
        assert len(items) == 1, items
        assert items[0]["catalogId"] == a
        assert items[0]["imageUrl"] == "https://img/a.jpg"

        res_b = c.get("/api/v1/catalogs/{}/images/".format(b), headers=headers)
        items_b = res_b.json()["data"]
        assert len(items_b) == 1
        assert items_b[0]["imageUrl"] == "https://img/b.jpg"


def test_register_role_admin_ditolak_400():
    """Self-register tidak boleh membuat user Admin (harus lewat /auth/register-admin/)."""
    with TestClient(app) as c:
        res = c.post("/api/v1/auth/register/", json={
            "name": "Penyusup", "email": "penyusup@example.com",
            "password": "password123", "role": "Admin",
        })
        assert res.status_code == 400


def test_register_role_tidak_ada_ditolak_400():
    """Role yang tidak dikenal juga ditolak saat self-register."""
    with TestClient(app) as c:
        res = c.post("/api/v1/auth/register/", json={
            "name": "Hacker", "email": "hacker@example.com",
            "password": "password123", "role": "Superuser",
        })
        assert res.status_code == 400


def test_export_audit_xlsx_memakai_audit_events():
    """Export XLSX audit membaca tabel audit_events (bukan tabel kosong 'audit')."""
    with TestClient(app) as c:
        token = _login(c)
        headers = {"Authorization": f"Bearer {token}"}
        # Pemicu audit event: mutasi produk
        res = c.post("/api/v1/products/", json={
            "name": "Kopi Audit", "category": "Makanan", "origin": "Aceh",
        }, headers=headers)
        assert res.status_code == 200

        out = c.get("/api/v1/audit/export.xlsx", headers=headers)
        assert out.status_code == 200
        assert out.content.startswith(b"PK")
        zf = zipfile.ZipFile(BytesIO(out.content))
        sheet = zf.read("xl/worksheets/sheet1.xml").decode("utf-8", errors="replace")
        # Data audit (aksi POST produk) ikut terekam di sheet
        assert "POST /api/v1/products/" in sheet


def test_admin_delete_regulasi_tidak_menghapus_negara():
    """Menghapus regulasi tidak boleh ikut menghapus record negara (bug tabel salah)."""
    with TestClient(app) as c:
        token = _login(c)
        headers = {"Authorization": f"Bearer {token}"}
        cty = c.post("/api/v1/admin/countries/", json={
            "country_code": "ZZ", "country_name": "Zzland", "region": "Test",
        }, headers=headers).json()["data"]["id"]
        reg = c.post("/api/v1/admin/countries/ZZ/regulations/create/", json={
            "rule_category": "Labeling", "forbidden_keywords": "X",
            "required_specs": "Y", "description_rule": "Z",
        }, headers=headers).json()["data"]["id"]

        res = c.delete("/api/v1/admin/regulations/{}/delete/".format(reg), headers=headers)
        assert res.status_code == 200

        # Negara tetap ada di database
        from app import db
        assert db.get("countries", cty) is not None


def test_catalog_detail_tidak_menyimpan_field_turunan():
    """GET /catalogs/{id}/ mengembalikan images (list) tanpa menyimpan field turunan ke db."""
    with TestClient(app) as c:
        token = _login(c)
        headers = {"Authorization": f"Bearer {token}"}
        cid = c.post("/api/v1/catalogs/", json={
            "title": "Katalog Detail", "productId": "PRD-COF-001", "targetMarket": "JP", "moq": "100",
        }, headers=headers).json()["data"]["id"]
        c.post("/api/v1/catalogs/{}/images/".format(cid), json={"image_url": "https://img/detail.jpg"}, headers=headers)

        res = c.get("/api/v1/catalogs/{}/".format(cid), headers=headers)
        assert res.status_code == 200
        data = res.json()["data"]
        assert isinstance(data["images"], list)
        assert len(data["images"]) == 1
        assert data["images"][0]["imageUrl"] == "https://img/detail.jpg"

        # Field turunan TIDAK tersimpan ke db: record tetap menyimpan jumlah (int)
        from app import db
        stored = db.get("catalogs", cid)
        assert isinstance(stored.get("images"), int)
        assert "variantTypes" not in stored


def test_regulasi_admin_negara_baru_bisa_dibuat():
    """Admin dapat membuat regulasi untuk negara yang baru dibuat via admin (paritas referensi)."""
    with TestClient(app) as c:
        token = _login(c)
        headers = {"Authorization": f"Bearer {token}"}
        c.post("/api/v1/admin/countries/", json={
            "country_code": "YY", "country_name": "Yyland", "region": "Test",
        }, headers=headers)
        res = c.post("/api/v1/admin/countries/YY/regulations/create/", json={
            "rule_category": "Ingredient", "forbidden_keywords": "Boraks",
            "required_specs": "", "description_rule": "Regulasi uji.",
        }, headers=headers)
        assert res.status_code == 200
        assert res.json()["data"]["countryCode"] == "YY"

        # Detail negara baru ikut menampilkan regulasi + regulations_count
        detail = c.get("/api/v1/countries/YY/")
        assert detail.status_code == 200
        assert len(detail.json()["data"]["regulations"]) == 1
        listing = c.get("/api/v1/countries/")
        yy = next((x for x in listing.json()["data"] if x["country_code"] == "YY"), None)
        assert yy is not None
        assert yy["regulationsCount"] >= 1


def test_regulation_recommendations_accept_language_header():
    """Endpoint rekomendasi regulasi mendukung header Accept-Language (paritas ExportReadyAI-fe)."""
    with TestClient(app) as c:
        token = _login(c)
        headers = {"Authorization": f"Bearer {token}"}
        # buat produk + enrichment + analisis (analisis butuh produk ter-enrich)
        prod = c.post("/api/v1/products/", json={
            "name": "Kopi Gayo", "category": "Makanan", "origin": "Aceh",
        }, headers=headers).json()["data"]
        c.post("/api/v1/products/{}/enrich/".format(prod["id"]), headers=headers)
        analysis = c.post("/api/v1/export-analysis/", json={
            "productId": prod["id"], "destination": "JP",
        }, headers=headers).json()["data"]
        aid = analysis["id"]

        res_en = c.get(
            "/api/v1/export-analysis/{}/regulation-recommendations/".format(aid),
            headers={"Accept-Language": "en"},
        )
        assert res_en.status_code == 200
        assert res_en.json()["data"]["language"] == "en"

        res_id = c.get(
            "/api/v1/export-analysis/{}/regulation-recommendations/".format(aid),
            headers={"Accept-Language": "id"},
        )
        assert res_id.status_code == 200
        assert res_id.json()["data"]["language"] == "id"
