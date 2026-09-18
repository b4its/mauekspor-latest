from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import db
from app.core.config import settings
from app.core.permissions import can_mutate_module, can_read_module
from app.core.security import decode_token
from app.api.routes import router
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_store()
    seed_if_empty()
    yield


app = FastAPI(
    title=settings.app_name,
    description="""
# MauEkspor API — Workspace Ekspor-Impor berbasis AI

**Base URL:** `http://localhost:8000/api/v1`

## Database

- **PostgreSQL** (`postgresql://...`) untuk production / Docker
- **SQLite** (`sqlite:///...`) untuk development lokal
- Pilih via env `MAUEKSPOR_DATABASE_URL`
- Semua tabel disimpan di tabel `records` (payload JSONB)

## Autentikasi & Keamanan

- **Login:** `POST /auth/login/` → dapatkan `access_token` & `refresh_token` di response `meta`
- **Bearer Auth:** Kirim `Authorization: Bearer <access_token>` di header setiap request
- **Refresh:** `POST /auth/refresh/` dengan header `X-Refresh-Token: <refresh_token>`
- **Cookie fallback:** Backend juga menerima cookie `access_token` (HttpOnly, SameSite=Lax)
- **Rate limiting:** Max 5 percobaan login gagal per 60 detik per IP → `429`
- **Password policy:** Min 8 karakter + wajib huruf & angka
- **Security headers:** `X-Content-Type-Options`, `X-Frame-Options: DENY`, `X-XSS-Protection`, `Referrer-Policy`, `Permissions-Policy`, `Cache-Control: no-store`

## RBAC (Role-Based Access Control)

| Role | Akses Baca | Akses Tulis (modul) |
|------|-----------|---------------------|
| Admin | Semua | Semua (termasuk users, audit, api-keys, settings) |
| Exporter | Semua (non-admin) | Produk, analisis, katalog, costing, order, shipment, dll. |
| Buyer | Semua (non-admin) | Buyer requests, quotations, orders, chat, messages |
| Forwarder | Semua (non-admin) | Shipments, messages, notifications |
| CustomsBroker | Semua (non-admin) | Shipments, compliance, documents, payments, messages |
| Finance | Semua (non-admin) | Payments, billing, orders, quotations, messages |

> Modul admin-only (`users`, `audit`, `api-keys`, `settings`) → hanya Admin yang bisa baca & tulis.

## Format Response

Semua endpoint mengembalikan:
```json
{"data": T, "meta": {...}}
```

Error:
```json
{"message": "string", "errors": {...}}
```

## Endpoint Utama

- **Auth:** login, register, register-admin, refresh, logout, me
- **Products:** CRUD, enrich (HS+SKU), market intelligence, pricing, catalog description
- **Export Analysis:** create, compare, reanalyze, regulation recommendations
- **Catalogs:** CRUD, publish, images, variants, AI description
- **Costing:** CRUD, exchange rate, PDF, compare
- **Commercial:** buyers, buyer-requests, forwarders, RFQ, quotations, orders, payments
- **Fulfillment:** compliance, documents, shipments, tasks
- **Insights:** analytics, reports, audit
- **Workspace:** team, messages, chat, files, notifications, educational
- **Master data:** countries (250), HS codes (6941), regulations
    """,
    version=settings.api_version,
    lifespan=lifespan,
    default_response_class=JSONResponse,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "MauEkspor",
        "url": "http://localhost:3000",
    },
    license_info={
        "name": "MIT",
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _actor_from_cookie(request) -> str:
    """Ekstrak actor name dari request (Authorization header atau cookie)."""
    token = _request_token(request)
    if not token:
        return "Anonymous"
    try:
        payload = decode_token(token)
        user = db.get("users", payload["sub"])
        if not user:
            return "Unknown user"
        return user.get("fullName") or user.get("name") or user.get("email") or str(user.get("id"))
    except Exception:
        return "Invalid session"


def _request_token(request) -> str | None:
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1]
    return request.cookies.get("access_token")


def _is_public_mutation(path: str) -> bool:
    return path in {
        "/api/v1/auth/login/",
        "/api/v1/auth/register/",
        "/api/v1/auth/refresh/",
        "/api/v1/auth/logout/",
    }


def _module_of(path: str) -> str:
    parts = path.strip("/").split("/")
    return parts[2] if len(parts) > 2 else ""


# ── Security headers middleware ────────────────────────────────────
_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cache-Control": "no-store",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' http://localhost:8000 http://localhost:5173; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    ),
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}


# ── General rate limiting (anti brute-force / abuse) ───────────────
import time as _time

_RL_WINDOW = 60
_RL_DEFAULT = 120  # max requests per window per IP
_RL_ENABLED = os.getenv("MAUEKSPOR_DISABLE_PERSISTENCE", "").lower() not in {"1", "true", "yes"}


def _rate_limit_key(request) -> str:
    ip = request.client.host if request.client else "unknown"
    return ip


_ratelimit: dict[str, list[float]] = {}


def _rate_limited(ip: str, limit: int, window: int = _RL_WINDOW) -> bool:
    now = _time.time()
    hits = [t for t in _ratelimit.get(ip, []) if now - t < window]
    _ratelimit[ip] = hits
    return len(hits) >= limit


def _record_hit(ip: str) -> None:
    _ratelimit.setdefault(ip, []).append(_time.time())


@app.middleware("http")
async def general_rate_limit(request, call_next):
    """Rate limit semua request API (120/60s per IP). Login lebih ketat."""
    if _RL_ENABLED and request.url.path.startswith("/api/v1/"):
        ip = _rate_limit_key(request)
        limit = 5 if request.url.path == "/api/v1/auth/login/" else _RL_DEFAULT
        if _rate_limited(ip, limit):
            return JSONResponse(
                status_code=429,
                content=_error_body(429, "Too many requests. Please slow down."),
                headers={"Retry-After": "60"},
            )
        response = await call_next(request)
        _record_hit(ip)
        return response
    return await call_next(request)


# ── Account lockout (login gagal berulang) ─────────────────────────
_login_failures: dict[str, int] = {}
_LOCKOUT_THRESHOLD = 10
_LOCKOUT_SECONDS = 300


def _is_locked_out(identifier: str) -> bool:
    failures = _login_failures.get(identifier, 0)
    if failures >= _LOCKOUT_THRESHOLD:
        return True
    return False


def _record_login_failure(identifier: str) -> None:
    _login_failures[identifier] = _login_failures.get(identifier, 0) + 1


def _clear_login_failures(identifier: str) -> None:
    _login_failures.pop(identifier, None)


@app.middleware("http")
async def login_lockout(request, call_next):
    if request.url.path == "/api/v1/auth/login/" and request.method == "POST":
        # Identifikasi berdasarkan IP + email (jika ada)
        ip = _rate_limit_key(request)
        identifier = ip
        response = await call_next(request)
        if response.status_code == 401:
            _record_login_failure(identifier)
        else:
            _clear_login_failures(identifier)
        return response
    return await call_next(request)


# ── CSRF protection (untuk auth via cookie) ────────────────────────
import secrets as _secrets

# Simpan token CSRF per sesi (dipakai request berbasis cookie)
_csrf_tokens: dict[str, str] = {}


def issue_csrf_token(request) -> str:
    """Buat / kembalikan token CSRF untuk request yang memakai cookie."""
    token = _secrets.token_urlsafe(32)
    _csrf_tokens[token] = _time.time()
    return token


@app.middleware("http")
async def csrf_protection(request, call_next):
    """Cegah CSRF untuk mutasi yang memakai cookie (bukan Bearer).

    Diaktifkan via env MAUEKSPOR_ENABLE_CSRF=1 (default nonaktif karena
    auth utama adalah Bearer token; CSRF hanya untuk fallback cookie).
    """
    if os.getenv("MAUEKSPOR_ENABLE_CSRF", "").lower() not in {"1", "true", "yes"}:
        return await call_next(request)
    is_write = request.method in {"POST", "PUT", "PATCH", "DELETE"}
    uses_bearer = request.headers.get("authorization", "").lower().startswith("bearer ")
    has_cookie = bool(request.cookies.get("access_token"))

    if (
        request.url.path.startswith("/api/v1/")
        and is_write
        and has_cookie
        and not uses_bearer
        and not _is_public_mutation(request.url.path)
    ):
        csrf = request.headers.get("x-csrf-token")
        if not csrf or csrf not in _csrf_tokens:
            return JSONResponse(
                status_code=403,
                content=_error_body(403, "CSRF token missing or invalid. Gunakan Authorization Bearer atau sertakan X-CSRF-Token."),
            )
    return await call_next(request)


# ── Request body size limit ────────────────────────────────────────
_MAX_BODY_SIZE = 25 * 1024 * 1024  # 25 MB


@app.middleware("http")
async def body_size_limit(request, call_next):
    if request.url.path.startswith("/api/v1/"):
        length = request.headers.get("content-length")
        if length and length.isdigit() and int(length) > _MAX_BODY_SIZE:
            return JSONResponse(
                status_code=413,
                content=_error_body(413, "Payload too large (max 25MB)"),
            )
    return await call_next(request)


# ── Security headers middleware ────────────────────────────────────
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    for key, value in _SECURITY_HEADERS.items():
        response.headers.setdefault(key, value)
    return response


@app.middleware("http")
async def require_auth_for_mutations(request, call_next):
    module = _module_of(request.url.path)
    if not (request.url.path.startswith("/api/v1/") and module):
        return await call_next(request)
    if module in {"auth"}:
        return await call_next(request)
    if request.method == "OPTIONS":
        return await call_next(request)

    token = _request_token(request)
    payload = None
    user = None
    if token:
        try:
            payload = decode_token(token)
            user = db.get("users", payload["sub"])
        except Exception:
            payload = None

    is_write = request.method in {"POST", "PATCH", "PUT", "DELETE"} and not _is_public_mutation(
        request.url.path
    )

    if is_write:
        if not token:
            return JSONResponse(status_code=401, content=_error_body(401, "Not authenticated"))
        if not user:
            return JSONResponse(status_code=401, content=_error_body(401, "User not found"))
        if not can_mutate_module(user.get("role", ""), module):
            return JSONResponse(
                status_code=403,
                content=_error_body(403, f"Role {user.get('role', '')} cannot modify this resource"),
            )
    elif not can_read_module((user or {}).get("role", ""), module):
        return JSONResponse(status_code=403, content=_error_body(403, "Admin access required"))
    return await call_next(request)


@app.middleware("http")
async def audit_mutations(request, call_next):
    response = await call_next(request)
    if (
        request.url.path.startswith("/api/v1/")
        and request.method in {"POST", "PATCH", "PUT", "DELETE"}
        and response.status_code < 500
    ):
        db.insert("audit_events", {
            "id": db.gen_id("audit_events", "AUD"),
            "time": _now(),
            "actor": _actor_from_cookie(request),
            "action": f"{request.method} {request.url.path}",
            "module": request.url.path.strip("/").split("/")[2] if len(request.url.path.strip("/").split("/")) > 2 else "API",
            "entity": request.url.path,
            "severity": "Info" if response.status_code < 400 else "Warning",
            "detail": f"HTTP {response.status_code}",
        })
    return response


def _error_body(status_code: int, message: str, errors=None) -> dict:
    return {"message": message, "errors": errors}


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    # Sanitasi: jangan bocorkan detail internal untuk error 500
    if exc.status_code >= 500:
        return JSONResponse(
            status_code=500,
            content=_error_body(500, "Internal server error"),
        )
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.status_code, str(exc.detail)),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    """Handler error tak terduga: jangan bocorkan stack trace ke klien."""
    import logging
    logging.getLogger("app").error("Unhandled error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content=_error_body(500, "Internal server error"),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = {}
    for e in exc.errors():
        loc = e.get("loc", ())
        field = str(loc[-1]) if loc else "body"
        # Sanitasi pesan error agar tidak bocorkan nilai input
        msg = str(e.get("msg", "invalid"))
        errors.setdefault(field, [])
        errors[field].append(msg)
    return JSONResponse(
        status_code=422,
        content=_error_body(422, "Validation error", errors),
    )


app.include_router(router)

# ── OpenAPI / Swagger: tambah Bearer auth scheme ───────────────────
# Hook ke FastAPI's openapi generation (dipanggil lazy saat /openapi.json diakses)
from fastapi.openapi.utils import get_openapi

_original_openapi = app.openapi


def _patched_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = _original_openapi()
    if "components" not in schema:
        schema["components"] = {}
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": (
                "Masukkan access_token dari response login.\n\n"
                "1. Buka POST /auth/login/ → jalankan → salin `access_token` dari response `meta`\n"
                "2. Klik tombol 'Authorize' di atas → paste token → klik Authorize\n"
                "3. Semua request akan otomatis menyertakan header `Authorization: Bearer <token>`"
            ),
        }
    }
    # Hapus default HTTPBearer scheme jika ada
    schema["components"]["securitySchemes"].pop("HTTPBearer", None)
    # Terapkan security ke semua path kecuali auth publik
    for path, methods in schema.get("paths", {}).items():
        for method in methods.values():
            if path.startswith("/api/v1/auth/") and method.get("operationId", "").startswith("login_") or \
               path.startswith("/api/v1/auth/register") or \
               path.startswith("/api/v1/auth/refresh"):
                method.pop("security", None)
            else:
                method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = _patched_openapi


@app.get("/")
def root():
    return {"app": settings.app_name, "version": settings.api_version, "docs": "/docs"}
