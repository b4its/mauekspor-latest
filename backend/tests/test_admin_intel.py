"""Cakupan lengkap fitur Admin: negara & regulasi (CRUD + import CSV) dan diagnostik AI."""
import io

from fastapi.testclient import TestClient

from app.main import app


def _login(c: TestClient) -> str:
    res = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
    assert res.status_code == 200
    return res.json()["meta"]["access_token"]


def _register_viewer(c: TestClient) -> str:
    res = c.post(
        "/api/v1/auth/register/",
        json={"name": "Viewer", "email": "viewer-intel@example.com", "password": "viewer123", "role": "Exporter"},
    )
    if res.status_code in (200, 201):
        login = c.post("/api/v1/auth/login/", json={"email": "viewer-intel@example.com", "password": "viewer123"})
        assert login.status_code == 200
        return login.json()["meta"]["access_token"]
    login = c.post("/api/v1/auth/login/", json={"email": "viewer-intel@example.com", "password": "viewer123"})
    assert login.status_code == 200
    return login.json()["meta"]["access_token"]


def test_admin_country_full_lifecycle():
    with TestClient(app) as c:
        token = _login(c)
        headers = {"Authorization": f"Bearer {token}"}

        created = c.post(
            "/api/v1/admin/countries/",
            json={"country_code": "QZ", "country_name": "Qzlandia", "region": "Test Region"},
            headers=headers,
        )
        assert created.status_code == 200
        body = created.json()["data"]
        assert body["country_code"] == "QZ"
        assert body["country_name"] == "Qzlandia"
        assert body["region"] == "Test Region"

        dup = c.post(
            "/api/v1/admin/countries/",
            json={"country_code": "QZ", "country_name": "Duplikat"},
            headers=headers,
        )
        assert dup.status_code == 409

        updated = c.put(
            "/api/v1/admin/countries/QZ/",
            json={"country_name": "Qzlandia Baru", "region": "Region Ubah"},
            headers=headers,
        )
        assert updated.status_code == 200
        assert updated.json()["data"]["country_name"] == "Qzlandia Baru"

        listing = c.get("/api/v1/countries/")
        assert listing.status_code == 200
        qz = next((x for x in listing.json()["data"] if x["country_code"] == "QZ"), None)
        assert qz is not None
        assert qz["country_name"] == "Qzlandia Baru"

        deleted = c.delete("/api/v1/admin/countries/QZ/delete/", headers=headers)
        assert deleted.status_code == 200

        gone = c.put("/api/v1/admin/countries/QZ/", json={"country_name": "Hilang"}, headers=headers)
        assert gone.status_code == 404


def test_admin_regulation_update_filter_delete():
    with TestClient(app) as c:
        token = _login(c)
        headers = {"Authorization": f"Bearer {token}"}
        c.post(
            "/api/v1/admin/countries/",
            json={"country_code": "QY", "country_name": "Qyland", "region": "Test"},
            headers=headers,
        )

        reg = c.post(
            "/api/v1/admin/countries/QY/regulations/create/",
            json={
                "rule_category": "Labeling",
                "forbidden_keywords": "racun",
                "required_specs": "label dwibahasa",
                "description_rule": "Aturan label uji.",
            },
            headers=headers,
        )
        assert reg.status_code == 200
        reg_id = reg.json()["data"]["id"]
        assert reg.json()["data"]["forbidden_keywords"] == "racun"

        listed = c.get("/api/v1/admin/countries/QY/regulations/", headers=headers)
        assert listed.status_code == 200
        assert any(r["id"] == reg_id for r in listed.json()["data"])

        filtered = c.get("/api/v1/admin/countries/QY/regulations/?rule_category=Customs", headers=headers)
        assert filtered.status_code == 200
        assert all(r["rule_category"] == "Customs" for r in filtered.json()["data"])

        updated = c.put(
            f"/api/v1/admin/regulations/{reg_id}/",
            json={
                "rule_category": "Customs",
                "forbidden_keywords": "dilarang",
                "required_specs": "sertifikat halal",
                "description_rule": "Aturan bea cukai uji.",
            },
            headers=headers,
        )
        assert updated.status_code == 200
        data = updated.json()["data"]
        assert data["rule_category"] == "Customs"
        assert data["forbidden_keywords"] == "dilarang"
        assert data["required_specs"] == "sertifikat halal"

        res = c.delete(f"/api/v1/admin/regulations/{reg_id}/delete/", headers=headers)
        assert res.status_code == 200

        missing = c.put(
            "/api/v1/admin/regulations/REG-tidak-ada/",
            json={"rule_category": "Labeling"},
            headers=headers,
        )
        assert missing.status_code == 404


def test_admin_import_regulations_csv():
    with TestClient(app) as c:
        token = _login(c)
        headers = {"Authorization": f"Bearer {token}"}
        c.post(
            "/api/v1/admin/countries/",
            json={"country_code": "QX", "country_name": "Qxland", "region": "Test"},
            headers=headers,
        )

        csv_content = (
            "country_code,rule_category,forbidden_keywords,required_specs,description_rule\n"
            "QX,Labeling,formalin,label kedaluwarsa,Aturan label QX.\n"
            "QX,Customs,pemutih,COO asli,Aturan bea cukai QX.\n"
        )
        res = c.post(
            "/api/v1/admin/regulations/import/",
            files={"file": ("regulasi.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")},
            headers=headers,
        )
        assert res.status_code == 200
        assert res.json()["data"]["imported"] == 2

        listed = c.get("/api/v1/admin/countries/QX/regulations/", headers=headers)
        cats = {r["rule_category"] for r in listed.json()["data"]}
        assert {"Labeling", "Customs"}.issubset(cats)


def test_admin_intel_rbac_non_admin_ditolak():
    with TestClient(app) as c:
        token = _register_viewer(c)
        headers = {"Authorization": f"Bearer {token}"}

        assert c.post("/api/v1/admin/countries/", json={"country_code": "QQ", "country_name": "Q"}, headers=headers).status_code == 403
        assert c.put("/api/v1/admin/countries/QQ/", json={"country_name": "Q"}, headers=headers).status_code == 403
        assert c.delete("/api/v1/admin/countries/QQ/delete/", headers=headers).status_code == 403
        assert c.get("/api/v1/admin/countries/QQ/regulations/", headers=headers).status_code == 403
        assert c.post("/api/v1/admin/countries/QQ/regulations/create/", json={"rule_category": "Labeling"}, headers=headers).status_code == 403
        assert c.put("/api/v1/admin/regulations/XYZ/", json={"rule_category": "Labeling"}, headers=headers).status_code == 403
        assert c.delete("/api/v1/admin/regulations/XYZ/delete/", headers=headers).status_code == 403
        assert c.post("/api/v1/admin/regulations/import/", files={"file": ("a.csv", io.BytesIO(b"a,b\n1,2"), "text/csv")}, headers=headers).status_code == 403


def test_ai_status_and_test_endpoints():
    with TestClient(app) as c:
        token = _login(c)
        headers = {"Authorization": f"Bearer {token}"}

        status = c.get("/api/v1/ai/status/", headers=headers)
        assert status.status_code == 200
        data = status.json()["data"]
        assert data["mode"] in ("mock", "remote", "localhost")
        assert "health" in data
        assert "circuit_breaker" in data

        test = c.post("/api/v1/ai/test/", headers=headers)
        assert test.status_code == 200
        payload = test.json()["data"]
        assert payload["success"] is True
        assert isinstance(payload["response"], str) and payload["response"]
        assert payload["ai_mode"] in ("mock", "remote", "localhost")
