"""Regression tests: CORS preflight (OPTIONS) must succeed for every API module.

The auth middleware in app/main.py originally blocked OPTIONS preflight to
admin-only modules (settings, users, audit, api-keys) with 403 before the CORS
middleware could attach Access-Control-Allow-Origin. In-browser this surfaces as
"No 'Access-Control-Allow-Origin' header is present" and breaks those pages.
Preflight requests must always be forwarded to the CORS middleware.
"""

import os
import tempfile

from fastapi.testclient import TestClient

with tempfile.TemporaryDirectory() as tmpdir:
    os.environ["MAUEKSPOR_DATA_DIR"] = tmpdir
    os.environ["MAUEKSPOR_AI_MODE"] = "mock"

    from app.main import app  # noqa: E402


def _preflight(path: str, request_method: str = "GET"):
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["MAUEKSPOR_DATA_DIR"] = tmpdir
        os.environ["MAUEKSPOR_AI_MODE"] = "mock"
        with TestClient(app) as client:
            return client.options(
                path,
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": request_method,
                },
            )


def test_preflight_admin_only_modules_allowed():
    for module in ("settings", "users", "audit", "api-keys"):
        r = _preflight(f"/api/v1/{module}/")
        assert r.status_code == 200, f"preflight /{module}/ should pass, got {r.status_code}"
        assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_preflight_regular_modules_allowed():
    for module in ("chat/sessions", "products", "buyers", "countries"):
        r = _preflight(f"/api/v1/{module}/", request_method="POST")
        assert r.status_code == 200, f"preflight /{module}/ should pass, got {r.status_code}"
        assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_auth_error_responses_carry_cors_headers():
    """401/403 produced by the auth middleware must still carry CORS headers.

    CORSMiddleware must wrap (be registered after) the auth middleware so that
    even short-circuited responses (401 unauth write, 403 admin-only read) are
    readable by the browser instead of triggering a confusing CORS error.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["MAUEKSPOR_DATA_DIR"] = tmpdir
        os.environ["MAUEKSPOR_AI_MODE"] = "mock"
        with TestClient(app) as client:
            r = client.post(
                "/api/v1/chat/sessions/",
                json={},
                headers={"Origin": "http://localhost:3000"},
            )
            assert r.status_code == 401
            assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"

            r = client.get(
                "/api/v1/settings/",
                headers={"Origin": "http://localhost:3000"},
            )
            assert r.status_code == 403
            assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"
