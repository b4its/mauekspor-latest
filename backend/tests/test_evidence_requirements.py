"""Regresi: klaim harus berbukti (dokumen/gambar), bukan centang kosong.

Menutup kelas bug "klaim tanpa bukti":
1. Sertifikasi profil tanpa berkas tidak menambah skor kesiapan.
2. Sertifikasi dengan berkas menambah skor & menandai verified.
3. Verifikasi supplier wajib berkas.
4. Kualifikasi buyer wajib berkas.
5. Verifikasi berkas wajib mencatat peninjau.
6. Requirement kepatuhan tidak bisa "Verified" tanpa bukti (server-side).
"""
from fastapi.testclient import TestClient

from app.main import app
from app import db
from app.services import readiness as readiness_svc

_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
    b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00"
    b"\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _login(c: TestClient) -> dict:
    res = c.post("/api/v1/auth/login/", json={"email": "admin@mauekspor.example", "password": "admin123"})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['meta']['access_token']}"}


def _upload(c: TestClient, h: dict, name: str = "evidence.png") -> str:
    res = c.post(
        "/api/v1/files/upload/",
        files={"file": (name, _PNG_BYTES, "image/png")},
        data={"type_": "Certificate", "project_id": "", "tags": "evidence,test"},
        headers=h,
    )
    assert res.status_code == 200, res.text
    return res.json()["data"]["id"]


def test_certification_without_evidence_does_not_raise_readiness():
    with TestClient(app) as c:
        h = _login(c)
        created = c.post(
            "/api/v1/business-profiles/",
            json={"companyName": "PT Tanpa Bukti", "address": "Jakarta",
                  "productionCapacity": "1 ton", "yearEstablished": 2020, "owner": "X"},
            headers=h,
        )
        pid = created.json()["data"]["id"]
        # Klaim 3 sertifikasi (bentuk lama) → tidak boleh menaikkan skor.
        base = db.get("business_profiles", pid)["readiness"]
        res = c.post(f"/api/v1/business-profiles/{pid}/certifications/",
                     json={"certifications": ["Halal", "ISO 22000", "HACCP"]}, headers=h)
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["certifiedCount"] == 0
        assert data["readiness"] == base  # klaim tanpa bukti tidak menambah skor
        assert all(not i["verified"] for i in data["certificationItems"])


def test_certification_with_evidence_raises_readiness_and_marks_verified():
    with TestClient(app) as c:
        h = _login(c)
        created = c.post(
            "/api/v1/business-profiles/",
            json={"companyName": "PT Berbukti", "address": "Bandung",
                  "productionCapacity": "2 ton", "yearEstablished": 2019, "owner": "Y"},
            headers=h,
        )
        pid = created.json()["data"]["id"]
        base = db.get("business_profiles", pid)["readiness"]
        file_id = _upload(c, h)
        res = c.post(f"/api/v1/business-profiles/{pid}/certifications/",
                     json={"items": [{"name": "Halal", "fileId": file_id}]}, headers=h)
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["certifiedCount"] == 1
        assert data["readiness"] > base
        item = data["certificationItems"][0]
        assert item["verified"] is True and item["evidenceFileId"] == file_id


def test_certification_with_bad_file_id_is_rejected():
    with TestClient(app) as c:
        h = _login(c)
        pid = c.post("/api/v1/business-profiles/",
                     json={"companyName": "PT Salah ID", "address": "Surabaya"}, headers=h).json()["data"]["id"]
        res = c.post(f"/api/v1/business-profiles/{pid}/certifications/",
                     json={"items": [{"name": "Halal", "fileId": "FIL-TIDAK-ADA"}]}, headers=h)
        assert res.status_code == 404


def test_readiness_counts_only_evidenced_certs():
    assert readiness_svc.evidenced_certification_count({"certifications": ["Halal", "ISO"]}) == 0
    assert readiness_svc.evidenced_certification_count(
        {"certificationItems": [{"name": "Halal", "verified": True}, {"name": "ISO", "verified": False}]}
    ) == 1
    assert readiness_svc.evidenced_certification_count(
        {"certificationItems": [{"name": "Halal", "evidenceFileId": "FIL-1"}]}
    ) == 1


def test_supplier_verify_requires_evidence():
    with TestClient(app) as c:
        h = _login(c)
        sid = c.get("/api/v1/suppliers/", headers=h).json()["data"][0]["id"]
        assert c.post(f"/api/v1/suppliers/{sid}/verify/", headers=h).status_code == 422
        assert c.post(f"/api/v1/suppliers/{sid}/verify/", json={"fileId": "FIL-NA"}, headers=h).status_code == 404
        file_id = _upload(c, h)
        ok = c.post(f"/api/v1/suppliers/{sid}/verify/", json={"fileId": file_id}, headers=h)
        assert ok.status_code == 200 and ok.json()["data"]["evidenceFileId"] == file_id


def test_buyer_qualify_requires_evidence():
    with TestClient(app) as c:
        h = _login(c)
        bid = c.get("/api/v1/buyers/", headers=h).json()["data"][0]["id"]
        assert c.post(f"/api/v1/buyers/{bid}/qualify/", headers=h).status_code == 422
        file_id = _upload(c, h)
        ok = c.post(f"/api/v1/buyers/{bid}/qualify/", json={"fileId": file_id}, headers=h)
        assert ok.status_code == 200 and ok.json()["data"]["evidenceFileId"] == file_id


def test_file_verify_requires_reviewer():
    with TestClient(app) as c:
        h = _login(c)
        file_id = _upload(c, h)
        assert c.post(f"/api/v1/files/{file_id}/verify/", headers=h).status_code == 422
        ok = c.post(f"/api/v1/files/{file_id}/verify/", json={"reviewedBy": "QA", "note": "ok"}, headers=h)
        assert ok.status_code == 200
        data = ok.json()["data"]
        assert data["verifiedBy"] == "QA" and data["verificationNote"] == "ok"


def test_compliance_verified_requires_evidence():
    with TestClient(app) as c:
        h = _login(c)
        rid = c.get("/api/v1/compliance/requirements/", headers=h).json()["data"][0]["id"]
        # Tanpa bukti → 422.
        blocked = c.patch(f"/api/v1/compliance/requirements/{rid}/", json={"status": "Verified"}, headers=h)
        assert blocked.status_code == 422, blocked.text
        # Unggah bukti + set status Evidence Uploaded → kini Verified diizinkan.
        file_id = _upload(c, h)
        c.post(f"/api/v1/compliance/requirements/{rid}/evidence/", json={"fileId": file_id, "note": "ok"}, headers=h)
        ok = c.patch(f"/api/v1/compliance/requirements/{rid}/", json={"status": "Verified"}, headers=h)
        assert ok.status_code == 200
