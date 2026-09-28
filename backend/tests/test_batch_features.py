"""Test fitur batch: registry export, export generik, sorting, dan konversi quotation->order."""
from fastapi.testclient import TestClient

from app.main import app


def _login(c: TestClient) -> dict:
    res = c.post(
        "/api/v1/auth/login/",
        json={"email": "admin@mauekspor.example", "password": "admin123"},
    )
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['meta']['access_token']}"}


# ---------------------------------------------------------------------------
# Export registry
# ---------------------------------------------------------------------------
def test_export_registry_lists_modules():
    with TestClient(app) as c:
        headers = _login(c)
        res = c.get("/api/v1/exports/tables/", headers=headers)
        assert res.status_code == 200
        tables = res.json()["data"]
        for expected in ("products", "orders", "shipments", "payments", "suppliers", "tasks", "documents"):
            assert expected in tables


def test_export_orders_csv_and_xlsx():
    with TestClient(app) as c:
        headers = _login(c)
        csv_res = c.get("/api/v1/orders/export.csv", headers=headers)
        assert csv_res.status_code == 200
        assert "text/csv" in csv_res.headers["content-type"]
        xlsx_res = c.get("/api/v1/orders/export.xlsx", headers=headers)
        assert xlsx_res.status_code == 200
        assert xlsx_res.content[:2] == b"PK"  # zip magic


def test_export_alias_paths_still_work():
    with TestClient(app) as c:
        headers = _login(c)
        for path in ("/api/v1/export-analysis/export.csv", "/api/v1/audit/export.csv"):
            res = c.get(path, headers=headers)
            assert res.status_code == 200, path


def test_generic_export_endpoint():
    with TestClient(app) as c:
        headers = _login(c)
        res = c.get("/api/v1/exports.csv", params={"table": "suppliers"}, headers=headers)
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]


def test_generic_export_unknown_table_404():
    with TestClient(app) as c:
        headers = _login(c)
        res = c.get("/api/v1/exports.csv", params={"table": "does_not_exist"}, headers=headers)
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# Search / status / sort / pagination on upgraded list endpoints
# ---------------------------------------------------------------------------
def test_list_orders_supports_search_and_meta():
    with TestClient(app) as c:
        headers = _login(c)
        res = c.get("/api/v1/orders/", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert "total" in body["meta"]

        full = len(body["data"])
        limited = c.get("/api/v1/orders/", params={"limit": 2}, headers=headers).json()
        assert len(limited["data"]) <= 2
        assert limited["meta"]["total"] == full


def test_list_tasks_sort_by_title():
    with TestClient(app) as c:
        headers = _login(c)
        asc = c.get("/api/v1/tasks/", params={"sort_by": "title", "sort_dir": "asc"}, headers=headers).json()["data"]
        desc = c.get("/api/v1/tasks/", params={"sort_by": "title", "sort_dir": "desc"}, headers=headers).json()["data"]
        if len(asc) > 1:
            assert [str(t.get("title", "")).lower() for t in asc] == sorted(
                str(t.get("title", "")).lower() for t in asc
            )
            assert [str(t.get("title", "")).lower() for t in desc] == sorted(
                (str(t.get("title", "")).lower() for t in desc), reverse=True
            )


def test_list_orders_status_filter():
    with TestClient(app) as c:
        headers = _login(c)
        all_orders = c.get("/api/v1/orders/", headers=headers).json()["data"]
        if not all_orders:
            return
        status = all_orders[0].get("status")
        filtered = c.get("/api/v1/orders/", params={"status": status}, headers=headers).json()["data"]
        assert all(str(o.get("status", "")).lower() == str(status).lower() for o in filtered)


# ---------------------------------------------------------------------------
# Quotation -> Order conversion
# ---------------------------------------------------------------------------
def test_quotation_to_order_creates_and_links_order():
    with TestClient(app) as c:
        headers = _login(c)
        created = c.post(
            "/api/v1/quotations/",
            json={
                "buyer": "Hikari Foods Co.",
                "product": "Gayo Arabica Coffee Beans",
                "value": 42800,
                "currency": "USD",
                "incoterm": "FOB",
                "destination": "Japan",
            },
            headers=headers,
        )
        assert created.status_code == 200
        quotation_id = created.json()["data"]["id"]

        conv = c.post(f"/api/v1/quotations/{quotation_id}/to-order/", headers=headers)
        assert conv.status_code == 200
        order = conv.json()["data"]
        assert order["id"].startswith("ORD")
        assert order["quotationId"] == quotation_id
        assert order["buyer"] == "Hikari Foods Co."
        assert order["value"] == 42800

        # Quotation ditandai Accepted dan menyimpan orderId.
        quote = c.get(f"/api/v1/quotations/{quotation_id}/", headers=headers).json()["data"]
        assert quote["status"] == "Accepted"
        assert quote["orderId"] == order["id"]

        # Order dapat dibaca kembali.
        fetched = c.get(f"/api/v1/orders/{order['id']}/", headers=headers)
        assert fetched.status_code == 200


def test_quotation_to_order_is_idempotent():
    with TestClient(app) as c:
        headers = _login(c)
        quotation_id = c.post(
            "/api/v1/quotations/", json={"buyer": "Merlion Grocers", "value": 100}, headers=headers
        ).json()["data"]["id"]

        first = c.post(f"/api/v1/quotations/{quotation_id}/to-order/", headers=headers).json()["data"]
        second = c.post(f"/api/v1/quotations/{quotation_id}/to-order/", headers=headers)
        assert second.status_code == 200
        body = second.json()
        assert body["meta"].get("deduplicated") is True
        assert body["data"]["id"] == first["id"]


def test_quotation_to_order_404_for_unknown():
    with TestClient(app) as c:
        headers = _login(c)
        res = c.post("/api/v1/quotations/Q-DOES-NOT-EXIST/to-order/", headers=headers)
        assert res.status_code == 404
