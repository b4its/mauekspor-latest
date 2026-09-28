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


def test_generic_export_requires_authentication():
    with TestClient(app) as c:
        res = c.get("/api/v1/exports.csv", params={"table": "buyers"})
        assert res.status_code == 401


def test_generic_export_honors_role_permissions():
    with TestClient(app) as c:
        login = c.post(
            "/api/v1/auth/login/",
            json={"email": "aya@hikari.example", "password": "buyer123"},
        )
        token = login.json()["meta"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        # Buyer tidak boleh mengekspor CRM buyers maupun daftar payment.
        assert c.get("/api/v1/exports.csv", params={"table": "buyers"}, headers=headers).status_code == 403
        assert c.get("/api/v1/exports.csv", params={"table": "payments"}, headers=headers).status_code == 403
        # Katalog adalah modul yang memang boleh dibaca Buyer.
        assert c.get("/api/v1/exports.csv", params={"table": "catalogs"}, headers=headers).status_code == 200


def test_csv_export_escapes_formula_cells():
    from app.api.routes import _csv_response

    response = _csv_response([["name"], ["=HYPERLINK(\"https://evil.example\")"], ["+1+1"]], "safe.csv")
    text = response.body.decode()
    assert "'=HYPERLINK" in text
    assert "'+1+1" in text


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
        # State machine: quotation harus Accepted dulu sebelum dikonversi.
        assert c.post(f"/api/v1/quotations/{quotation_id}/to-order/", headers=headers).status_code == 409
        accepted = c.post(f"/api/v1/quotations/{quotation_id}/accept/", headers=headers)
        assert accepted.status_code == 200

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
        c.post(f"/api/v1/quotations/{quotation_id}/accept/", headers=headers)

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


# ---------------------------------------------------------------------------
# Every collection list endpoint exposes search/status/sort/pagination meta
# ---------------------------------------------------------------------------
# (path, a status value that exists in seed data)
_LIST_ENDPOINTS = [
    "/api/v1/trade-projects/", "/api/v1/business-profiles/", "/api/v1/compliance/requirements/",
    "/api/v1/audit/", "/api/v1/team/", "/api/v1/templates/", "/api/v1/automations/", "/api/v1/integrations/",
    "/api/v1/knowledge/", "/api/v1/educational/articles/", "/api/v1/calendar/", "/api/v1/files/",
    "/api/v1/messages/", "/api/v1/reports/", "/api/v1/billing/", "/api/v1/support/", "/api/v1/api-keys/",
    "/api/v1/buyers/", "/api/v1/buyer-requests/", "/api/v1/catalogs/", "/api/v1/export-analysis/",
    "/api/v1/orders/", "/api/v1/quotations/", "/api/v1/shipments/", "/api/v1/payments/", "/api/v1/tasks/", "/api/v1/suppliers/",
]


def test_all_collection_lists_expose_pagination_meta():
    with TestClient(app) as c:
        headers = _login(c)
        for path in _LIST_ENDPOINTS:
            res = c.get(path, params={"limit": 2}, headers=headers)
            assert res.status_code == 200, path
            body = res.json()
            assert "data" in body and "meta" in body, path
            assert "total" in body["meta"], path
            assert body["meta"]["total"] >= len(body["data"]), path


def test_all_collection_lists_accept_sort_params():
    with TestClient(app) as c:
        headers = _login(c)
        for path in _LIST_ENDPOINTS:
            res = c.get(path, params={"sort_by": "id", "sort_dir": "asc"}, headers=headers)
            assert res.status_code == 200, path


def test_all_collection_lists_accept_status_filter():
    with TestClient(app) as c:
        headers = _login(c)
        for path in _LIST_ENDPOINTS:
            res = c.get(path, params={"status": "nonexistent-status"}, headers=headers)
            assert res.status_code == 200, path
            # Filter status yang tidak ada harus menghasilkan koleksi kosong, bukan 500.
            assert res.json()["data"] == [], path


def test_search_narrows_trade_projects():
    with TestClient(app) as c:
        headers = _login(c)
        all_rows = c.get("/api/v1/trade-projects/", headers=headers).json()["data"]
        if not all_rows:
            return
        needle = str(all_rows[0]["name"])[:6]
        filtered = c.get("/api/v1/trade-projects/", params={"search": needle}, headers=headers).json()["data"]
        assert filtered
        assert all(needle.lower() in str(r.get("name", "")).lower() for r in filtered)


def test_sort_dir_desc_reverses_order():
    with TestClient(app) as c:
        headers = _login(c)
        asc = c.get("/api/v1/team/", params={"sort_by": "name", "sort_dir": "asc"}, headers=headers).json()["data"]
        desc = c.get("/api/v1/team/", params={"sort_by": "name", "sort_dir": "desc"}, headers=headers).json()["data"]
        if len(asc) > 1:
            assert [str(r.get("name", "")).lower() for r in asc] == sorted(
                str(r.get("name", "")).lower() for r in asc
            )
            assert [str(r.get("name", "")).lower() for r in desc] == sorted(
                (str(r.get("name", "")).lower() for r in desc), reverse=True
            )


# ---------------------------------------------------------------------------
# Export registry now covers every upgraded module
# ---------------------------------------------------------------------------
def test_export_registry_covers_more_modules():
    with TestClient(app) as c:
        headers = _login(c)
        res = c.get("/api/v1/exports/tables/", headers=headers)
        assert res.status_code == 200
        tables = set(res.json()["data"])
        for expected in (
            "projects", "team_members", "templates", "automations",
            "integrations", "knowledge_articles", "calendar_events",
            "files", "messages", "reports", "billing_records",
            "support_tickets", "api_keys",
        ):
            assert expected in tables, expected


def test_upgraded_module_export_has_header_and_rows():
    with TestClient(app) as c:
        headers = _login(c)
        for module in ("projects", "team-members", "reports", "support-tickets"):
            res = c.get(f"/api/v1/{module}/export.csv", headers=headers)
            assert res.status_code == 200, module
            assert "text/csv" in res.headers["content-type"], module
            first_line = res.text.strip().splitlines()[0]
            assert first_line, module


# ---------------------------------------------------------------------------
# Generic batch delete endpoints
# ---------------------------------------------------------------------------
def test_batch_delete_removes_tasks_and_reports_count():
    with TestClient(app) as c:
        headers = _login(c)
        created = [
            c.post("/api/v1/tasks/", json={"title": f"Batch task {i}"}, headers=headers).json()["data"]["id"]
            for i in range(3)
        ]
        res = c.post("/api/v1/tasks/batch/delete/", json={"ids": [*created, "TSK-DOES-NOT-EXIST"]}, headers=headers)
        assert res.status_code == 200
        body = res.json()["data"]
        # Hanya id yang benar-benar ada yang dilaporkan terhapus.
        assert sorted(body["deleted"]) == sorted(created)
        assert body["deletedCount"] == len(created)
        # Verifikasi hilang dari koleksi.
        remaining = {t["id"] for t in c.get("/api/v1/tasks/", headers=headers).json()["data"]}
        assert remaining.isdisjoint(created)


def test_batch_delete_empty_ids_returns_422():
    with TestClient(app) as c:
        headers = _login(c)
        res = c.post("/api/v1/orders/batch/delete/", json={"ids": []}, headers=headers)
        assert res.status_code == 422


def test_batch_delete_available_for_common_modules():
    with TestClient(app) as c:
        headers = _login(c)
        for module in ("orders", "quotations", "shipments", "payments", "documents", "suppliers", "buyers", "messages", "support", "notifications"):
            res = c.post(f"/api/v1/{module}/batch/delete/", json={"ids": []}, headers=headers)
            # 422 (validasi ids kosong) membuktikan route terdaftar — bukan 404/405.
            assert res.status_code == 422, module


def test_notification_batch_delete_enforces_ownership():
    from app import db

    with TestClient(app) as c:
        login = c.post(
            "/api/v1/auth/login/",
            json={"email": "aya@hikari.example", "password": "buyer123"},
        )
        token = login.json()["meta"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        db.insert("notifications", {"id": "NTF-OWN", "title": "milik buyer", "status": "Unread", "ownerId": "U-003"})
        db.insert("notifications", {"id": "NTF-FOREIGN", "title": "rahasia", "status": "Unread", "ownerId": "U-999"})

        res = c.post(
            "/api/v1/notifications/batch/delete/",
            json={"ids": ["NTF-OWN", "NTF-FOREIGN"]},
            headers=headers,
        )
        assert res.status_code == 200
        assert res.json()["data"] == {"deleted": ["NTF-OWN"], "deletedCount": 1}
        assert db.get("notifications", "NTF-OWN") is None
        assert db.get("notifications", "NTF-FOREIGN") is not None


# ---------------------------------------------------------------------------
# PRD: document types, provenance, gates (FR-DOC/FR-COMPL/FR-AI/FR-CAT/FR-COMM)
# ---------------------------------------------------------------------------
def test_document_types_endpoint_lists_supported_and_required():
    with TestClient(app) as c:
        headers = _login(c)
        res = c.get("/api/v1/documents/types/", params={"commodityGroup": "pertanian", "incoterm": "CIF"}, headers=headers)
        assert res.status_code == 200
        body = res.json()["data"]
        names = [t["type"] for t in body["types"]]
        assert "Phytosanitary Certificate" in names
        assert "Bill of Lading" in names
        # CIF menambahkan Insurance Certificate.
        assert "Insurance Certificate" in body["required"]


def test_generate_document_rejects_unsupported_type():
    with TestClient(app) as c:
        headers = _login(c)
        res = c.post("/api/v1/documents/generate/", json={"type": "Alien Permit"}, headers=headers)
        assert res.status_code == 422


def test_generate_document_accepts_health_certificate():
    with TestClient(app) as c:
        headers = _login(c)
        res = c.post("/api/v1/documents/generate/", json={"type": "Health Certificate"}, headers=headers)
        assert res.status_code == 200
        assert res.json()["data"]["type"] == "Health Certificate"


def _fresh_analysis(c, headers):
    """Buat analisis untuk produk unik agar tidak menabrak dedup (product,country)."""
    product = c.post("/api/v1/products/", json={
        "name": f"Provenance Coffee {len(c.get('/api/v1/products/', headers=headers).json()['data'])}",
        "category": "Agro", "hs": "090111", "origin": "Aceh", "packaging": "Karung 60kg",
    }, headers=headers).json()["data"]
    return product["id"]


def test_analysis_carries_trust_and_required_documents():
    with TestClient(app) as c:
        headers = _login(c)
        pid = _fresh_analysis(c, headers)
        created = c.post("/api/v1/export-analysis/", json={"productId": pid, "destination": "Japan"}, headers=headers)
        assert created.status_code == 200
        data = created.json()["data"]
        assert data.get("trust", {}).get("advisory") is True
        assert data["trust"]["humanReviewRequired"] is True
        assert isinstance(data.get("requiredDocuments"), list) and data["requiredDocuments"]


def test_regulation_recommendations_include_sources_and_trust():
    with TestClient(app) as c:
        headers = _login(c)
        pid = _fresh_analysis(c, headers)
        created = c.post("/api/v1/export-analysis/", json={"productId": pid, "destination": "Japan"}, headers=headers)
        aid = created.json()["data"]["id"]
        rec = c.get(f"/api/v1/export-analysis/{aid}/regulation-recommendations/", headers=headers)
        assert rec.status_code == 200
        data = rec.json()["data"]
        assert data.get("trust", {}).get("advisory") is True
        assert data.get("sources"), "harus ada daftar sumber"
        # Setiap bagian ditandai asal-usulnya.
        assert all("generatedBy" in sec for sec in data["sections"])


def test_quotation_to_order_requires_accepted_status():
    with TestClient(app) as c:
        headers = _login(c)
        qid = c.post("/api/v1/quotations/", json={"buyer": "Gate Test", "value": 10}, headers=headers).json()["data"]["id"]
        blocked = c.post(f"/api/v1/quotations/{qid}/to-order/", headers=headers)
        assert blocked.status_code == 409
        c.post(f"/api/v1/quotations/{qid}/accept/", headers=headers)
        ok = c.post(f"/api/v1/quotations/{qid}/to-order/", headers=headers)
        assert ok.status_code == 200


# ---------------------------------------------------------------------------
# PRD FR-EXP-2: scoped exports (selected / filtered / filename scope)
# ---------------------------------------------------------------------------
def test_generic_export_scope_ids_and_status():
    with TestClient(app) as c:
        headers = _login(c)
        tasks = c.get("/api/v1/tasks/", params={"limit": 3}, headers=headers).json()["data"]
        assert tasks, "seed harus punya task"
        wanted = [t["id"] for t in tasks[:2]]
        res = c.get("/api/v1/exports.csv", params={"table": "tasks", "ids": ",".join(wanted)}, headers=headers)
        assert res.status_code == 200
        # Hanya id terpilih yang ikut (baris = header + 2).
        lines = [l for l in res.text.strip().splitlines() if l]
        assert len(lines) == 1 + len(wanted)
        assert "selected-2" in res.headers["content-disposition"]

        # Filter status menyempitkan hasil dan memberi nama berkas ber-scope.
        first_status = tasks[0]["status"]
        f = c.get("/api/v1/exports.csv", params={"table": "tasks", "status": first_status}, headers=headers)
        assert f.status_code == 200
        assert "tasks-" in f.headers["content-disposition"]


def test_module_export_accepts_scope_params():
    with TestClient(app) as c:
        headers = _login(c)
        res = c.get("/api/v1/orders/export.csv", params={"status": "Draft"}, headers=headers)
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]


# ---------------------------------------------------------------------------
# PRD FR-ADMIN-1: admin HS codes feed the runtime search pipeline
# ---------------------------------------------------------------------------
def test_admin_hs_code_becomes_searchable():
    with TestClient(app) as c:
        headers = _login(c)
        code = "99999999"
        created = c.post("/api/v1/hs-codes/", json={
            "hs_code": code, "description": "Uji komoditas ekspor khusus",
            "section": "I", "keywords": ["uji", "komoditas", "khusus"],
        }, headers=headers)
        assert created.status_code == 200
        # Langsung muncul di detail publik.
        detail = c.get(f"/api/v1/hs-codes/{code}/", headers=headers)
        assert detail.status_code == 200
        assert detail.json()["data"]["hs_code"] == code
        # Dan di autocomplete.
        auto = c.get("/api/v1/hs-codes/autocomplete/", params={"q": code}, headers=headers)
        assert any(r["hs_code"] == code for r in auto.json()["data"])


def test_admin_hs_code_rejects_non_numeric():
    with TestClient(app) as c:
        headers = _login(c)
        res = c.post("/api/v1/hs-codes/", json={"hs_code": "ABC", "description": "x", "section": "I"}, headers=headers)
        assert res.status_code == 422


# ---------------------------------------------------------------------------
# PRD G-16: upload magic-byte validation & safe storage names
# ---------------------------------------------------------------------------
def test_upload_rejects_extension_mismatch():
    with TestClient(app) as c:
        headers = _login(c)
        # .png dengan isi teks → ditolak (magic bytes tidak cocok).
        res = c.post(
            "/api/v1/files/upload/",
            files={"file": ("logo.png", b"not an image", "image/png")},
            data={"type": "Image"},
            headers=headers,
        )
        assert res.status_code == 400
        assert "tidak" in res.text.lower()


def test_upload_accepts_real_png_and_stores_uuid_name():
    import base64
    with TestClient(app) as c:
        headers = _login(c)
        png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mPgYQAAAAMAAeVZK6kAAAAASUVORK5CYII="
        )
        res = c.post(
            "/api/v1/files/upload/",
            files={"file": ("dot.png", png, "image/png")},
            data={"type": "Image"},
            headers=headers,
        )
        assert res.status_code == 200, res.text
        name = res.json()["data"]["storageName"]
        # Nama penyimpanan acak (UUID hex) + ekstensi, bukan timestamp+nama asli.
        assert name.endswith(".png")
        assert "dot" not in name
        assert len(name.split(".")[0]) == 32


def test_upload_rejects_unsupported_extension():
    with TestClient(app) as c:
        headers = _login(c)
        res = c.post(
            "/api/v1/files/upload/",
            files={"file": ("evil.exe", b"MZ\x90\x00", "application/octet-stream")},
            data={"type": "Document"},
            headers=headers,
        )
        assert res.status_code == 400
