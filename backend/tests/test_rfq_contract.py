"""Regresi kontrak RFQ: respons list & detail harus mengekspos alias `buyer`
dan `product` yang dibaca frontend, tanpa menghapus field asli
`buyerName`/`productId`.

Sebelumnya record seed hanya menyimpan `buyerName`/`productId`, sehingga
halaman /rfq dan /rfq/[id] menampilkan pembeli & produk kosong (mis. " - Japan").
"""
from fastapi.testclient import TestClient

from app.main import app

ADMIN = ("admin@mauekspor.example", "admin123")


def _login(c: TestClient) -> str:
    res = c.post("/api/v1/auth/login/", json={"email": ADMIN[0], "password": ADMIN[1]})
    assert res.status_code == 200, res.text
    return res.json()["meta"]["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_rfq_list_exposes_buyer_and_product_aliases():
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/rfqs/", headers=_auth(token))
        assert res.status_code == 200, res.text
        items = res.json()["data"]
        assert items, "seed RFQ kosong"
        for item in items:
            # Alias wajib terisi (fallback minimal ke id bila produk tak ada).
            assert item.get("buyer"), f"buyer kosong untuk {item.get('id')}"
            assert item.get("product"), f"product kosong untuk {item.get('id')}"
            # Kontrak lama tetap dipertahankan.
            assert "buyerName" in item and "productId" in item


def test_rfq_detail_exposes_buyer_and_product_aliases():
    with TestClient(app) as c:
        token = _login(c)
        res = c.get("/api/v1/rfqs/RFQ-0891/", headers=_auth(token))
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["buyer"] == data["buyerName"] == "Hikari Foods Co."
        assert data["product"] == "Gayo Arabica Coffee Beans"


def test_rfq_create_returns_aliases():
    with TestClient(app) as c:
        token = _login(c)
        res = c.post(
            "/api/v1/rfqs/",
            json={"buyerName": "BuyCo", "productId": "PRD-COF-001",
                  "destination": "JP", "quantity": "1"},
            headers=_auth(token),
        )
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["buyer"] == "BuyCo"
        assert data["product"] == "Gayo Arabica Coffee Beans"
