"""Pembungkus respons dan error yang konsisten dengan kontrak frontend."""
from typing import Any

from fastapi import HTTPException
from fastapi.responses import JSONResponse


def ok(data: Any, meta: dict | None = None) -> dict:
    return {"data": data, "meta": meta or {}}


def created(data: Any, meta: dict | None = None) -> dict:
    return ok(data, meta)


def not_found(message: str = "Resource not found") -> None:
    raise HTTPException(status_code=404, detail=message)


def api_error_response(message: str, status_code: int = 400, errors: Any = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"message": message, "errors": errors})