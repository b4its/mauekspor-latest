"""Test helpers respons API (app/api/responses.py)."""
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from app.api.responses import api_error_response, created, not_found, ok


def test_ok_membungkus_data():
    body = ok({"id": "X"})
    assert body == {"data": {"id": "X"}, "meta": {}}


def test_ok_dengan_meta():
    body = ok([1], meta={"count": 1})
    assert body["meta"]["count"] == 1


def test_created_sama_dengan_ok():
    assert created({"id": "Y"}) == ok({"id": "Y"})


def test_not_found_melempar_404_default():
    try:
        not_found()
    except HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "Resource not found"
    else:
        raise AssertionError("harus melempar HTTPException")


def test_not_found_pesan_kustom():
    try:
        not_found("Product not found")
    except HTTPException as exc:
        assert exc.detail == "Product not found"
    else:
        raise AssertionError("harus melempar HTTPException")


def test_api_error_response_format():
    resp = api_error_response("Terjadi error", status_code=422, errors={"field": ["required"]})
    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 422
    import json

    body = json.loads(resp.body)
    assert body["message"] == "Terjadi error"
    assert body["errors"]["field"] == ["required"]
