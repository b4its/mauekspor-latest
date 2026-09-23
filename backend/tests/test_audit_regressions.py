"""Regresi audit: RBAC module-names, login email casing, self-service profiles,
lockout tidak terhapus oleh 429, dan validasi rate exchange."""
from fastapi.testclient import TestClient

from app.main import app

ADMIN = ("admin@mauekspor.example", "admin123")
EXPORTER = ("rizal@kopigayo.example", "rizal123")
BUYER = ("aya@hikari.example", "buyer123")


def _login(c: TestClient, creds: tuple[str, str] = ADMIN) -> str:
    res = c.post("/api/v1/auth/login/", json={"email": creds[0], "password": creds[1]})
    assert res.status_code == 200, res.text
    return res.json()["meta"]["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_exporter_can_mutate_module_names_from_routes():
    """MUTATE_MODULES memakai 'business-profile'/'rfq' (singular) sedangkan path
    aktual '/business-profiles/' dan '/rfqs/' -> Exporter selalu 403. Regresi."""
    with TestClient(app) as c:
        token = _login(c, EXPORTER)
        r = c.post(
            "/api/v1/rfqs/",
            json={"projectId": "", "productId": "PRD-COF-001", "buyerName": "X",
                  "destination": "JP", "quantity": "1", "deadline": "2026-12-01"},
            headers=_auth(token),
        )
        assert r.status_code == 200, r.text
        r = c.post("/api/v1/business-profiles/", json={"companyName": "PT Uji"}, headers=_auth(token))
        assert r.status_code == 200, r.text
        r = c.post("/api/v1/analytics/refresh/", headers=_auth(token))
        assert r.status_code == 200, r.text


def test_login_email_case_insensitive():
    with TestClient(app) as c:
        reg = c.post("/api/v1/auth/register/", json={
            "email": "MiXeD.CaSe@Example.COM", "password": "Password123!", "name": "Mixed",
        })
        assert reg.status_code == 200, reg.text
        # login dengan casing berbeda harus berhasil (register lowercases, login
        # sebelumnya exact-match)
        ok = c.post("/api/v1/auth/login/", json={"email": "mixed.case@example.com", "password": "Password123!"})
        assert ok.status_code == 200, ok.text
        ok2 = c.post("/api/v1/auth/login/", json={"email": "MiXeD.CaSe@Example.COM", "password": "Password123!"})
        assert ok2.status_code == 200, ok2.text


def test_login_unknown_user_without_password_no_500():
    """User admin-made tanpa field password -> login sebelumnya KeyError 500."""
    from app import db
    with TestClient(app) as c:
        c.get("/api/v1/health")
        db.insert("users", {"id": "U-NOPW", "email": "nopass@example.com", "role": "Exporter", "fullName": "NP"})
        res = c.post("/api/v1/auth/login/", json={"email": "nopass@example.com", "password": "whatever"})
        assert res.status_code == 401, res.text


def test_buyer_can_save_own_profile_but_not_crm():
    with TestClient(app) as c:
        token = _login(c, BUYER)
        saved = c.post(
            "/api/v1/buyers/profile/",
            json={"companyName": "Hikari Foods Co.", "sourceCountries": ["Japan"]},
            headers=_auth(token),
        )
        assert saved.status_code == 200, saved.text
        me = c.get("/api/v1/buyers/profile/me/", headers=_auth(token))
        assert me.status_code == 200
        # Tetapi CRM buyers (tabel milik exporter) tetap tertutup untuk Buyer
        crm = c.post("/api/v1/buyers/", json={"name": "Fake", "country": "XX", "segment": "S", "interestedProducts": []}, headers=_auth(token))
        assert crm.status_code == 403, crm.text


def test_update_buyer_profile_ownership_enforced():
    """PUT /buyers/profile/{id}/ sebelumnya tanpa auth/ownership (IDOR)."""
    from app import db
    with TestClient(app) as c:
        c.get("/api/v1/health")
        db.insert("buyer_profiles", {
            "id": "BYP-OTHER", "userId": "U-999", "company_name": "Korban",
            "source_countries": ["ID"], "createdAt": "now",
        })
        token = _login(c, BUYER)  # U-003
        r = c.put("/api/v1/buyers/profile/BYP-OTHER/", json={"companyName": "Hacked"}, headers=_auth(token))
        assert r.status_code == 403, r.text


def test_anon_cannot_create_buyer_profile():
    with TestClient(app) as c:
        r = c.post("/api/v1/buyers/profile/", json={"companyName": "Anon"})
        assert r.status_code == 401, r.text


def test_login_lockout_survives_rate_limit_burst():
    """429 dari limiter tidak boleh menghapus计数器 kegagalan login."""
    from app import main as app_main
    with TestClient(app) as c:
        # bersihkan state
        app_main._login_failures.clear()
        app_main._ratelimit.clear()
        ident = "test-ident"
        for _ in range(10):
            app_main._record_login_failure(ident)
        assert app_main._is_locked_out(ident) is True
        resp = c.post("/api/v1/auth/login/", json={"email": "x@y.z", "password": "bad"})
        if resp.status_code == 401:
            assert app_main._is_locked_out(ident) is True, "lockout harus bertahan setelah 401"
        # 429 (bukan 401/sukses) tidak boleh clear
        app_main._clear_login_failures(ident)
        for _ in range(10):
            app_main._record_login_failure(ident)
        # Simulasi: respons 429 tidak memanggil clear (regresi bug lama)
        assert app_main._is_locked_out(ident) is True
        app_main._login_failures.clear()
        app_main._ratelimit.clear()


def test_exchange_rate_rejects_garbage_and_negative():
    with TestClient(app) as c:
        token = _login(c, ADMIN)
        assert c.put("/api/v1/costing/exchange-rate/", json={"rate": "abc"}, headers=_auth(token)).status_code == 422
        assert c.put("/api/v1/costing/exchange-rate/", json={"rate": -100}, headers=_auth(token)).status_code == 422
        assert c.put("/api/v1/costing/exchange-rate/", json={"rate": 15800}, headers=_auth(token)).status_code == 200
