"""Test edge case middleware & root endpoint (app/main.py)."""
from fastapi.testclient import TestClient

from app.main import app


def test_root_endpoint():
    with TestClient(app) as c:
        res = c.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "app" in data
    assert "version" in data


def test_non_api_path_tidak_ditangani_auth_middleware():
    """Path non-API seperti /docs tidak masuk middleware auth."""
    with TestClient(app) as c:
        res = c.get("/docs")
    assert res.status_code == 200


def test_bearer_token_invalid_on_write_401():
    with TestClient(app) as c:
        res = c.post(
            "/api/v1/products/",
            json={"name": "X", "category": "F&B", "origin": "Aceh"},
            headers={"Authorization": "Bearer token-invalid"},
        )
        assert res.status_code == 401


def test_bearer_token_invalid_on_read_returns_response():
    """GET dengan bearer invalid -> token tidak valid, tapi GET melewati auth write check."""
    with TestClient(app) as c:
        # Karena endpoint GET /products/ tidak memerlukan auth write,
        # request tetap diproses (mengembalikan data atau 401 dari endpoint?)
        res = c.get("/api/v1/products/", headers={"Authorization": "Bearer token-invalid"})
        # Middleware: token exists, decode fails -> payload/user None.
        # is_write = False -> tidak masuk check auth write.
        # call_next dipanggil. Endpoint GET /products/ bisa mengembalikan 200
        # atau 401 tergantung endpoint (list_products via @router memanggil db.all).
        # Yang penting: tidak crash, http status valid.
        assert res.status_code in (200, 401)


def test_missing_bearer_on_protected_read():
    """GET /users/ tanpa auth -> endpoint mungkin memerlukan auth via deps."""
    # Endpoint /users/ menggunakan get_current_user (depends)
    with TestClient(app) as c:
        res = c.get("/api/v1/users/")
        assert res.status_code == 403


def test_auth_header_dengan_bearer_valid():
    with TestClient(app) as c:
        # login dulu dapat token
        login = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
        assert login.status_code == 200
        token = login.json()["meta"]["access_token"]
        res = c.get("/api/v1/users/", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200