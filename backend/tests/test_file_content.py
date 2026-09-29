"""Test pratinjau isi berkas & analisis AI (fitur "Analisa file ini").

Menguji ekstraksi isi untuk spreadsheet (.xlsx/.csv), dokumen (.docx),
presentasi (.pptx), serta endpoint preview/analyze. Berkas OOXML dibangun
on-the-fly memakai zipfile agar tidak menambah fixture biner ke repo.
"""

import csv
import contextlib
import io
import zipfile

from fastapi.testclient import TestClient

from app.main import app
from app.services import file_content


# ── Pembuat berkas OOXML minimal ──────────────────────────────────────────────
def _make_xlsx() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "xl/sharedStrings.xml",
            '<?xml version="1.0"?><sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            "<si><t>Produk</t></si><si><t>Kopi Gayo</t></si><si><t>Negara</t></si><si><t>Jepang</t></si></sst>",
        )
        zf.writestr(
            "xl/worksheets/sheet1.xml",
            '<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            "<sheetData>"
            '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>2</v></c></row>'
            '<row r="2"><c r="A2" t="s"><v>1</v></c><c r="B2" t="s"><v>3</v></c></row>'
            "</sheetData></worksheet>",
        )
    return buf.getvalue()


def _make_docx() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "word/document.xml",
            '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "<w:body>"
            "<w:p><w:r><w:t>Packing list ekspor kopi.</w:t></w:r></w:p>"
            "<w:p><w:r><w:t>Berat bersih 500 kg.</w:t></w:r></w:p>"
            "</w:body></w:document>",
        )
    return buf.getvalue()


def _make_pptx() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "ppt/slides/slide1.xml",
            '<?xml version="1.0"?><p:sld xmlns:p="x" '
            'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            "<a:t>Rencana Ekspor 2026</a:t><a:t>Target pasar Jepang</a:t></p:sld>",
        )
    return buf.getvalue()


@contextlib.contextmanager
def _client():
    with TestClient(app) as c:
        c.post(
            "/api/v1/auth/login/",
            json={"email": "admin@mauekspor.example", "password": "admin123"},
        )
        yield c


def _upload(c, name, content, ctype="application/octet-stream"):
    files = {"file": (name, io.BytesIO(content), ctype)}
    res = c.post("/api/v1/files/upload/", files=files, data={"type_": "Document"})
    assert res.status_code == 200, res.text
    return res.json()["data"]


# ── Unit: ekstraktor isi ──────────────────────────────────────────────────────
def test_extract_xlsx_rows():
    preview = file_content.extract("data.xlsx", _make_xlsx())
    assert preview.kind == "spreadsheet"
    assert preview.sheets[0]["rows"][1] == ["Kopi Gayo", "Jepang"]
    assert "Kopi Gayo" in preview.text


def test_extract_csv():
    raw = "produk,negara\nKopi,Jepang\n".encode()
    preview = file_content.extract("data.csv", raw)
    assert preview.kind == "spreadsheet"
    assert preview.sheets[0]["rows"][0] == ["produk", "negara"]
    # CSV tetap dapat diparse kembali oleh modul csv standar
    assert list(csv.reader(io.StringIO(preview.sheets[0]["rows"][1][0] + ",")))[0][0] == "Kopi"


def test_extract_docx_paragraphs():
    preview = file_content.extract("dok.docx", _make_docx())
    assert preview.kind == "document"
    assert preview.paragraphs == ["Packing list ekspor kopi.", "Berat bersih 500 kg."]


def test_extract_pptx_slides():
    preview = file_content.extract("deck.pptx", _make_pptx())
    assert preview.kind == "presentation"
    assert preview.metadata["slide_count"] == 1
    assert "Rencana Ekspor 2026" in preview.slides[0]


def test_extract_txt():
    preview = file_content.extract("note.txt", b"halo dunia")
    assert preview.kind == "text"
    assert preview.text == "halo dunia"


def test_extract_unknown_and_corrupt():
    assert file_content.extract("x.bin", b"\x00\x01").kind == "unknown"
    # docx rusak tidak boleh melempar exception
    assert file_content.extract("x.docx", b"not a zip").kind == "document"


def test_ai_context_includes_summary():
    preview = file_content.extract("data.txt", b"baris penting")
    ctx = file_content.ai_context(preview)
    assert "Isi berkas:" in ctx
    assert "baris penting" in ctx


# ── API: preview ──────────────────────────────────────────────────────────────
def test_preview_endpoint_xlsx():
    with _client() as c:
        asset = _upload(c, "angka.xlsx", _make_xlsx())
        res = c.get(f"/api/v1/files/{asset['id']}/preview/")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["preview"]["kind"] == "spreadsheet"
        assert data["storageAvailable"] is True


def test_preview_endpoint_missing_file_404():
    with _client() as c:
        res = c.get("/api/v1/files/FIL-TIDAK-ADA/preview/")
        assert res.status_code == 404


def test_preview_endpoint_no_storage():
    # Berkas seed tanpa storageName → metadata saja, bukan error.
    with _client() as c:
        res = c.get("/api/v1/files/FIL-CI-JP/preview/")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["storageAvailable"] is False


# ── API: analyze ──────────────────────────────────────────────────────────────
def test_analyze_endpoint_returns_analysis():
    with _client() as c:
        asset = _upload(c, "angka.xlsx", _make_xlsx())
        res = c.post(f"/api/v1/files/{asset['id']}/analyze/")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["kind"] == "spreadsheet"
        assert data["analysis"]  # mock fallback pun mengisi analisis
        assert "Ringkasan" in data["analysis"] or "analisis" in data["analysis"].lower()


def test_analyze_endpoint_persists_analysis():
    with _client() as c:
        asset = _upload(c, "dok.docx", _make_docx())
        c.post(f"/api/v1/files/{asset['id']}/analyze/")
        listed = c.get("/api/v1/files/").json()["data"]
        rec = next(f for f in listed if f["id"] == asset["id"])
        assert rec.get("aiAnalysis", {}).get("text")


def test_analyze_endpoint_missing_file_404():
    with _client() as c:
        res = c.post("/api/v1/files/FIL-TIDAK-ADA/analyze/")
        assert res.status_code == 404
