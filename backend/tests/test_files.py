"""Test upload file nyata (multipart) + download."""

import contextlib
import os
import shutil

from io import BytesIO

from fastapi.testclient import TestClient

from app.api.routes import UPLOAD_DIR
from app.main import app


@contextlib.contextmanager
def _client():
    with TestClient(app) as c:
        c.post(
            "/api/v1/auth/login/",
            json={"email": "admin@mauekspor.example", "password": "admin123"},
        )
        yield c


def test_upload_binary_file():
    with _client() as c:
        files = {"file": ("invoice.pdf", BytesIO(b"%PDF-1.4 fake content"), "application/pdf")}
        data = {"type_": "Document", "project_id": "EXP-2408-017", "tags": "invoice, japan"}
        res = c.post("/api/v1/files/upload/", files=files, data=data)
        assert res.status_code == 200
        asset = res.json()["data"]
        assert asset["name"] == "invoice.pdf"
        assert asset["size"].endswith("KB")
        assert asset["contentType"] == "application/pdf"
        assert asset["tags"] == ["invoice", "japan"]
        assert asset["status"] == "Needs Review"

        dl = c.get(f"/api/v1/files/{asset['id']}/download/")
        assert dl.status_code == 200
        assert dl.content == b"%PDF-1.4 fake content"
        assert dl.headers["content-type"] == "application/pdf"
        shutil.rmtree(UPLOAD_DIR, ignore_errors=True)


def test_upload_empty_file_rejected():
    with _client() as c:
        files = {"file": ("empty.pdf", BytesIO(b""), "application/pdf")}
        res = c.post("/api/v1/files/upload/", files=files, data={"type_": "Document"})
        assert res.status_code == 400


def test_download_file_missing_disk_404():
    with _client() as c:
        res = c.get("/api/v1/files/FIL-CI-JP/download/")
        assert res.status_code == 404