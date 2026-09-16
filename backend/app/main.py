from contextlib import asynccontextmanager
from datetime import datetime, timezone

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
    version=settings.api_version,
    lifespan=lifespan,
    default_response_class=JSONResponse,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _actor_from_cookie(request) -> str:
    token = request.cookies.get("access_token")
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
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.status_code, str(exc.detail)),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = {}
    for e in exc.errors():
        loc = e.get("loc", ())
        field = str(loc[-1]) if loc else "body"
        errors.setdefault(field, [])
        errors[field].append(e.get("msg", "invalid"))
    return JSONResponse(
        status_code=422,
        content=_error_body(422, "Validation error", errors),
    )


app.include_router(router)


@app.get("/")
def root():
    return {"app": settings.app_name, "version": settings.api_version, "docs": "/docs"}
