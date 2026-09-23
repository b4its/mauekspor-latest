"""Semua endpoint API. Prefix /api/v1, respons # {"data": T, "meta": {}}."""

import json
import os
import pathlib
import time

from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, File, Form
from fastapi.responses import FileResponse

from app import ai, db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    decode_token,
)
from app.schemas import models as sc

router = APIRouter(prefix="/api/v1")


def _serialize(record):
    out = {k: v for k, v in dict(record).items() if not k.startswith("__")}
    out.pop("password", None)
    return out


def _list_query(table: str) -> dict:
    return {"data": [_serialize(r) for r in db.all(table)], "meta": {}}


def _filtered_query(
    table: str,
    search: str = "",
    search_fields: tuple[str, ...] = (),
    status: str = "",
    status_field: str = "status",
    limit: int = 0,
    offset: int = 0,
) -> dict:
    """List dengan filter opsional: search (LIKE pada field), status, dan pagination.

    Bila `limit` <= 0, kembalikan semua (perilaku default lama agar kontrak frontend tetap).
    """
    items = db.all(table)
    if search:
        q = search.lower()
        items = [
            r for r in items
            if any(q in str(r.get(f, "")).lower() for f in search_fields)
        ]
    if status:
        items = [r for r in items if str(r.get(status_field, "")).lower() == status.lower()]
    total = len(items)
    if limit > 0:
        items = items[offset:offset + limit]
    return {
        "data": [_serialize(r) for r in items],
        "meta": {"total": total, "limit": limit, "offset": offset, "count": len(items)},
    }


def _one(record) -> dict:
    db.save(record)
    return {"data": _serialize(record), "meta": {}}


def _notify(title: str, description: str, module: str, severity: str = "Info", href: str = "") -> None:
    """Buat notifikasi internal (dipanggil pada aksi penting)."""
    db.insert("notifications", {
        "id": db.gen_id("notifications", "NTF"),
        "title": title,
        "description": description,
        "module": module,
        "severity": severity,
        "status": "Unread",
        "time": "now",
        "href": href,
    })


# ----------------------------------------------------------------------------
# HEALTH & ROOT
# ----------------------------------------------------------------------------
@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("")
def api_root():
    return {"data": {"app": "MauEkspor API", "version": "0.2.0", "docs": "/docs"}, "meta": {}}


# ----------------------------------------------------------------------------
# AUTH
# ----------------------------------------------------------------------------
@router.post("/auth/login/")
def login(payload: sc.LoginPayload, response: Response):
    user = db.get_by("users", email=str(payload.email))
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(401, "Incorrect email or password")
    access, refresh = _issue_tokens(user, response)
    return {"data": _serialize(user), "meta": {"access_token": access, "refresh_token": refresh}}


def _issue_tokens(user: dict, response: Response) -> tuple[str, str]:
    access = create_access_token(user)
    refresh = create_refresh_token(user)
    db.insert("refresh_tokens", {
        "id": db.gen_id("refresh_tokens", "RFT"),
        "token": refresh,
        "userId": user["id"],
        "createdAt": "2026-08-07",
        "expiresAt": None,
        "revoked": False,
    })
    response.set_cookie("access_token", access, httponly=True, samesite="lax", max_age=3600)
    response.set_cookie("refresh_token", refresh, httponly=True, samesite="lax", max_age=7 * 86400)
    return access, refresh


@router.post("/auth/register/")
def register(payload: sc.RegisterPayload, response: Response):
    if db.get_by("users", email=str(payload.email)):
        raise HTTPException(409, "Email already registered")
    user = db.insert("users", {
        "id": db.gen_id("users", "U"),
        "email": str(payload.email),
        "fullName": payload.name,
        "name": payload.name,
        "role": payload.role,
        "organization": payload.organization,
        "password": hash_password(payload.password),
        "status": "Active",
        "createdAt": "2026-08-07",
        "lastLogin": "new",
    })
    access, _ = _issue_tokens(user, response)
    return {"data": _serialize(user), "meta": {"access_token": access}}


@router.post("/auth/register-admin/")
def register_admin(payload: sc.RegisterAdminPayload, response: Response):
    """Buat user Admin — via kode bootstrap `MAUEKSPOR_ADMIN_CODE` atau admin yang sudah login."""
    code = os.environ.get("MAUEKSPOR_ADMIN_CODE", "admin-bootstrap-2026")
    if payload.admin_code and payload.admin_code != code:
        raise HTTPException(403, "Invalid admin code")
    if not payload.admin_code and not os.environ.get("MAUEKSPOR_ADMIN_CODE"):
        # Jika tanpa kode, hanya admin yang bisa (dicek middleware untuk module auth? tidak)
        raise HTTPException(403, "Admin code required")
    if db.get_by("users", email=str(payload.email)):
        raise HTTPException(409, "Email already registered")
    user = db.insert("users", {
        "id": db.gen_id("users", "U"),
        "email": str(payload.email),
        "fullName": payload.full_name,
        "name": payload.full_name,
        "role": "Admin",
        "organization": "",
        "password": hash_password(payload.password),
        "status": "Active",
        "createdAt": "2026-08-07",
        "lastLogin": "new",
    })
    access, _ = _issue_tokens(user, response)
    return {"data": _serialize(user), "meta": {"access_token": access}}


@router.get("/auth/me/")
def me(current_user: dict = Depends(get_current_user)):
    return _one(current_user)


@router.post("/auth/logout/")
def logout(request: Request, response: Response):
    token = request.cookies.get("refresh_token") or request.headers.get("X-Refresh-Token")
    if token:
        for rec in db.find("refresh_tokens", token=token):
            rec["revoked"] = True
            db.save(rec)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"data": {"status": "logged_out"}, "meta": {}}


@router.post("/auth/refresh/")
def refresh(request: Request, response: Response):
    token = request.cookies.get("refresh_token") or request.headers.get("X-Refresh-Token")
    if not token:
        raise HTTPException(401, "No refresh token")
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(401, "Not a refresh token")
    session = db.get_by("refresh_tokens", token=token)
    if not session or session.get("revoked"):
        raise HTTPException(401, "Refresh token revoked or unknown")
    user = db.get("users", payload["sub"])
    if not user:
        raise HTTPException(401, "User not found")
    session["revoked"] = True
    db.save(session)
    access, new_refresh = _issue_tokens(user, response)
    return {"data": _serialize(user), "meta": {"access_token": access, "refresh_token": new_refresh}}


# ----------------------------------------------------------------------------
# USERS
# ----------------------------------------------------------------------------
@router.get("/users/")
def list_users(search: str = "", role: str = "", limit: int = 0, offset: int = 0):
    items = db.all("users")
    if search:
        q = search.lower()
        items = [r for r in items if q in str(r.get("email", "")).lower() or q in str(r.get("fullName", "")).lower()]
    if role:
        items = [r for r in items if str(r.get("role", "")).lower() == role.lower()]
    total = len(items)
    if limit > 0:
        items = items[offset:offset + limit]
    return {"data": [_serialize(r) for r in items], "meta": {"total": total, "limit": limit, "offset": offset, "count": len(items)}}


@router.get("/users/{user_id}/")
def get_user(user_id: str):
    record = db.get("users", user_id)
    if not record:
        raise HTTPException(404, "User not found")
    return _one(record)


@router.delete("/users/{user_id}/")
def delete_user(user_id: str):
    record = db.get("users", user_id)
    if not record:
        raise HTTPException(404, "User not found")
    db.delete("users", user_id)
    # Bersihkan data terkait
    for table in ("business_profiles", "products", "projects", "buyer_requests", "catalogs",
                  "export_analyses", "costing", "notifications", "api_keys", "support_tickets"):
        for related in db.find(table, ownerId=user_id):
            db.delete(table, related.get("id"))
    return {"data": {"status": "deleted", "id": user_id}, "meta": {}}


# ----------------------------------------------------------------------------
# CSV EXPORT (didefinisikan sebelum route parameterized agar tidak tertutup)
# ----------------------------------------------------------------------------
def _csv_response(rows: list[list], filename: str) -> Response:
    import csv as _csv
    import io as _io
    buffer = _io.StringIO()
    writer = _csv.writer(buffer)
    for row in rows:
        writer.writerow(["" if v is None else v for v in row])
    from fastapi.responses import Response
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _xlsx_bytes(sheet_name: str, rows: list[list]) -> bytes:
    """Buat workbook .xlsx minimal tanpa dependensi (zipped XML + inline strings)."""
    import html as _html
    import io as _io
    import zipfile

    def esc(v):
        return _html.escape(str(v), quote=True)

    sheet_rows = []
    for r_idx, row in enumerate(rows, start=1):
        cells = []
        for c_idx, value in enumerate(row, start=1):
            ref = f"{chr(64 + c_idx)}{r_idx}"
            if value is None or str(value) == "":
                cells.append(f'<c r="{ref}"/>')
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                cells.append(f'<c r="{ref}"><v>{value}</v></c>')
            else:
                cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{esc(value)}</t></is></c>')
        sheet_rows.append("<row>" + "".join(cells) + "</row>")

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(sheet_rows)}</sheetData></worksheet>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        "</Types>"
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    )
    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<sheets><sheet name="{esc(sheet_name)}" sheetId="1" r:id="rId1"/></sheets></workbook>'
    )
    workbook_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        "</Relationships>"
    )
    buffer = _io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)
    return buffer.getvalue()


def _xlsx_response(rows: list[list], sheet_name: str, filename: str) -> Response:
    content = _xlsx_bytes(sheet_name, rows)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/products/export.xlsx")
def export_products_xlsx():
    rows = [["id", "name", "category", "status", "hs", "origin", "packaging", "netWeight", "grossWeight", "moq", "leadTime", "readiness"]]
    for p in db.all("products"):
        rows.append([p.get("id"), p.get("name"), p.get("category"), p.get("status"), p.get("hs"), p.get("origin"),
                     p.get("packaging"), p.get("netWeight"), p.get("grossWeight"), p.get("moq"), p.get("leadTime"), p.get("readiness")])
    return _xlsx_response(rows, "Products", "products.xlsx")


@router.get("/buyers/export.xlsx")
def export_buyers_xlsx():
    rows = [["id", "name", "country", "segment", "status", "fitScore", "estimatedAnnualValue", "nextStep"]]
    for b in db.all("buyers"):
        rows.append([b.get("id"), b.get("name"), b.get("country"), b.get("segment"), b.get("status"),
                     b.get("fitScore"), b.get("estimatedAnnualValue"), b.get("nextStep")])
    return _xlsx_response(rows, "Buyers", "buyers.xlsx")


@router.get("/export-analysis/export.xlsx")
def export_analyses_xlsx():
    rows = [["id", "productName", "destination", "status", "hsCode", "score", "grade", "confidence", "summary"]]
    for a in db.all("export_analyses"):
        rows.append([a.get("id"), a.get("productName"), a.get("destination"), a.get("status"), a.get("hsCode"),
                     a.get("score"), a.get("statusGrade"), a.get("confidence"), a.get("summary")])
    return _xlsx_response(rows, "ExportAnalysis", "export-analyses.xlsx")


@router.get("/costing/export.xlsx")
def export_costing_xlsx():
    rows = [["id", "title", "destination", "incoterm", "margin", "exchangeRate", "exwPrice", "fobPrice", "cifPrice", "status"]]
    for c in db.all("costing"):
        rows.append([c.get("id"), c.get("title"), c.get("destination"), c.get("incoterm"), c.get("margin"),
                     c.get("exchangeRate"), c.get("exwPrice"), c.get("fobPrice"), c.get("cifPrice"), c.get("status")])
    return _xlsx_response(rows, "Costing", "costing.xlsx")


@router.get("/audit/export.xlsx")
def export_audit_xlsx():
    rows = [["time", "actor", "action", "detail"]]
    for a in db.all("audit"):
        rows.append([a.get("time"), a.get("actor"), a.get("action"), a.get("detail")])
    return _xlsx_response(rows, "Audit", "audit.xlsx")


@router.get("/products/export.csv")
def export_products_csv():
    rows = [["id", "name", "category", "status", "hs", "origin", "packaging", "netWeight", "grossWeight", "moq", "leadTime", "readiness"]]
    for p in db.all("products"):
        rows.append([p.get("id"), p.get("name"), p.get("category"), p.get("status"), p.get("hs"), p.get("origin"),
                     p.get("packaging"), p.get("netWeight"), p.get("grossWeight"), p.get("moq"), p.get("leadTime"), p.get("readiness")])
    return _csv_response(rows, "products.csv")


@router.get("/buyers/export.csv")
def export_buyers_csv():
    rows = [["id", "name", "country", "segment", "status", "fitScore", "estimatedAnnualValue", "nextStep"]]
    for b in db.all("buyers"):
        rows.append([b.get("id"), b.get("name"), b.get("country"), b.get("segment"), b.get("status"),
                     b.get("fitScore"), b.get("estimatedAnnualValue"), b.get("nextStep")])
    return _csv_response(rows, "buyers.csv")


@router.get("/export-analysis/export.csv")
def export_analyses_csv():
    rows = [["id", "productName", "destination", "status", "hsCode", "score", "grade", "confidence", "summary"]]
    for a in db.all("export_analyses"):
        rows.append([a.get("id"), a.get("productName"), a.get("destination"), a.get("status"), a.get("hsCode"),
                     a.get("score"), a.get("statusGrade"), a.get("confidence"), a.get("summary")])
    return _csv_response(rows, "export-analyses.csv")


@router.get("/costing/export.csv")
def export_costing_csv():
    rows = [["id", "title", "destination", "incoterm", "margin", "exchangeRate", "exwPrice", "fobPrice", "cifPrice", "status"]]
    for c in db.all("costing"):
        rows.append([c.get("id"), c.get("title"), c.get("destination"), c.get("incoterm"), c.get("margin"),
                     c.get("exchangeRate"), c.get("exwPrice"), c.get("fobPrice"), c.get("cifPrice"), c.get("status")])
    return _csv_response(rows, "costing.csv")


# ----------------------------------------------------------------------------
# PRODUCTS
# ----------------------------------------------------------------------------
@router.get("/products/")
def list_products(search: str = "", status: str = "", category: str = "", limit: int = 0, offset: int = 0):
    items = db.all("products")
    if search:
        q = search.lower()
        items = [r for r in items if q in str(r.get("name", "")).lower() or q in str(r.get("hs", "")).lower() or q in str(r.get("origin", "")).lower()]
    if status:
        items = [r for r in items if str(r.get("status", "")).lower() == status.lower()]
    if category:
        items = [r for r in items if str(r.get("category", "")).lower() == category.lower()]
    total = len(items)
    if limit > 0:
        items = items[offset:offset + limit]
    return {"data": [_serialize(r) for r in items], "meta": {"total": total, "limit": limit, "offset": offset, "count": len(items)}}


@router.get("/products/{product_id}/")
def get_product(product_id: str):
    record = db.get("products", product_id)
    if not record:
        raise HTTPException(404, "Product not found")
    return _one(record)


@router.post("/products/")
def create_product(payload: sc.CreateProductPayload):
    data = payload.model_dump()
    data.update({
        "id": db.gen_id("products", "PRD"),
        "status": "Needs HS Review",
        "hs": "TBD",
        "certificates": [],
        "readiness": 40,
        "description": "",
        "material_composition": "",
        "production_technique": "",
        "finishing_type": "",
        "quality_specs": {},
        "dimensions_l_w_h": {},
        "weight_net": None,
        "weight_gross": None,
        "updatedAt": "now",
    })
    data["readiness"] = compute_product_readiness(data)
    return _one(db.insert("products", data))


def _generate_sku(product: dict) -> str:
    """SKU deterministik {CAT}-{MAT}-{SEQ:03d} (diadaptasi dari ExportReadyAI ai_service)."""
    cat = (product.get("category") or "GEN")[:3].upper()
    if not cat.isalpha():
        cat = (product.get("name") or "PRO")[:3].upper()
    mat = (product.get("material_composition") or product.get("origin") or "MAT")[:3].upper()
    if not mat.isalpha():
        mat = "MAT"
    seq = len(db.find("product_enrichments", productId=str(product.get("id", "")))) + 1
    return f"{cat}-{mat}-{seq:03d}"


def compute_product_readiness(product: dict) -> int:
    """Skor kesiapan produk 0-100 dari kelengkapan data (diadaptasi dari readiness model ExportReadyAI)."""
    score = 20  # base
    name = str(product.get("name", "")).strip()
    category = str(product.get("category", "")).strip()
    if name and category:
        score += 15
    if product.get("description") or product.get("quality_specs") or product.get("material_composition"):
        score += 10
    if product.get("packaging"):
        score += 10
    if product.get("netWeight") or product.get("weight_net"):
        score += 5
    if product.get("grossWeight") or product.get("weight_gross"):
        score += 5
    if product.get("moq") or product.get("min_order_quantity"):
        score += 5
    if product.get("leadTime") or product.get("lead_time_days"):
        score += 5
    if product.get("certificates"):
        score += min(len(product["certificates"]) * 5, 15)
    if product.get("status") == "Enriched" and product.get("hs") not in (None, "", "TBD"):
        score += 10
    return max(0, min(100, score))


@router.post("/products/batch/enrich/")
def batch_enrich_products(payload: sc.BatchActionPayload):
    """Enrich beberapa produk sekaligus (default: semua yang masih 'Needs HS Review').

    Jika payload.ids kosong, ambil semua produk berstatus 'Needs HS Review'.
    Endpoint ini didasarkan pada ProductSync service Adaptasi ExportReadyAI (sync & review loop).
    """
    from app.data.hs_loader import get_hs_loader

    loader = get_hs_loader()
    if payload.ids:
        targets = [db.get("products", pid) for pid in payload.ids if db.get("products", pid)]
    else:
        targets = [p for p in db.all("products") if p.get("status") != "Enriched"]

    enriched, skipped = [], []
    for record in targets:
        keywords = " ".join([str(record.get("name", "")), str(record.get("category", "")), str(record.get("description", ""))])
        context = loader.get_hs_code_context(keywords, max_results=10)
        system = "You are an Indonesia export HS code classifier. Return JSON with keys hsCode (8 digits), confidence (0-100), reason."
        user = f"Product: {record.get('name', '')} ({record.get('category', '')} - {record.get('description', '')})\n{context}"
        enriched_data = ai.ask_json(system, user, kind="classify")
        hs_code = ""
        confidence = None
        if enriched_data and enriched_data.get("hsCode"):
            hs_code = str(enriched_data["hsCode"])
            confidence = enriched_data.get("confidence")
        if not hs_code:
            results = loader.search_hs_codes(keywords, max_results=1, min_level=6)
            if results:
                hs_code = results[0]["hs_code"]
                if len(hs_code) == 6:
                    hs_code = f"{hs_code}00"
        if not hs_code:
            hs_code = "00000000"

        sku = _generate_sku(record)
        record["status"] = "Enriched"
        record["hs"] = hs_code
        record["hsConfidence"] = confidence if confidence is not None else 88
        record["sku"] = sku
        record["readiness"] = compute_product_readiness(record)
        record["updatedAt"] = "now"
        db.save(record)

        existing = db.get_by("product_enrichments", productId=record["id"])
        if existing:
            existing.update({"hsCodeRecommendation": hs_code, "skuGenerated": sku, "lastUpdatedAi": "now"})
            db.save(existing)
        else:
            db.insert("product_enrichments", {
                "id": db.gen_id("product_enrichments", "ENR"),
                "productId": record["id"],
                "hsCodeRecommendation": hs_code,
                "skuGenerated": sku,
                "nameEnglishB2b": record.get("name_english_b2b", ""),
                "descriptionEnglishB2b": record.get("description_english_b2b", ""),
                "marketingHighlights": record.get("marketing_highlights", []),
                "lastUpdatedAi": "now",
            })
        enriched.append(record["id"])
    return {"data": {"enriched": enriched, "enrichedCount": len(enriched), "skippedCount": len(skipped), "targetCount": len(targets)}, "meta": {}}


@router.post("/products/{product_id}/enrich/")
def enrich_product(product_id: str):
    record = db.get("products", product_id)
    if not record:
        raise HTTPException(404, "Product not found")

    from app.data.hs_loader import get_hs_loader
    loader = get_hs_loader()
    keywords = " ".join([str(record.get("name", "")), str(record.get("category", "")), str(record.get("description", ""))])
    context = loader.get_hs_code_context(keywords, max_results=15)
    system = "You are an Indonesia export HS code classifier. Return JSON with keys hsCode (8 digits), confidence (0-100), reason."
    user = f"Product: {record.get('name', '')} ({record.get('category', '')} - {record.get('description', '')})\n{context}"

    enriched = ai.ask_json(system, user, kind="classify")
    hs_code = ""
    confidence = None
    if enriched and enriched.get("hsCode"):
        hs_code = str(enriched["hsCode"])
        confidence = enriched.get("confidence")
    if not hs_code:
        # Fallback: cari HS code dari dataset
        results = loader.search_hs_codes(keywords, max_results=1, min_level=6)
        if results:
            hs_code = results[0]["hs_code"]
            if len(hs_code) == 6:
                hs_code = f"{hs_code}00"
    if not hs_code:
        hs_code = "00000000"

    sku = _generate_sku(record)
    record["status"] = "Enriched"
    record["hs"] = hs_code
    record["hsConfidence"] = confidence if confidence is not None else 88
    record["sku"] = sku
    record["status"] = "Enriched"
    record["readiness"] = compute_product_readiness(record)
    record["updatedAt"] = "now"

    # Simpan enrichment terpisah (1-per-produk)
    existing = db.get_by("product_enrichments", productId=product_id)
    if existing:
        existing.update({
            "hsCodeRecommendation": hs_code,
            "skuGenerated": sku,
            "lastUpdatedAi": "now",
        })
        db.save(existing)
    else:
        db.insert("product_enrichments", {
            "id": db.gen_id("product_enrichments", "ENR"),
            "productId": product_id,
            "hsCodeRecommendation": hs_code,
            "skuGenerated": sku,
            "nameEnglishB2b": record.get("name_english_b2b", ""),
            "descriptionEnglishB2b": record.get("description_english_b2b", ""),
            "marketingHighlights": record.get("marketing_highlights", []),
            "lastUpdatedAi": "now",
        })
    return _one(record)


@router.post("/products/batch/delete/")
def batch_delete_products(payload: sc.BatchActionPayload):
    """Hapus beberapa produk sekaligus berdasarkan daftar ids."""
    if not payload.ids:
        raise HTTPException(422, "ids wajib diisi")
    deleted = []
    for pid in payload.ids:
        record = db.get("products", pid)
        if record:
            db.delete("products", pid)
            for enrich in db.find("product_enrichments", productId=pid):
                db.delete("product_enrichments", enrich.get("id"))
            deleted.append(pid)
    return {"data": {"deleted": deleted, "deletedCount": len(deleted)}, "meta": {}}


@router.patch("/products/{product_id}/")
def update_product(product_id: str, payload: sc.UpdateProductPayload):
    record = db.get("products", product_id)
    if not record:
        raise HTTPException(404, "Product not found")
    data = payload.model_dump(exclude_none=True)
    # Normalisasi field gabungan
    if data.get("hs_code") and not data.get("hs"):
        data["hs"] = data["hs_code"]
    if data.get("netWeight"):
        data["netWeight"] = data["netWeight"]
    record.update(data)
    record["readiness"] = compute_product_readiness(record)
    record["updatedAt"] = "now"
    # Jika ada field enrichment, update tabel enrichment juga
    enrich_patch = {}
    if data.get("hs_code"):
        enrich_patch["hsCodeRecommendation"] = data["hs_code"]
    if data.get("sku"):
        enrich_patch["skuGenerated"] = data["sku"]
    if data.get("name_english_b2b"):
        enrich_patch["nameEnglishB2b"] = data["name_english_b2b"]
    if data.get("description_english_b2b"):
        enrich_patch["descriptionEnglishB2b"] = data["description_english_b2b"]
    if data.get("marketing_highlights") is not None:
        enrich_patch["marketingHighlights"] = data["marketing_highlights"]
    if enrich_patch:
        existing = db.get_by("product_enrichments", productId=product_id)
        if existing:
            existing.update(enrich_patch)
            db.save(existing)
        else:
            db.insert("product_enrichments", {
                "id": db.gen_id("product_enrichments", "ENR"),
                "productId": product_id,
                **enrich_patch,
                "lastUpdatedAi": "now",
            })
    return _one(record)


@router.delete("/products/{product_id}/")
def delete_product(product_id: str):
    record = db.get("products", product_id)
    if not record:
        raise HTTPException(404, "Product not found")
    db.delete("products", product_id)
    for tbl in ("product_enrichments", "market_intelligence", "pricing_results"):
        for related in db.find(tbl, productId=product_id):
            db.delete(tbl, related.get("id"))
    return {"data": {"status": "deleted", "id": product_id}, "meta": {}}


# ----------------------------------------------------------------------------
# PRODUCT AI: market intelligence / pricing / catalog description
# ----------------------------------------------------------------------------
@router.get("/products/{product_id}/ai/market-intelligence/")
def get_market_intelligence(product_id: str):
    record = db.get_by("market_intelligence", productId=product_id)
    if not record:
        raise HTTPException(404, "Market intelligence not found")
    return _one(record)


@router.post("/products/{product_id}/ai/market-intelligence/")
def create_market_intelligence(product_id: str):
    product = db.get("products", product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    from app.services.market_intel import generate_market_intelligence
    result = generate_market_intelligence(product)
    existing = db.get_by("market_intelligence", productId=product_id)
    if existing:
        existing.update(result)
        db.save(existing)
        return _one(existing)
    record = db.insert("market_intelligence", {
        "id": db.gen_id("market_intelligence", "MI"),
        **result,
    })
    return _one(record)


@router.get("/products/{product_id}/ai/pricing/")
def get_product_pricing(product_id: str):
    record = db.get_by("pricing_results", productId=product_id)
    if not record:
        raise HTTPException(404, "Pricing result not found")
    return _one(record)


@router.post("/products/{product_id}/ai/pricing/")
def create_product_pricing(product_id: str, payload: dict):
    product = db.get("products", product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    from app.services.market_intel import generate_product_pricing
    cogs = payload.get("cogs_per_unit_idr") or payload.get("cogsPerUnitIdr") or 0
    margin = payload.get("target_margin_percent") or payload.get("targetMarginPercent") or 30
    country = payload.get("target_country_code") or payload.get("targetCountryCode") or "JP"
    result = generate_product_pricing(product, float(cogs), float(margin), str(country))
    existing = db.get_by("pricing_results", productId=product_id)
    if existing:
        existing.update(result)
        db.save(existing)
        return _one(existing)
    record = db.insert("pricing_results", {
        "id": db.gen_id("pricing_results", "PRC"),
        **result,
    })
    return _one(record)


@router.post("/products/{product_id}/ai/catalog-description/")
def generate_product_catalog_description(product_id: str, payload: dict):
    product = db.get("products", product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    from app.services.market_intel import generate_catalog_description
    result = generate_catalog_description(product)
    return {"data": result, "meta": {}}



# ----------------------------------------------------------------------------
# TRADE PROJECTS
# ----------------------------------------------------------------------------
@router.get("/trade-projects/")
def list_projects():
    return _list_query("projects")


@router.get("/trade-projects/{project_id}/")
def get_project(project_id: str):
    record = db.get("projects", project_id)
    if not record:
        raise HTTPException(404, "Project not found")
    return _one(record)


@router.post("/trade-projects/")
def create_project(payload: sc.CreateTradeProjectPayload):
    data = payload.model_dump()
    data.update({
        "id": db.gen_id("projects", "EXP"),
        "stage": "Scoping",
        "readiness": 25,
        "risk": "Low",
        "hsCode": "TBD",
        "port": "TBD",
        "payment": "TBD",
        "updatedAt": "now",
    })
    data.setdefault("value", data.get("targetValue") or 0)
    return _one(db.insert("projects", data))


# ----------------------------------------------------------------------------
# BUSINESS PROFILES
# ----------------------------------------------------------------------------
@router.get("/business-profiles/")
def list_profiles():
    return _list_query("business_profiles")


@router.get("/business-profiles/{profile_id}/")
def get_profile(profile_id: str):
    record = db.get("business_profiles", profile_id)
    if not record:
        raise HTTPException(404, "Business profile not found")
    return _one(record)


@router.post("/business-profiles/")
def create_profile(payload: sc.CreateBusinessProfilePayload):
    data = payload.model_dump()
    data["id"] = db.gen_id("business_profiles", "BIZ")
    data["updatedAt"] = "now"
    return _one(db.insert("business_profiles", data))


@router.put("/business-profiles/{profile_id}/")
def put_profile(profile_id: str, payload: sc.CreateBusinessProfilePayload):
    record = db.get("business_profiles", profile_id)
    if not record:
        raise HTTPException(404, "Business profile not found")
    data = payload.model_dump()
    record.update(data)
    record["readiness"] = min(40 + len(data.get("certifications", []) or []) * 8, 100)
    record["updatedAt"] = "now"
    return _one(record)


@router.patch("/business-profiles/{profile_id}/")
def update_profile(profile_id: str, payload: dict):
    record = db.update("business_profiles", profile_id, payload)
    if not record:
        raise HTTPException(404, "Business profile not found")
    return _one(record)


@router.post("/business-profiles/{profile_id}/certifications/")
def update_certifications(profile_id: str, payload: sc.UpdateCertificationsPayload):
    record = db.get("business_profiles", profile_id)
    if not record:
        raise HTTPException(404, "Business profile not found")
    record["certifications"] = payload.certifications
    record["readiness"] = min(40 + len(payload.certifications) * 8, 100)
    record["updatedAt"] = "now"
    return _one(record)


@router.get("/business-profiles/dashboard/summary/")
def dashboard_summary():
    """Ringkasan dashboard berbasis role (Admin vs Exporter/UMKM)."""
    users = db.all("users")
    admin = next((u for u in users if u.get("role") == "Admin"), None)
    products = db.all("products")
    catalogs = db.all("catalogs")
    profiles = db.all("business_profiles")
    requests = db.all("buyer_requests")
    role_counts: dict[str, int] = {}
    for u in users:
        role_counts[str(u.get("role", "Exporter"))] = role_counts.get(str(u.get("role", "Exporter")), 0) + 1
    has_profile = any(p.get("owner") or p.get("companyName") for p in profiles)
    return {"data": {
        "role": (admin or {}).get("role", "Exporter"),
        "has_business_profile": has_profile,
        "business_profile": profiles[0] if profiles else None,
        "counts": {
            "products": len(products),
            "catalogs": len(catalogs),
            "buyer_requests": len(requests),
            "business_profiles": len(profiles),
            "users": len(users),
            "users_by_role": role_counts,
        },
    }, "meta": {}}


# ----------------------------------------------------------------------------
# BUYERS
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# BUYER PROFILES (role Buyer) — didefinisikan sebelum route parameterized
# ----------------------------------------------------------------------------
@router.post("/buyers/profile/")
def create_buyer_profile(payload: sc.CreateBuyerProfilePayload):
    data = payload.model_dump()
    existing = db.get_by("buyer_profiles", userId="current")
    if existing:
        existing.update(data)
        existing["updatedAt"] = "now"
        return _one(existing)
    record = db.insert("buyer_profiles", {
        "id": db.gen_id("buyer_profiles", "BYP"),
        "userId": "current",
        **data,
        "createdAt": "now",
    })
    return _one(record)


@router.get("/buyers/profile/me/")
def get_my_buyer_profile():
    record = db.get_by("buyer_profiles", userId="current")
    if not record:
        record = db.get_by("buyer_profiles", userId="U-003")
    if not record:
        raise HTTPException(404, "Buyer profile not found")
    return _one(record)


@router.get("/buyers/my-profile/")
def get_my_buyer_profile_alias():
    return get_my_buyer_profile()


@router.put("/buyers/profile/{profile_id}/")
def update_buyer_profile(profile_id: str, payload: sc.UpdateBuyerProfilePayload):
    record = db.get("buyer_profiles", profile_id)
    if not record:
        raise HTTPException(404, "Buyer profile not found")
    data = payload.model_dump()
    record.update(data)
    record["updatedAt"] = "now"
    return _one(record)


@router.get("/buyers/")
def list_buyers(search: str = "", status: str = "", limit: int = 0, offset: int = 0):
    return _filtered_query("buyers", search=search, search_fields=("name", "country", "segment"), status=status, limit=limit, offset=offset)


@router.get("/buyers/{buyer_id}/")
def get_buyer(buyer_id: str):
    record = db.get("buyers", buyer_id)
    if not record:
        raise HTTPException(404, "Buyer not found")
    return _one(record)


@router.post("/buyers/")
def create_buyer(payload: sc.CreateBuyerPayload):
    data = payload.model_dump()
    data.update({
        "id": db.gen_id("buyers", "BUY"),
        "status": "Lead",
        "fitScore": 50,
        "estimatedAnnualValue": 0,
        "notes": [],
        "signals": [],
        "updatedAt": "now",
        "paymentProfile": "TBD",
        "lastContact": "New",
        "nextStep": "Qualify the lead",
        "contact": {"name": payload.name, "role": "Contact", "email": "", "phone": ""},
    })
    return _one(db.insert("buyers", data))


@router.post("/buyers/{buyer_id}/qualify/")
def qualify_buyer(buyer_id: str):
    record = db.get("buyers", buyer_id)
    if not record:
        raise HTTPException(404, "Buyer not found")
    record["status"] = "Qualified"
    record["fitScore"] = max(record.get("fitScore", 50), 60)
    record["updatedAt"] = "now"
    return _one(record)


@router.post("/buyers/{buyer_id}/contacts/")
def log_buyer_contact(buyer_id: str, payload: dict):
    record = db.get("buyers", buyer_id)
    if not record:
        raise HTTPException(404, "Buyer not found")
    record.setdefault("notes", []).append(payload.get("note", ""))
    record["lastContact"] = "now"
    record["updatedAt"] = "now"
    return _one(record)


# ----------------------------------------------------------------------------
# BUYER REQUESTS
# ----------------------------------------------------------------------------
@router.get("/buyer-requests/")
def list_buyer_requests(search: str = "", status: str = "", limit: int = 0, offset: int = 0):
    return _filtered_query("buyer_requests", search=search, search_fields=("subject", "destination", "buyerId"), status=status, limit=limit, offset=offset)


@router.get("/buyer-requests/{request_id}/")
def get_buyer_request(request_id: str):
    record = db.get("buyer_requests", request_id)
    if not record:
        raise HTTPException(404, "Buyer request not found")
    return _one(record)


@router.post("/buyer-requests/")
def create_buyer_request(payload: sc.CreateBuyerRequestPayload):
    data = payload.model_dump()
    data["id"] = db.gen_id("buyer_requests", "BRQ")
    data["status"] = "Open"
    data["createdAt"] = "now"
    data["updatedAt"] = "now"
    record = db.insert("buyer_requests", data)
    # Trigger matching on-demand
    from app.services.matching import match_buyer_request
    record["matches"] = match_buyer_request(record)
    return _one(record)


@router.put("/buyer-requests/{request_id}/")
def update_buyer_request(request_id: str, payload: dict):
    record = db.get("buyer_requests", request_id)
    if not record:
        raise HTTPException(404, "Buyer request not found")
    for key in ("subject", "destination", "quantity", "productId", "buyerId", "deadline", "requirements",
                "product_category", "hs_code_target", "spec_requirements", "target_volume", "keyword_tags",
                "min_rank_required"):
        if payload.get(key) is not None:
            record[key] = payload[key]
    record["updatedAt"] = "now"
    from app.services.matching import match_buyer_request
    record["matches"] = match_buyer_request(record)
    return _one(record)


@router.patch("/buyer-requests/{request_id}/status/")
def update_buyer_request_status(request_id: str, payload: sc.UpdateBuyerRequestStatusPayload):
    record = db.get("buyer_requests", request_id)
    if not record:
        raise HTTPException(404, "Buyer request not found")
    record["status"] = payload.status
    if payload.selected_catalog or payload.selected_catalog_id:
        record["selectedCatalog"] = payload.selected_catalog_id or payload.selected_catalog
    if payload.umkm or payload.umkm_id:
        record["selectedUmkm"] = payload.umkm_id or payload.umkm
    record["updatedAt"] = "now"
    return _one(record)


@router.delete("/buyer-requests/{request_id}/")
def delete_buyer_request(request_id: str):
    record = db.get("buyer_requests", request_id)
    if not record:
        raise HTTPException(404, "Buyer request not found")
    db.delete("buyer_requests", request_id)
    return {"data": {"status": "deleted", "id": request_id}, "meta": {}}


@router.post("/buyer-requests/{request_id}/match/")
def match_buyer_request(request_id: str):
    record = db.get("buyer_requests", request_id)
    if not record:
        raise HTTPException(404, "Buyer request not found")
    from app.services.matching import match_buyer_request as run_match
    record["matches"] = run_match(record)
    if record["matches"]:
        record["status"] = "Matched"
        _notify(
            f"Buyer request {record.get('subject', '')} matched",
            f"{len(record['matches'])} katalog cocok ditemukan.",
            "Buyer Requests", "Info", f"/buyer-requests/{request_id}",
        )
    record["updatedAt"] = "now"
    return _one(record)


@router.get("/buyer-requests/{request_id}/matched-catalogs/")
def get_matched_catalogs(request_id: str):
    record = db.get("buyer_requests", request_id)
    if not record:
        raise HTTPException(404, "Buyer request not found")
    from app.services.matching import match_buyer_request as run_match
    matches = record.get("matches") or run_match(record)
    return {"data": matches, "meta": {}}


@router.get("/buyer-requests/{request_id}/matched-umkm/")
def get_matched_umkm(request_id: str):
    record = db.get("buyer_requests", request_id)
    if not record:
        raise HTTPException(404, "Buyer request not found")
    from app.services.matching import match_buyer_request as run_match
    matches = record.get("matches") or run_match(record)
    for m in matches:
        catalog = db.get("catalogs", str(m.get("catalogId", "")))
        if catalog:
            m["catalogTitle"] = catalog.get("title", "")
            m["contactInfo"] = {"phone": catalog.get("contactPhone", ""), "email": catalog.get("contactEmail", "")}
            m["catalog"] = catalog
    return {"data": matches, "meta": {}}


# ----------------------------------------------------------------------------
# FORWARDERS
# ----------------------------------------------------------------------------
# (rute statis profile/rekomendasi didefinisikan sebelum route parameterized)
@router.post("/forwarders/profile/")
def create_forwarder_profile(payload: sc.CreateForwarderProfilePayload):
    data = payload.model_dump()
    existing = db.get_by("forwarder_profiles", userId="current")
    if existing:
        existing.update(data)
        existing["updatedAt"] = "now"
        return _one(existing)
    record = db.insert("forwarder_profiles", {
        "id": db.gen_id("forwarder_profiles", "FWP"),
        "userId": "current",
        **data,
        "averageRating": 0,
        "totalReviews": 0,
        "createdAt": "now",
    })
    return _one(record)


@router.get("/forwarders/profile/me/")
def get_my_forwarder_profile():
    record = db.get_by("forwarder_profiles", userId="current")
    if not record:
        record = db.get_by("forwarder_profiles", userId="U-001")
    if not record:
        raise HTTPException(404, "Forwarder profile not found")
    return _one(record)


@router.get("/forwarders/my-profile/")
def get_my_forwarder_profile_alias():
    return get_my_forwarder_profile()


@router.put("/forwarders/profile/{profile_id}/")
def update_forwarder_profile(profile_id: str, payload: sc.UpdateForwarderProfilePayload):
    record = db.get("forwarder_profiles", profile_id)
    if not record:
        raise HTTPException(404, "Forwarder profile not found")
    data = payload.model_dump()
    for key in ("companyName", "contactInfo", "specializationRoutes", "serviceTypes"):
        if data.get(key) is not None:
            record[key] = data[key]
    record["updatedAt"] = "now"
    return _one(record)


@router.get("/forwarders/recommendations/")
def forwarder_recommendations(destination_country: str):
    from app.services.forwarders import get_recommendations
    return {"data": get_recommendations(destination_country), "meta": {}}


@router.get("/forwarders/")
def list_forwarders(search: str = "", status: str = "", min_rating: float = 0, limit: int = 0, offset: int = 0):
    items = db.all("forwarders")
    if search:
        q = search.lower()
        items = [r for r in items if q in str(r.get("name", "")).lower() or q in str(r.get("coverage", "")).lower()]
    if status:
        items = [r for r in items if str(r.get("status", "")).lower() == status.lower()]
    if min_rating:
        items = [r for r in items if float(r.get("averageRating", 0) or 0) >= min_rating]
    total = len(items)
    if limit > 0:
        items = items[offset:offset + limit]
    return {"data": [_serialize(r) for r in items], "meta": {"total": total, "limit": limit, "offset": offset, "count": len(items)}}


@router.get("/forwarders/{forwarder_id}/")
def get_forwarder(forwarder_id: str):
    record = db.get("forwarders", forwarder_id)
    if not record:
        raise HTTPException(404, "Forwarder not found")
    return _one(record)


@router.post("/forwarders/")
def create_forwarder(payload: sc.CreateForwarderPayload):
    data = payload.model_dump()
    data.update({
        "id": db.gen_id("forwarders", "FWD"),
        "status": "In Review",
        "onTimeRate": 0,
        "quoteSpeed": "TBD",
        "lanes": [],
        "averageRating": 0,
        "totalReviews": 0,
        "updatedAt": "now",
    })
    return _one(db.insert("forwarders", data))


@router.post("/forwarders/{forwarder_id}/request-quote/")
def request_forwarder_quote(forwarder_id: str):
    record = db.get("forwarders", forwarder_id)
    if not record:
        raise HTTPException(404, "Forwarder not found")
    record["lastQuoteRequest"] = "now"
    return _one(record)


# ----------------------------------------------------------------------------
# FORWARDER REVIEWS / STATISTIK
# ----------------------------------------------------------------------------
@router.post("/forwarders/{forwarder_id}/reviews/")
def create_forwarder_review(forwarder_id: str, payload: sc.CreateForwarderReviewPayload):
    record = db.get("forwarders", forwarder_id)
    if not record:
        raise HTTPException(404, "Forwarder not found")
    if payload.rating < 1 or payload.rating > 5:
        raise HTTPException(422, "Rating must be 1-5")
    review = db.insert("forwarder_reviews", {
        "id": db.gen_id("forwarder_reviews", "REV"),
        "forwarderId": forwarder_id,
        "rating": payload.rating,
        "reviewText": payload.review_text,
        "umkmId": "U-002",
        "reviewerName": "Rizal Fahmi",
        "createdAt": "now",
    })
    from app.services.forwarders import recalculate_rating
    recalculate_rating(record)
    return _one(review)


@router.put("/forwarders/{forwarder_id}/reviews/{review_id}/")
def update_forwarder_review(forwarder_id: str, review_id: str, payload: sc.UpdateForwarderReviewPayload):
    review = db.get("forwarder_reviews", review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    if payload.rating < 1 or payload.rating > 5:
        raise HTTPException(422, "Rating must be 1-5")
    review["rating"] = payload.rating
    review["reviewText"] = payload.review_text
    review["updatedAt"] = "now"
    record = db.get("forwarders", forwarder_id)
    if record:
        from app.services.forwarders import recalculate_rating
        recalculate_rating(record)
    return _one(review)


@router.delete("/forwarders/{forwarder_id}/reviews/{review_id}/delete/")
def delete_forwarder_review(forwarder_id: str, review_id: str):
    review = db.get("forwarder_reviews", review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    db.delete("forwarder_reviews", review_id)
    record = db.get("forwarders", forwarder_id)
    if record:
        from app.services.forwarders import recalculate_rating
        recalculate_rating(record)
    return {"data": {"status": "deleted"}, "meta": {}}


@router.get("/forwarders/{forwarder_id}/statistics/")
def forwarder_statistics(forwarder_id: str):
    from app.services.forwarders import get_statistics
    stats = get_statistics(forwarder_id)
    if not stats:
        raise HTTPException(404, "Forwarder not found")
    return {"data": stats, "meta": {}}


# ----------------------------------------------------------------------------
# CATALOGS
# ----------------------------------------------------------------------------
@router.get("/catalogs/")
def list_catalogs(search: str = "", status: str = "", limit: int = 0, offset: int = 0):
    return _filtered_query("catalogs", search=search, search_fields=("title", "targetMarket", "productId"), status=status, limit=limit, offset=offset)


@router.get("/catalogs/forwarder/")
def list_forwarder_catalogs(search: str = "", tag: str = "", min_price: float = 0, max_price: float = 0):
    items = [c for c in db.all("catalogs") if str(c.get("status", "")).lower() == "published"]
    if search:
        items = [c for c in items if search.lower() in str(c.get("title", "")).lower() or search.lower() in str(c.get("description", "")).lower()]
    if tag:
        items = [c for c in items if tag.lower() in [str(t).lower() for t in (c.get("tags") or [])]]
    if min_price:
        items = [c for c in items if float(c.get("basePriceExw") or 0) >= min_price]
    if max_price:
        items = [c for c in items if float(c.get("basePriceExw") or 0) <= max_price]
    for item in items:
        product = db.get("products", str(item.get("productId", ""))) if item.get("productId") else None
        item["sellerName"] = item.get("owner", "") or (product or {}).get("origin", "")
        item["sellerId"] = item.get("ownerId", "")
    return {"data": items, "meta": {}}


@router.get("/catalogs/public/")
def list_public_catalogs(search: str = "", tag: str = "", min_price: float = 0, max_price: float = 0):
    items = [c for c in db.all("catalogs") if str(c.get("status", "")).lower() == "published"]
    if search:
        items = [c for c in items if search.lower() in str(c.get("title", "")).lower() or search.lower() in str(c.get("description", "")).lower()]
    if tag:
        items = [c for c in items if tag.lower() in [str(t).lower() for t in (c.get("tags") or [])]]
    if min_price:
        items = [c for c in items if float(c.get("basePriceExw") or 0) >= min_price]
    if max_price:
        items = [c for c in items if float(c.get("basePriceExw") or 0) <= max_price]
    return {"data": items, "meta": {}}


@router.get("/catalogs/{catalog_id}/")
def get_catalog(catalog_id: str):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    record["images"] = db.find("catalog_images", catalogId=catalog_id)
    record["variantTypes"] = db.find("catalog_variant_types", catalogId=catalog_id)
    product = db.get("products", str(record.get("productId", ""))) if record.get("productId") else None
    if product:
        record["sellerName"] = record.get("owner", "") or product.get("origin", "")
    return _one(record)


@router.post("/catalogs/")
def create_catalog(payload: sc.CreateCatalogPayload):
    data = payload.model_dump(exclude_none=True)
    data.update({
        "id": db.gen_id("catalogs", "CAT"),
        "status": "Draft",
        "readiness": 40,
        "incoterms": ["EXW", "FOB"],
        "highlights": data.get("highlights") or [],
        "specifications": data.get("specifications") or [],
        "tags": data.get("tags") or [],
        "images": 0,
        "variants": [],
        "basePriceExw": data.get("base_price_exw"),
        "exportDescription": "",
        "technicalSpecs": [],
        "safetyInfo": [],
        "updatedAt": "now",
    })
    return _one(db.insert("catalogs", data))


@router.put("/catalogs/{catalog_id}/")
def update_catalog(catalog_id: str, payload: sc.UpdateCatalogPayload):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    data = payload.model_dump(exclude_none=True)
    if data.get("is_published") is not None:
        record["status"] = "Published" if data["is_published"] else "Draft"
        data.pop("is_published")
        if record["status"] == "Published":
            record["readiness"] = max(record.get("readiness", 0), 95)
    record.update(data)
    record["updatedAt"] = "now"
    return _one(record)


@router.delete("/catalogs/{catalog_id}/")
def delete_catalog(catalog_id: str):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    db.delete("catalogs", catalog_id)
    for img in db.find("catalog_images", catalogId=catalog_id):
        db.delete("catalog_images", img.get("id"))
    for vt in db.find("catalog_variant_types", catalogId=catalog_id):
        db.delete("catalog_variant_types", vt.get("id"))
        for opt in db.find("catalog_variant_options", variantTypeId=vt.get("id")):
            db.delete("catalog_variant_options", opt.get("id"))
    return {"data": {"status": "deleted", "id": catalog_id}, "meta": {}}


@router.post("/catalogs/{catalog_id}/publish/")
def publish_catalog(catalog_id: str):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    record["status"] = "Published"
    record["readiness"] = max(record.get("readiness", 0), 95)
    record["updatedAt"] = "now"
    return _one(record)


@router.post("/catalogs/{catalog_id}/unpublish/")
def unpublish_catalog(catalog_id: str):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    record["status"] = "Draft"
    record["updatedAt"] = "now"
    return _one(record)


@router.post("/catalogs/{catalog_id}/generate-description/")
def generate_catalog_description(catalog_id: str):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    product = db.get("products", str(record.get("productId", ""))) if record.get("productId") else record
    from app.services.market_intel import generate_catalog_description as gen_desc
    result = gen_desc(product or record, save_to_catalog=True, catalog=record)
    return {"data": result, "meta": {}}


# ----------------------------------------------------------------------------
# CATALOG IMAGES
# ----------------------------------------------------------------------------
@router.get("/catalogs/{catalog_id}/images/")
def list_catalog_images(catalog_id: str):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    return _list_query("catalog_images")


@router.post("/catalogs/{catalog_id}/images/")
def add_catalog_image(catalog_id: str, payload: dict):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    image = db.insert("catalog_images", {
        "id": db.gen_id("catalog_images", "IMG"),
        "catalogId": catalog_id,
        "imageUrl": payload.get("image_url") or payload.get("imageUrl") or "",
        "altText": payload.get("alt_text") or payload.get("altText") or "",
        "sortOrder": payload.get("sort_order") or payload.get("sortOrder") or 0,
        "isPrimary": payload.get("is_primary") or payload.get("isPrimary") or False,
        "createdAt": "now",
    })
    record["images"] = len(db.find("catalog_images", catalogId=catalog_id))
    record["updatedAt"] = "now"
    return _one(image)


@router.put("/catalogs/{catalog_id}/images/{image_id}/")
def update_catalog_image(catalog_id: str, image_id: str, payload: dict):
    image = db.get("catalog_images", image_id)
    if not image:
        raise HTTPException(404, "Image not found")
    for key in ("imageUrl", "altText", "sortOrder", "isPrimary"):
        mapped = {"imageUrl": "image_url", "altText": "alt_text", "sortOrder": "sort_order", "isPrimary": "is_primary"}[key]
        if payload.get(mapped) is not None or payload.get(key) is not None:
            image[key] = payload.get(mapped) if payload.get(mapped) is not None else payload.get(key)
    image["updatedAt"] = "now"
    return _one(image)


@router.delete("/catalogs/{catalog_id}/images/{image_id}/")
def delete_catalog_image(catalog_id: str, image_id: str):
    image = db.get("catalog_images", image_id)
    if not image:
        raise HTTPException(404, "Image not found")
    db.delete("catalog_images", image_id)
    record = db.get("catalogs", catalog_id)
    if record:
        record["images"] = len(db.find("catalog_images", catalogId=catalog_id))
    return {"data": {"status": "deleted"}, "meta": {}}


# ----------------------------------------------------------------------------
# CATALOG VARIANTS
# ----------------------------------------------------------------------------
_PREDEFINED_VARIANT_TYPES = [
    {"type_code": "color", "type_name": "Color"},
    {"type_code": "size", "type_name": "Size"},
    {"type_code": "material", "type_name": "Material"},
    {"type_code": "flavor", "type_name": "Flavor"},
    {"type_code": "weight", "type_name": "Weight"},
    {"type_code": "style", "type_name": "Style"},
    {"type_code": "pattern", "type_name": "Pattern"},
    {"type_code": "custom", "type_name": "Custom"},
]


@router.get("/catalogs/{catalog_id}/variant-types/")
def list_catalog_variant_types(catalog_id: str):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    types = db.find("catalog_variant_types", catalogId=catalog_id)
    for vt in types:
        vt["options"] = db.find("catalog_variant_options", variantTypeId=vt.get("id"))
    return {"data": types, "meta": {"predefined_types": _PREDEFINED_VARIANT_TYPES}}


@router.post("/catalogs/{catalog_id}/variant-types/")
def add_catalog_variant_type(catalog_id: str, payload: sc.AddVariantTypePayload):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    vt = db.insert("catalog_variant_types", {
        "id": db.gen_id("catalog_variant_types", "VT"),
        "catalogId": catalog_id,
        "typeCode": payload.type_code,
        "typeName": payload.type_name,
        "sortOrder": payload.sort_order,
        "createdAt": "now",
    })
    for option in payload.options:
        db.insert("catalog_variant_options", {
            "id": db.gen_id("catalog_variant_options", "VO"),
            "variantTypeId": vt.get("id"),
            "optionName": option,
            "sortOrder": 0,
            "isAvailable": True,
            "createdAt": "now",
        })
    vt["options"] = db.find("catalog_variant_options", variantTypeId=vt.get("id"))
    return _one(vt)


@router.put("/catalogs/{catalog_id}/variant-types/{type_id}/")
def update_catalog_variant_type(catalog_id: str, type_id: str, payload: sc.UpdateVariantTypePayload):
    vt = db.get("catalog_variant_types", type_id)
    if not vt:
        raise HTTPException(404, "Variant type not found")
    if payload.type_name:
        vt["typeName"] = payload.type_name
    vt["typeCode"] = payload.type_code
    if payload.sort_order is not None:
        vt["sortOrder"] = payload.sort_order
    vt["updatedAt"] = "now"
    return _one(vt)


@router.delete("/catalogs/{catalog_id}/variant-types/{type_id}/")
def delete_catalog_variant_type(catalog_id: str, type_id: str):
    vt = db.get("catalog_variant_types", type_id)
    if not vt:
        raise HTTPException(404, "Variant type not found")
    db.delete("catalog_variant_types", type_id)
    for opt in db.find("catalog_variant_options", variantTypeId=type_id):
        db.delete("catalog_variant_options", opt.get("id"))
    return {"data": {"status": "deleted"}, "meta": {}}


@router.get("/catalogs/{catalog_id}/variant-types/{type_id}/options/")
def list_catalog_variant_options(catalog_id: str, type_id: str):
    return {"data": db.find("catalog_variant_options", variantTypeId=type_id), "meta": {}}


@router.post("/catalogs/{catalog_id}/variant-types/{type_id}/options/")
def add_catalog_variant_option(catalog_id: str, type_id: str, payload: sc.AddVariantOptionPayload):
    vt = db.get("catalog_variant_types", type_id)
    if not vt:
        raise HTTPException(404, "Variant type not found")
    option = db.insert("catalog_variant_options", {
        "id": db.gen_id("catalog_variant_options", "VO"),
        "variantTypeId": type_id,
        "optionName": payload.option_name,
        "sortOrder": payload.sort_order,
        "isAvailable": payload.is_available,
        "createdAt": "now",
    })
    return _one(option)


@router.put("/catalogs/{catalog_id}/variant-types/{type_id}/options/{option_id}/")
def update_catalog_variant_option(catalog_id: str, type_id: str, option_id: str, payload: sc.UpdateVariantOptionPayload):
    option = db.get("catalog_variant_options", option_id)
    if not option:
        raise HTTPException(404, "Variant option not found")
    option["optionName"] = payload.option_name
    option["sortOrder"] = payload.sort_order
    option["isAvailable"] = payload.is_available
    option["updatedAt"] = "now"
    return _one(option)


@router.delete("/catalogs/{catalog_id}/variant-types/{type_id}/options/{option_id}/")
def delete_catalog_variant_option(catalog_id: str, type_id: str, option_id: str):
    option = db.get("catalog_variant_options", option_id)
    if not option:
        raise HTTPException(404, "Variant option not found")
    db.delete("catalog_variant_options", option_id)
    return {"data": {"status": "deleted"}, "meta": {}}


# ----------------------------------------------------------------------------
# CATALOG AI
# ----------------------------------------------------------------------------
@router.get("/catalogs/{catalog_id}/ai/market-intelligence/")
def get_catalog_market_intelligence(catalog_id: str):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    mi = db.get_by("market_intelligence", productId=str(record.get("productId", "")))
    if not mi:
        raise HTTPException(404, "Market intelligence not found")
    return _one(mi)


@router.post("/catalogs/{catalog_id}/ai/market-intelligence/")
def create_catalog_market_intelligence(catalog_id: str):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    product = db.get("products", str(record.get("productId", ""))) if record.get("productId") else record
    from app.services.market_intel import generate_market_intelligence
    result = generate_market_intelligence(product or record)
    existing = db.get_by("market_intelligence", productId=str(record.get("productId", "")))
    if existing:
        existing.update(result)
        db.save(existing)
        return _one(existing)
    return _one(db.insert("market_intelligence", {"id": db.gen_id("market_intelligence", "MI"), **result}))


@router.get("/catalogs/{catalog_id}/ai/pricing/")
def get_catalog_pricing(catalog_id: str):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    pr = db.get_by("pricing_results", productId=str(record.get("productId", "")))
    if not pr:
        raise HTTPException(404, "Pricing result not found")
    return _one(pr)


@router.post("/catalogs/{catalog_id}/ai/pricing/")
def create_catalog_pricing(catalog_id: str, payload: dict):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    product = db.get("products", str(record.get("productId", ""))) if record.get("productId") else record
    from app.services.market_intel import generate_product_pricing
    cogs = payload.get("cogs_per_unit_idr") or payload.get("cogsPerUnitIdr") or 0
    margin = payload.get("target_margin_percent") or payload.get("targetMarginPercent") or 30
    country = payload.get("target_country_code") or payload.get("targetCountryCode") or "JP"
    result = generate_product_pricing(product or record, float(cogs), float(margin), str(country))
    existing = db.get_by("pricing_results", productId=str(record.get("productId", "")))
    if existing:
        existing.update(result)
        db.save(existing)
        return _one(existing)
    return _one(db.insert("pricing_results", {"id": db.gen_id("pricing_results", "PRC"), **result}))


@router.post("/catalogs/{catalog_id}/ai/description/")
def generate_catalog_ai_description(catalog_id: str, payload: dict):
    record = db.get("catalogs", catalog_id)
    if not record:
        raise HTTPException(404, "Catalog not found")
    product = db.get("products", str(record.get("productId", ""))) if record.get("productId") else record
    from app.services.market_intel import generate_catalog_description
    save = bool(payload.get("save_to_catalog", False))
    result = generate_catalog_description(product or record, save_to_catalog=save, catalog=record if save else None)
    return {"data": result, "meta": {}}



# ----------------------------------------------------------------------------
# COSTING
# ----------------------------------------------------------------------------
# (exchange rate routes didefinisikan sebelum route parameterized {costing_id})
@router.get("/costing/exchange-rate/")
def get_exchange_rate_endpoint():
    from app.services.pricing import get_exchange_rate
    return _one(get_exchange_rate())


@router.put("/costing/exchange-rate/")
def update_exchange_rate(payload: dict):
    from app.services.pricing import set_exchange_rate
    rate = payload.get("rate") or payload.get("exchange_rate")
    if not rate:
        raise HTTPException(422, "rate is required")
    return _one(set_exchange_rate(float(rate), source="manual"))


@router.post("/costing/exchange-rate/refresh/")
def refresh_exchange_rate():
    from app.services.pricing import fetch_live_exchange_rate, set_exchange_rate, FALLBACK_RATE
    rate = fetch_live_exchange_rate()
    if rate is None:
        rate = FALLBACK_RATE
        source = "fallback"
    else:
        source = "manual_refresh"
    return _one(set_exchange_rate(float(rate), source=source))


@router.post("/costing/compare/")
def compare_costings(payload: sc.BatchActionPayload):
    """Bandingkan beberapa skenario costing berdampingan (diadaptasi dari costing comparison ExportReadyAI).

    Kirim daftar costing ids -> tabel perbandingan + rekomendasi terbaik.
    """
    if not payload.ids:
        raise HTTPException(422, "ids wajib diisi")
    items = []
    for cid in payload.ids:
        record = db.get("costing", cid)
        if record:
            items.append(record)
    if not items:
        raise HTTPException(404, "Costing not found")
    columns = ["id", "title", "destination", "incoterm", "margin", "exchangeRate", "exwPrice", "fobPrice", "cifPrice", "status"]
    rows = [[c.get(k) for k in columns] for c in items]

    def _num(c, key):
        v = c.get(key)
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    best_margin = max(items, key=lambda c: _num(c, "margin") or -1, default=None)
    best_fob = min(items, key=lambda c: _num(c, "fobPrice") or float("inf"), default=None)
    recommendation = None
    if best_margin:
        recommendation = {
            "costingId": best_margin["id"],
            "title": best_margin.get("title"),
            "reason": f"Margin tertinggi ({best_margin.get('margin')}%)",
            "fobPrice": best_margin.get("fobPrice"),
            "cifPrice": best_margin.get("cifPrice"),
        }
    return {
        "data": {
            "columns": columns,
            "rows": rows,
            "items": items,
            "count": len(items),
            "bestMargin": {"id": best_margin.get("id"), "title": best_margin.get("title"), "margin": best_margin.get("margin")} if best_margin else None,
            "bestFobPrice": {"id": best_fob.get("id"), "title": best_fob.get("title"), "fobPrice": best_fob.get("fobPrice")} if best_fob else None,
            "recommendation": recommendation,
        },
        "meta": {},
    }


@router.get("/costing/{costing_id}/pdf/")
def costing_pdf(costing_id: str):
    record = db.get("costing", costing_id)
    if not record:
        raise HTTPException(404, "Costing not found")
    from app.services.pricing import build_costing_pdf
    pdf_bytes = build_costing_pdf(record)
    from fastapi.responses import Response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="costing-{costing_id}.pdf"'},
    )


@router.get("/costing/")
def list_costing():
    return _list_query("costing")


@router.get("/costing/{costing_id}/")
def get_costing(costing_id: str):
    record = db.get("costing", costing_id)
    if not record:
        raise HTTPException(404, "Costing not found")
    return _one(record)


@router.post("/costing/")
def create_costing(payload: sc.CreateCostingPayload):
    from app.services import pricing as pricing_svc

    data = payload.model_dump()
    margin = payload.margin if payload.margin is not None else payload.targetMargin
    cogs = payload.cogs_per_unit_idr if payload.cogs_per_unit_idr is not None else (payload.cogsPerUnitIdr or 0)
    packing = payload.packing_cost_idr if payload.packing_cost_idr is not None else (payload.packingCostIdr or 0)
    distance = payload.distance_km if payload.distance_km is not None else (payload.distanceKm or 200)

    # Fallback COGS dari product bila tidak dikirim frontend
    product = db.get("products", str(payload.productId or "")) if payload.productId else None
    if not cogs:
        cogs = float((product or {}).get("cogsPerUnitIdr") or 10000)

    calc = pricing_svc.calculate_full_costing(
        cogs_idr=float(cogs or 0),
        packing_cost_idr=float(packing or 0),
        margin_percent=float(margin or 20),
        destination=str(payload.destination),
        distance_km=float(distance or 200),
        product_volume_m3=0,
        product_weight_kg=0,
    )
    data.update({
        "id": db.gen_id("costing", "CST"),
        "margin": margin,
        "currency": "USD",
        "status": "Ready",
        "cogs_per_unit_idr": cogs,
        "exchangeRate": calc["exchangeRate"],
        "exchangeSource": calc["exchangeSource"],
        "exwPrice": calc["exwPrice"],
        "fobPrice": calc["fobPrice"],
        "cifPrice": calc["cifPrice"],
        "landedCost": round(calc["cifPrice"] * 1.12, 2),
        "profit": round(calc["exwPrice"] - (cogs + packing) / calc["exchangeRate"], 2),
        "confidence": 84,
        "lines": calc["lines"],
        "container": calc["container"],
        "risks": ["Freight estimate not converted to booking"] if not payload.destination else [],
        "updatedAt": "now",
    })
    return _one(db.insert("costing", data))


@router.put("/costing/{costing_id}/")
def update_costing(costing_id: str, payload: sc.UpdateCostingPayload):
    record = db.get("costing", costing_id)
    if not record:
        raise HTTPException(404, "Costing not found")
    from app.services import pricing as pricing_svc

    data = payload.model_dump(exclude_none=True)
    record.update(data)
    if payload.exchange_rate is not None:
        pricing_svc.set_exchange_rate(float(payload.exchange_rate), source="manual")
        record["exchangeRate"] = payload.exchange_rate
    margin = record.get("margin", 20)
    cogs = record.get("cogs_per_unit_idr") or record.get("cogsPerUnitIdr") or 0
    packing = record.get("packing_cost_idr") or record.get("packingCostIdr") or 0
    distance = record.get("distance_km") or record.get("distanceKm") or 200
    calc = pricing_svc.calculate_full_costing(
        cogs_idr=float(cogs or 0),
        packing_cost_idr=float(packing or 0),
        margin_percent=float(margin or 20),
        destination=str(record.get("destination", "")),
        distance_km=float(distance or 200),
    )
    record.update({
        "exchangeRate": calc["exchangeRate"],
        "exwPrice": calc["exwPrice"],
        "fobPrice": calc["fobPrice"],
        "cifPrice": calc["cifPrice"],
        "lines": calc["lines"],
        "container": calc["container"],
        "status": "Ready",
        "updatedAt": "now",
    })
    return _one(record)


@router.delete("/costing/{costing_id}/")
def delete_costing(costing_id: str):
    record = db.get("costing", costing_id)
    if not record:
        raise HTTPException(404, "Costing not found")
    db.delete("costing", costing_id)
    return {"data": {"status": "deleted", "id": costing_id}, "meta": {}}


@router.post("/costing/{costing_id}/recalculate/")
def recalculate_costing(costing_id: str):
    from app.services import pricing as pricing_svc

    record = db.get("costing", costing_id)
    if not record:
        raise HTTPException(404, "Costing not found")
    margin = record.get("margin", 20)
    cogs = record.get("cogs_per_unit_idr") or record.get("cogsPerUnitIdr") or record.get("cogs", 0)
    packing = record.get("packing_cost_idr") or record.get("packingCostIdr") or 0
    distance = record.get("distance_km") or record.get("distanceKm") or 200
    calc = pricing_svc.calculate_full_costing(
        cogs_idr=float(cogs or 0),
        packing_cost_idr=float(packing or 0),
        margin_percent=float(margin or 20),
        destination=str(record.get("destination", "")),
        distance_km=float(distance or 200),
    )
    record["status"] = "Ready"
    record["confidence"] = max(record.get("confidence", 0), 84)
    record["exchangeRate"] = calc["exchangeRate"]
    record["exwPrice"] = calc["exwPrice"]
    record["fobPrice"] = calc["fobPrice"]
    record["cifPrice"] = calc["cifPrice"]
    record["landedCost"] = round(calc["cifPrice"] * 1.12, 2)
    record["lines"] = calc["lines"]
    record["container"] = calc["container"]
    record["updatedAt"] = "now"
    return _one(record)


# ----------------------------------------------------------------------------
# MARKETS
# ----------------------------------------------------------------------------
@router.get("/markets/")
def list_markets():
    return _list_query("markets")


@router.get("/markets/{market_id}/")
def get_market(market_id: str):
    record = db.get("markets", market_id)
    if not record:
        raise HTTPException(404, "Market not found")
    return _one(record)


@router.post("/markets/")
def create_market(payload: sc.CreateMarketPayload):
    data = payload.model_dump()
    data.update({"id": db.gen_id("markets", "MKT"), "marketScore": 50, "status": "Needs Research", "updatedAt": "now"})
    return _one(db.insert("markets", data))


@router.post("/markets/{market_id}/refresh/")
def refresh_market(market_id: str):
    record = db.get("markets", market_id)
    if not record:
        raise HTTPException(404, "Market not found")
    insight = ai.ask_json(
        "You are a market intelligence analyst for Indonesian exports. Return JSON with score (0-100) and insight.",
        f"Market: {record.get('destination', '')} for {record.get('products', '')}",
        kind="market_insight",
    )
    if insight and isinstance(insight.get("score"), (int, float)):
        record["marketScore"] = max(0, min(100, int(insight["score"])))
    else:
        record["marketScore"] = min(record.get("marketScore", 0) + 5, 100)
    if insight and insight.get("insight"):
        record.setdefault("insight", insight["insight"])
    record["updatedAt"] = "now"
    return _one(record)


# ----------------------------------------------------------------------------
# RFQ
# ----------------------------------------------------------------------------
@router.get("/rfqs/")
def list_rfqs():
    return _list_query("rfqs")


@router.get("/rfqs/{rfq_id}/")
def get_rfq(rfq_id: str):
    record = db.get("rfqs", rfq_id)
    if not record:
        raise HTTPException(404, "RFQ not found")
    return _one(record)


@router.post("/rfqs/")
def create_rfq(payload: sc.CreateRFQPayload):
    data = payload.model_dump()
    data.update({
        "id": db.gen_id("rfqs", "RFQ"),
        "status": "Open",
        "matchScore": 0,
        "requirements": [],
        "matches": [],
        "updatedAt": "now",
    })
    return _one(db.insert("rfqs", data))


@router.post("/rfqs/{rfq_id}/shortlist/")
def shortlist_rfq(rfq_id: str, payload: dict):
    record = db.get("rfqs", rfq_id)
    if not record:
        raise HTTPException(404, "RFQ not found")
    record.setdefault("matches", [])
    record["matches"].append({"supplier": payload.get("supplier", ""), "score": 50, "reason": "Shortlisted"})
    record["status"] = "Matching"
    return _one(record)


# ----------------------------------------------------------------------------
# QUOTATIONS
# ----------------------------------------------------------------------------
@router.get("/quotations/")
def list_quotations():
    return _list_query("quotations")


@router.get("/quotations/{quotation_id}/")
def get_quotation(quotation_id: str):
    record = db.get("quotations", quotation_id)
    if not record:
        raise HTTPException(404, "Quotation not found")
    return _one(record)


@router.post("/quotations/")
def create_quotation(payload: sc.CreateQuotationPayload):
    data = payload.model_dump()
    data.update({"id": db.gen_id("quotations", "Q"), "status": "Draft", "currency": "USD", "value": 0, "costLines": [], "updatedAt": "now"})
    return _one(db.insert("quotations", data))


@router.post("/quotations/{quotation_id}/accept/")
def accept_quotation(quotation_id: str):
    record = db.get("quotations", quotation_id)
    if not record:
        raise HTTPException(404, "Quotation not found")
    record["status"] = "Accepted"
    record["updatedAt"] = "now"
    return _one(record)


# ----------------------------------------------------------------------------
# ORDERS
# ----------------------------------------------------------------------------
@router.get("/orders/")
def list_orders():
    return _list_query("orders")


@router.get("/orders/{order_id}/")
def get_order(order_id: str):
    record = db.get("orders", order_id)
    if not record:
        raise HTTPException(404, "Order not found")
    return _one(record)


@router.post("/orders/")
def create_order(payload: sc.CreateOrderPayload):
    data = payload.model_dump()
    data.update({"id": db.gen_id("orders", "ORD"), "status": "Draft", "updatedAt": "now"})
    return _one(db.insert("orders", data))


@router.post("/orders/{order_id}/confirm/")
def confirm_order(order_id: str):
    record = db.get("orders", order_id)
    if not record:
        raise HTTPException(404, "Order not found")
    record["status"] = "Confirmed"
    record["updatedAt"] = "now"
    return _one(record)


# ----------------------------------------------------------------------------
# COMPLIANCE
# ----------------------------------------------------------------------------
@router.get("/compliance/requirements/")
def list_compliance():
    return _list_query("compliance_requirements")


@router.get("/compliance/requirements/{req_id}/")
def get_compliance(req_id: str):
    record = db.get("compliance_requirements", req_id)
    if not record:
        raise HTTPException(404, "Compliance requirement not found")
    return _one(record)


@router.post("/compliance/requirements/{req_id}/evidence/")
def upload_compliance_evidence(req_id: str, payload: dict):
    record = db.get("compliance_requirements", req_id)
    if not record:
        raise HTTPException(404, "Compliance requirement not found")
    record["currentEvidence"] = payload.get("description") or payload.get("note") or record.get("currentEvidence")
    record["status"] = "Evidence Uploaded"
    record["updatedAt"] = "now"
    _notify(
        f"Bukti diunggah untuk {record.get('title', 'requirement')}",
        record["currentEvidence"],
        "Compliance", "Info", f"/compliance/{req_id}",
    )
    return _one(record)


# ----------------------------------------------------------------------------
# DOCUMENTS
# ----------------------------------------------------------------------------
@router.get("/documents/")
def list_documents():
    return _list_query("documents")


@router.get("/documents/{document_id}/")
def get_document(document_id: str):
    record = db.get("documents", document_id)
    if not record:
        raise HTTPException(404, "Document not found")
    return _one(record)


@router.post("/documents/generate/")
def generate_document(payload: sc.GenerateDocumentPayload):
    fields = dict(payload.data or {})
    checks: list[dict] = []
    project = db.get("projects", str(payload.projectId or "")) if payload.projectId else None
    product = None
    if project:
        fields.setdefault("buyer", project.get("buyer", ""))
        fields.setdefault("destination", project.get("country", ""))
        fields.setdefault("value", project.get("value", 0))
        fields.setdefault("incoterm", project.get("incoterm", ""))
        fields.setdefault("hsCode", project.get("hsCode", ""))
        # Cari produk terkait
        pid = project.get("productId")
        if pid:
            product = db.get("products", pid)
    # Invoice number otomatis
    doc_type = payload.type or "Commercial Invoice"
    if not fields.get("invoiceNo") and doc_type.lower().startswith("commercial"):
        fields["invoiceNo"] = f"INV-{payload.projectId or 'DRAFT'}-{len(db.all('documents')) + 1:03d}"
    # Checks & validation score
    checks.append({"label": "Buyer terisi", "status": "Passed" if fields.get("buyer") else "Failed", "detail": "Buyer wajib pada dokumen komersial"})
    checks.append({"label": "HS code", "status": "Passed" if fields.get("hsCode") else "Needs Review", "detail": "HS code dari data proyek/produk"})
    if product:
        fields.setdefault("product", product.get("name", ""))
        fields.setdefault("origin", product.get("origin", ""))
        checks.append({"label": "Produk terisi", "status": "Passed", "detail": product.get("name", "")})
    if fields.get("value"):
        checks.append({"label": "Nilai dokumen", "status": "Passed", "detail": f"{fields['value']}"})
    passed = sum(1 for c in checks if c["status"] == "Passed")
    validation_score = round((passed / len(checks)) * 100) if checks else 0
    record = db.insert("documents", {
        "id": db.gen_id("documents", "DOC"),
        "projectId": payload.projectId,
        "type": doc_type,
        "status": "Draft",
        "version": "v1.0",
        "owner": "System",
        "updatedAt": "now",
        "validationScore": validation_score,
        "fields": fields,
        "checks": checks,
    })
    return _one(record)


@router.post("/documents/{document_id}/approve/")
def approve_document(document_id: str):
    record = db.get("documents", document_id)
    if not record:
        raise HTTPException(404, "Document not found")
    record["status"] = "Approved"
    record["updatedAt"] = "now"
    return _one(record)


# ----------------------------------------------------------------------------
# SHIPMENTS
# ----------------------------------------------------------------------------
@router.get("/shipments/")
def list_shipments():
    return _list_query("shipments")


@router.get("/shipments/{shipment_id}/")
def get_shipment(shipment_id: str):
    record = db.get("shipments", shipment_id)
    if not record:
        raise HTTPException(404, "Shipment not found")
    return _one(record)


@router.post("/shipments/{shipment_id}/milestones/")
def update_shipment_milestone(shipment_id: str, payload: dict):
    record = db.get("shipments", shipment_id)
    if not record:
        raise HTTPException(404, "Shipment not found")
    record.setdefault("milestones", [])
    record["milestones"].append({"label": payload.get("milestone", "Updated"), "status": "Done"})
    record["progress"] = min(record.get("progress", 0) + 15, 100)
    record["updatedAt"] = "now"
    _notify(
        f"Milestone shipment: {payload.get('milestone', 'Updated')}",
        f"Progres {record.get('progress', 0)}%.",
        "Shipments", "Info", f"/shipments/{shipment_id}",
    )
    return _one(record)


@router.post("/shipments/{shipment_id}/exceptions/resolve/")
def resolve_shipment_exception(shipment_id: str):
    record = db.get("shipments", shipment_id)
    if not record:
        raise HTTPException(404, "Shipment not found")
    record["status"] = "In Transit"
    record.pop("exception", None)
    record["updatedAt"] = "now"
    _notify("Exception shipment diselesaikan", "Shipment kembali In Transit.", "Shipments", "Info", f"/shipments/{shipment_id}")
    return _one(record)


# ----------------------------------------------------------------------------
# PAYMENTS
# ----------------------------------------------------------------------------
@router.get("/payments/")
def list_payments():
    return _list_query("payments")


@router.get("/payments/{payment_id}/")
def get_payment(payment_id: str):
    record = db.get("payments", payment_id)
    if not record:
        raise HTTPException(404, "Payment not found")
    return _one(record)


@router.post("/payments/{payment_id}/mark-received/")
def mark_payment_received(payment_id: str, payload: dict):
    record = db.get("payments", payment_id)
    if not record:
        raise HTTPException(404, "Payment not found")
    amount = payload.get("amount") or record.get("paid") or record.get("amount", 0)
    record["paid"] = amount
    record["status"] = "Settled" if amount >= record.get("amount", amount) else "Deposit Paid"
    record["updatedAt"] = "now"
    _notify(
        f"Pembayaran {record.get('status', '')}",
        f"Tercatat {amount} untuk {record.get('buyer', '')}.",
        "Payments", "Info", f"/payments/{payment_id}",
    )
    return _one(record)


@router.post("/payments/{payment_id}/send-reminder/")
def send_payment_reminder(payment_id: str):
    record = db.get("payments", payment_id)
    if not record:
        raise HTTPException(404, "Payment not found")
    record["remindersSent"] = record.get("remindersSent", 0) + 1
    return _one(record)


# ----------------------------------------------------------------------------
# TASKS
# ----------------------------------------------------------------------------
@router.get("/tasks/")
def list_tasks():
    return _list_query("tasks")


@router.get("/tasks/{task_id}/")
def get_task(task_id: str):
    record = db.get("tasks", task_id)
    if not record:
        raise HTTPException(404, "Task not found")
    return _one(record)


@router.post("/tasks/{task_id}/complete/")
def complete_task(task_id: str):
    record = db.get("tasks", task_id)
    if not record:
        raise HTTPException(404, "Task not found")
    record["status"] = "Done"
    record["updatedAt"] = "now"
    _notify(f"Task selesai: {record.get('title', '')}", "Task ditandai selesai.", "Tasks", "Info", f"/tasks/{task_id}")
    return _one(record)


@router.post("/tasks/{task_id}/assign/")
def assign_task(task_id: str, payload: dict):
    record = db.get("tasks", task_id)
    if not record:
        raise HTTPException(404, "Task not found")
    record["owner"] = payload.get("owner", record.get("owner"))
    record["status"] = "In Progress"
    return _one(record)


# ----------------------------------------------------------------------------
# SUPPLIERS
# ----------------------------------------------------------------------------
@router.get("/suppliers/")
def list_suppliers():
    return _list_query("suppliers")


@router.get("/suppliers/{supplier_id}/")
def get_supplier(supplier_id: str):
    record = db.get("suppliers", supplier_id)
    if not record:
        raise HTTPException(404, "Supplier not found")
    return _one(record)


@router.post("/suppliers/{supplier_id}/verify/")
def verify_supplier(supplier_id: str):
    record = db.get("suppliers", supplier_id)
    if not record:
        raise HTTPException(404, "Supplier not found")
    record["status"] = "Verified"
    record["complianceScore"] = max(record.get("complianceScore", 0), 90)
    return _one(record)


@router.post("/suppliers/{supplier_id}/request-evidence/")
def request_supplier_evidence(supplier_id: str):
    record = db.get("suppliers", supplier_id)
    if not record:
        raise HTTPException(404, "Supplier not found")
    record["evidenceRequested"] = record.get("evidenceRequested", 0) + 1
    record["status"] = "Needs Evidence"
    return _one(record)


# ----------------------------------------------------------------------------
# ANALYTICS
# ----------------------------------------------------------------------------
@router.get("/analytics/overview/")
def analytics_overview():
    projects = db.all("projects")
    products = db.all("products")
    buyers = db.all("buyers")
    analyses = db.all("export_analyses")
    catalogs = db.all("catalogs")
    forwarders = db.all("forwarders")
    orders = db.all("orders")
    total = sum(p.get("value", 0) or 0 for p in projects)
    total_orders = sum(o.get("value", 0) or 0 for o in orders)
    return {"data": [
        {"label": "Active projects", "value": str(len(projects)), "change": "+1 this month", "tone": "green"},
        {"label": "Pipeline value", "value": f"${total:,}", "change": "+12%", "tone": "blue"},
        {"label": "Products", "value": str(len(products)), "change": f"{sum(1 for p in products if p.get('status') == 'Enriched')} enriched", "tone": "green"},
        {"label": "Market analyses", "value": str(len(analyses)), "change": f"{sum(1 for a in analyses if a.get('status') == 'Ready')} ready", "tone": "blue"},
        {"label": "Published catalogs", "value": str(sum(1 for c in catalogs if c.get('status') == 'Published')), "change": f"{len(catalogs)} total", "tone": "green"},
        {"label": "Active buyers", "value": str(len(buyers)), "change": "CRM", "tone": "orange"},
        {"label": "Verified forwarders", "value": str(sum(1 for f in forwarders if f.get('status') == 'Verified')), "change": f"{len(forwarders)} total", "tone": "blue"},
        {"label": "Order value", "value": f"${total_orders:,}", "change": "booked", "tone": "green"},
    ], "meta": {}}


@router.post("/analytics/refresh/")
def analytics_refresh():
    return {"data": analytics_overview()["data"], "meta": {}}


# ----------------------------------------------------------------------------
# NOTIFICATIONS / AUDIT / TEAM / TEMPLATES / AUTOMATIONS / INTEGRATIONS
# ----------------------------------------------------------------------------
@router.get("/notifications/")
def list_notifications():
    return _list_query("notifications")


@router.get("/notifications/stream/")
def stream_notifications(request: Request):
    """Realtime SSE: kirim jumlah notifikasi unread setiap perubahan (polling server-side).

    Didefinisikan sebelum rute parameterized {notification_id} agar tidak tertutup.
    Client: EventSource(url, {withCredentials: true}) -> 'unread:<n>'.
    """
    from fastapi.responses import StreamingResponse

    user = None
    token = request.cookies.get("access_token")
    if token:
        try:
            payload = decode_token(token)
            user = db.get("users", payload.get("sub", ""))
        except HTTPException:
            user = None
    if not user:
        raise HTTPException(401, "Not authenticated")

    async def event_generator():
        import asyncio

        last_count = None
        while True:
            unread = [n for n in db.find("notifications") if n.get("status") == "Unread"]
            count = len(unread)
            if count != last_count:
                last_count = count
                event = {"unread_count": count, "items": unread[:5]}
                yield f"event: unread\ndata: {json.dumps(event)}\n\n"
            yield ": keep-alive\n\n"
            await asyncio.sleep(5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )


@router.post("/notifications/{notification_id}/read/")
def mark_notification_read(notification_id: str):
    record = db.get("notifications", notification_id)
    if not record:
        raise HTTPException(404, "Notification not found")
    record["status"] = "Read"
    return _one(record)


@router.post("/notifications/{notification_id}/archive/")
def archive_notification(notification_id: str):
    record = db.get("notifications", notification_id)
    if not record:
        raise HTTPException(404, "Notification not found")
    record["status"] = "Archived"
    return _one(record)


@router.get("/audit/")
def list_audit():
    return _list_query("audit_events")


@router.get("/audit/export.csv")
def export_audit_csv():
    """Ekspor audit log sebagai CSV."""
    import csv as _csv
    import io as _io
    buffer = _io.StringIO()
    writer = _csv.writer(buffer)
    writer.writerow(["time", "actor", "action", "module", "entity", "severity", "detail"])
    for event in db.all("audit_events"):
        writer.writerow([
            event.get("time", ""), event.get("actor", ""), event.get("action", ""),
            event.get("module", ""), event.get("entity", ""), event.get("severity", ""),
            event.get("detail", ""),
        ])
    from fastapi.responses import Response
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="audit-events.csv"'},
    )


@router.post("/audit/export/")
def export_audit():
    # Sinkron dengan endpoint CSV nyata; tetap pertahankan kontrak lama
    events = db.all("audit_events")
    return {"data": {"status": "queued", "count": len(events), "url": "/api/v1/audit/export.csv"}, "meta": {}}


@router.get("/team/")
def list_team():
    return _list_query("team_members")


@router.post("/team/invite/")
def invite_team(payload: dict):
    email = payload.get("email", "")
    name = email.split("@")[0] if email else ""
    record = db.insert("team_members", {
        "id": db.gen_id("team_members", "USR"),
        "email": email,
        "name": name,
        "role": payload.get("role", "Operations"),
        "status": "Invited",
        "permissions": [],
        "workload": 0,
    })
    return _one(record)


@router.post("/team/{member_id}/role/")
def update_team_member_role(member_id: str, payload: dict):
    record = db.get("team_members", member_id)
    if not record:
        raise HTTPException(404, "Team member not found")
    record["role"] = payload.get("role", record.get("role"))
    record["updatedAt"] = "now"
    return _one(record)


@router.get("/templates/")
def list_templates():
    return _list_query("templates")


@router.post("/templates/")
def create_template(payload: dict):
    record = db.insert("templates", {
        "id": db.gen_id("templates", "TPL"),
        "title": payload.get("title", "Template"),
        "category": payload.get("category", "Document"),
        "status": "Draft",
        "updatedAt": "now",
    })
    return _one(record)


@router.post("/templates/{template_id}/use/")
def use_template(template_id: str):
    record = db.get("templates", template_id)
    if not record:
        raise HTTPException(404, "Template not found")
    record["usedCount"] = record.get("usedCount", 0) + 1
    return _one(record)


@router.get("/automations/")
def list_automations():
    return _list_query("automations")


@router.post("/automations/{automation_id}/activate/")
def activate_automation(automation_id: str):
    record = db.get("automations", automation_id)
    if not record:
        raise HTTPException(404, "Automation not found")
    record["status"] = "Active"
    return _one(record)


@router.post("/automations/{automation_id}/run/")
def run_automation(automation_id: str):
    record = db.get("automations", automation_id)
    if not record:
        raise HTTPException(404, "Automation not found")
    record["runs"] = record.get("runs", 0) + 1
    record["lastRun"] = "now"
    db.save(record)
    # Notifikasi realtime agar badge SSE ikut ter-update
    db.insert("notifications", {
        "id": db.gen_id("notifications", "NTF"),
        "title": f"Automation '{record.get('name', automation_id)}' dijalankan",
        "description": f"{record.get('trigger', '')} -> {record.get('action', '')}",
        "category": "Automations",
        "status": "Unread",
        "type": "automation",
        "createdAt": "now",
        "ownerId": record.get("ownerId", "U-001"),
    })
    return _one(record)


@router.get("/integrations/")
def list_integrations():
    return _list_query("integrations")


@router.post("/integrations/{integration_id}/connect/")
def connect_integration(integration_id: str):
    record = db.get("integrations", integration_id)
    if not record:
        raise HTTPException(404, "Integration not found")
    record["status"] = "Connected"
    return _one(record)


@router.post("/integrations/{integration_id}/sync/")
def sync_integration(integration_id: str):
    record = db.get("integrations", integration_id)
    if not record:
        raise HTTPException(404, "Integration not found")
    record["lastSync"] = "now"
    return _one(record)


# ----------------------------------------------------------------------------
# KNOWLEDGE / EDUCATIONAL / CALENDAR / FILES / MESSAGES / REPORTS / BILLING
# ----------------------------------------------------------------------------
@router.get("/knowledge/")
def list_knowledge():
    return _list_query("knowledge_articles")


@router.post("/knowledge/{article_id}/publish/")
def publish_knowledge(article_id: str):
    record = db.get("knowledge_articles", article_id)
    if not record:
        raise HTTPException(404, "Article not found")
    record["status"] = "Published"
    return _one(record)


@router.get("/educational/")
def list_educational_modules():
    modules = db.all("educational_modules")
    for m in modules:
        m["articleCount"] = len(db.find("educational_articles", moduleId=m.get("id")))
    return {"data": modules, "meta": {}}


@router.get("/educational/modules/")
def list_educational_modules_v2():
    modules = db.all("educational_modules")
    for m in modules:
        m["articles"] = db.find("educational_articles", moduleId=m.get("id"))
        m["articleCount"] = len(m["articles"])
    return {"data": modules, "meta": {}}


@router.post("/educational/modules/")
def create_educational_module(payload: sc.CreateEducationalModulePayload):
    record = db.insert("educational_modules", {
        "id": db.gen_id("educational_modules", "EDU"),
        "title": payload.title,
        "description": payload.description,
        "orderIndex": payload.order_index,
        "status": "Published",
        "createdAt": "now",
        "updatedAt": "now",
    })
    return _one(record)


@router.get("/educational/modules/{module_id}/")
def get_educational_module(module_id: str):
    record = db.get("educational_modules", module_id)
    if not record:
        raise HTTPException(404, "Module not found")
    record["articles"] = db.find("educational_articles", moduleId=module_id)
    record["articleCount"] = len(record["articles"])
    return _one(record)


@router.put("/educational/modules/{module_id}/")
def update_educational_module(module_id: str, payload: sc.UpdateEducationalModulePayload):
    record = db.get("educational_modules", module_id)
    if not record:
        raise HTTPException(404, "Module not found")
    record["title"] = payload.title
    record["description"] = payload.description
    record["orderIndex"] = payload.order_index
    record["updatedAt"] = "now"
    return _one(record)


@router.delete("/educational/modules/{module_id}/")
def delete_educational_module(module_id: str):
    record = db.get("educational_modules", module_id)
    if not record:
        raise HTTPException(404, "Module not found")
    db.delete("educational_modules", module_id)
    for article in db.find("educational_articles", moduleId=module_id):
        db.delete("educational_articles", article.get("id"))
    return {"data": {"status": "deleted"}, "meta": {}}


@router.post("/educational/{module_id}/publish/")
def publish_educational_module(module_id: str):
    record = db.get("educational_modules", module_id)
    if not record:
        raise HTTPException(404, "Module not found")
    record["status"] = "Published"
    return _one(record)


@router.get("/educational/articles/")
def list_educational_articles():
    return _list_query("educational_articles")


@router.post("/educational/articles/")
def create_educational_article(payload: sc.CreateEducationalArticlePayload):
    record = db.insert("educational_articles", {
        "id": db.gen_id("educational_articles", "ART"),
        "moduleId": payload.module_id,
        "title": payload.title,
        "content": payload.content,
        "videoUrl": payload.video_url,
        "fileUrl": payload.file_url,
        "orderIndex": payload.order_index,
        "status": "Published",
        "createdAt": "now",
        "updatedAt": "now",
    })
    return _one(record)


@router.get("/educational/articles/{article_id}/")
def get_educational_article(article_id: str):
    record = db.get("educational_articles", article_id)
    if not record:
        raise HTTPException(404, "Article not found")
    return _one(record)


@router.put("/educational/articles/{article_id}/")
def update_educational_article(article_id: str, payload: sc.UpdateEducationalArticlePayload):
    record = db.get("educational_articles", article_id)
    if not record:
        raise HTTPException(404, "Article not found")
    record["moduleId"] = payload.module_id
    record["title"] = payload.title
    record["content"] = payload.content
    record["videoUrl"] = payload.video_url
    record["fileUrl"] = payload.file_url
    record["orderIndex"] = payload.order_index
    record["updatedAt"] = "now"
    return _one(record)


@router.delete("/educational/articles/{article_id}/")
def delete_educational_article(article_id: str):
    record = db.get("educational_articles", article_id)
    if not record:
        raise HTTPException(404, "Article not found")
    db.delete("educational_articles", article_id)
    return {"data": {"status": "deleted"}, "meta": {}}


@router.post("/educational/articles/{article_id}/upload-file/")
def upload_educational_file(article_id: str, file: UploadFile = File(...)):
    record = db.get("educational_articles", article_id)
    if not record:
        raise HTTPException(404, "Article not found")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    content = file.file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, "File terlalu besar (maks 10MB)")
    safe_name = os.path.basename(file.filename or "file.bin")
    stored_name = f"{int(time.time() * 1000)}-{safe_name}"
    with open(os.path.join(UPLOAD_DIR, stored_name), "wb") as out:
        out.write(content)
    record["fileUrl"] = f"/files/storage/{stored_name}"
    record["fileName"] = safe_name
    record["updatedAt"] = "now"
    return _one(record)


@router.post("/educational/articles/{article_id}/publish/")
def publish_educational_article(article_id: str):
    record = db.get("educational_articles", article_id)
    if not record:
        raise HTTPException(404, "Article not found")
    record["status"] = "Published"
    return _one(record)


@router.get("/calendar/")
def list_calendar():
    return _list_query("calendar_events")


@router.post("/calendar/")
def create_calendar(payload: sc.CreateCalendarEventPayload):
    data = payload.model_dump()
    data["id"] = db.gen_id("calendar_events", "CAL")
    data["status"] = "Scheduled"
    data["updatedAt"] = "now"
    return _one(db.insert("calendar_events", data))


@router.post("/calendar/{event_id}/done/")
def mark_calendar_done(event_id: str):
    record = db.get("calendar_events", event_id)
    if not record:
        raise HTTPException(404, "Calendar event not found")
    record["status"] = "Done"
    return _one(record)


@router.get("/files/")
def list_files():
    return _list_query("files")


@router.post("/files/")
def upload_file(payload: dict):
    record = db.insert("files", {
        "id": db.gen_id("files", "FIL"),
        "name": payload.get("name", "File"),
        "type": payload.get("type", "Document"),
        "projectId": payload.get("projectId", ""),
        "status": "Needs Review",
        "size": "-",
        "tags": [],
        "updatedAt": "now",
    })
    return _one(record)


UPLOAD_DIR = os.environ.get("MAUEKSPOR_UPLOAD_DIR", os.path.join(os.getcwd(), "uploads"))
MAX_UPLOAD_MB = 25


@router.post("/files/upload/")
def upload_file_binary(
    file: UploadFile = File(...),
    type_: str = Form(default="Document"),
    project_id: str = Form(default=""),
    tags: str = Form(default=""),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    content = file.file.read()
    if len(content) == 0:
        raise HTTPException(400, "File kosong")
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, "File terlalu besar (maks 25MB)")
    safe_name = os.path.basename(file.filename or "file.bin")
    stored_name = f"{int(time.time() * 1000)}-{safe_name}"
    storage_path = os.path.join(UPLOAD_DIR, stored_name)
    with open(storage_path, "wb") as out:
        out.write(content)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    record = db.insert("files", {
        "id": db.gen_id("files", "FIL-UPL"),
        "name": safe_name,
        "type": type_,
        "projectId": project_id,
        "status": "Needs Review",
        "size": f"{len(content) / 1024:.0f} KB",
        "tags": tag_list,
        "storageName": stored_name,
        "contentType": file.content_type or "application/octet-stream",
        "updatedAt": "now",
    })
    return _one(record)


@router.get("/files/{file_id}/download/")
def download_file(file_id: str):
    record = db.get("files", file_id)
    if not record or not record.get("storageName"):
        raise HTTPException(404, "File not found or not stored")
    storage_path = os.path.join(UPLOAD_DIR, record["storageName"])
    if not os.path.isfile(storage_path):
        raise HTTPException(404, "Stored file missing on disk")
    return FileResponse(
        storage_path,
        media_type=record.get("contentType") or "application/octet-stream",
        filename=record.get("name") or record["storageName"],
    )


@router.post("/files/{file_id}/verify/")
def verify_file(file_id: str):
    record = db.get("files", file_id)
    if not record:
        raise HTTPException(404, "File not found")
    record["status"] = "Verified"
    return _one(record)


@router.get("/messages/")
def list_messages():
    return _list_query("messages")


@router.post("/messages/{message_id}/send/")
def send_message(message_id: str, payload: dict):
    record = db.get("messages", message_id)
    if not record:
        raise HTTPException(404, "Message not found")
    record["lastMessage"] = payload.get("body", "")
    record["status"] = "Open"
    record["time"] = "now"
    return _one(record)


@router.post("/messages/{message_id}/resolve/")
def resolve_message(message_id: str):
    record = db.get("messages", message_id)
    if not record:
        raise HTTPException(404, "Message not found")
    record["status"] = "Resolved"
    return _one(record)


@router.get("/reports/")
def list_reports():
    return _list_query("reports")


@router.get("/reports/{report_id}/")
def get_report(report_id: str):
    record = db.get("reports", report_id)
    if not record:
        raise HTTPException(404, "Report not found")
    return _one(record)


@router.post("/reports/{report_id}/generate/")
def generate_report(report_id: str):
    record = db.get("reports", report_id)
    if not record:
        raise HTTPException(404, "Report not found")
    # Bangun konten laporan dari data workspace nyata
    projects = db.all("projects")
    products = db.all("products")
    analyses = db.all("export_analyses")
    buyers = db.all("buyers")
    orders = db.all("orders")
    pipeline_value = sum(p.get("value", 0) or 0 for p in projects)
    order_value = sum(o.get("value", 0) or 0 for o in orders)
    record["sections"] = [
        {"title": "Pipeline value", "value": f"${pipeline_value:,}", "detail": f"{len(projects)} proyek aktif"},
        {"title": "Order value", "value": f"${order_value:,}", "detail": f"{len(orders)} order"},
        {"title": "Products", "value": str(len(products)), "detail": f"{sum(1 for p in products if p.get('status') == 'Enriched')} enriched"},
        {"title": "Market analyses", "value": str(len(analyses)), "detail": f"{sum(1 for a in analyses if a.get('status') == 'Ready')} ready"},
        {"title": "Active buyers", "value": str(len(buyers)), "detail": "CRM pipeline"},
    ]
    record["insights"] = []
    if analyses:
        best = max(analyses, key=lambda a: a.get("score", 0) or 0)
        record["insights"].append(f"Pasar dengan skor tertinggi: {best.get('destination', '')} ({best.get('score', 0)}).")
    if projects:
        high = [p for p in projects if p.get("risk") == "High"]
        if high:
            record["insights"].append(f"{len(high)} proyek berisiko tinggi memerlukan perhatian.")
    if not record["insights"]:
        record["insights"].append("Tidak ada insight tambahan untuk periode ini.")
    record["status"] = "Ready"
    record["updatedAt"] = "now"
    return _one(record)


@router.post("/reports/{report_id}/schedule/")
def schedule_report(report_id: str):
    record = db.get("reports", report_id)
    if not record:
        raise HTTPException(404, "Report not found")
    record["status"] = "Scheduled"
    return _one(record)


@router.get("/billing/")
def list_billing():
    return _list_query("billing_records")


@router.post("/billing/change-plan/")
def change_billing_plan(payload: dict):
    records = db.all("billing_records")
    record = records[0] if records else None
    if record:
        record["plan"] = payload.get("plan", record.get("plan"))
    return _one(record) if record else {"data": None, "meta": {}}


@router.post("/billing/{billing_id}/invoice/")
def download_invoice(billing_id: str):
    record = db.get("billing_records", billing_id)
    if not record:
        raise HTTPException(404, "Billing record not found")
    record["invoiceDownloaded"] = record.get("invoiceDownloaded", 0) + 1
    return _one(record)


# ----------------------------------------------------------------------------
# SUPPORT / API KEYS / CHAT
# ----------------------------------------------------------------------------
@router.get("/support/")
def list_support():
    return _list_query("support_tickets")


@router.post("/support/")
def create_support(payload: dict):
    record = db.insert("support_tickets", {
        "id": db.gen_id("support_tickets", "SUPPORT"),
        "subject": payload.get("subject", "Ticket"),
        "category": payload.get("category", "Question"),
        "description": payload.get("description", ""),
        "status": "Open",
        "priority": "Medium",
        "createdAt": "now",
        "owner": "Unassigned",
    })
    return _one(record)


@router.post("/support/{ticket_id}/resolve/")
def resolve_support(ticket_id: str):
    record = db.get("support_tickets", ticket_id)
    if not record:
        raise HTTPException(404, "Ticket not found")
    record["status"] = "Resolved"
    return _one(record)


@router.get("/api-keys/")
def list_api_keys():
    return _list_query("api_keys")


@router.post("/api-keys/")
def create_api_key(payload: sc.CreateApiKeyPayload):
    record = db.insert("api_keys", {
        "id": db.gen_id("api_keys", "KEY"),
        "name": payload.name,
        "prefix": "mek_live_",
        "scopes": payload.scopes,
        "status": "Active",
        "createdAt": "now",
        "lastUsed": "never",
        "owner": "Admin",
    })
    return _one(record)


@router.post("/api-keys/{key_id}/revoke/")
def revoke_api_key(key_id: str):
    record = db.get("api_keys", key_id)
    if not record:
        raise HTTPException(404, "API key not found")
    record["status"] = "Revoked"
    return _one(record)


@router.get("/chat/")
def list_chat():
    return _list_query("chat_conversations")


@router.post("/chat/{chat_id}/messages/")
def send_chat_message(chat_id: str, payload: dict):
    record = db.get("chat_conversations", chat_id)
    if not record:
        raise HTTPException(404, "Chat not found")
    record.setdefault("messages", []).append({"role": "User", "text": payload.get("text", "")})
    history = "\n".join(f"{m.get('role', '')}: {m.get('text', '')}" for m in record["messages"][-8:])
    reply = ai.complete(
        "You are MauEkspor Copilot, a trade assistant for Indonesian exporters. Answer concisely in Indonesian, grounded in the workspace context given.",
        f"Conversation so far:\n{history}",
        kind="chat_reply",
    )
    if reply:
        record["messages"].append({"role": "AI", "text": reply})
    record["updatedAt"] = "now"
    return _one(record)


# ----------------------------------------------------------------------------
# CHAT SESSIONS & SUGGESTIONS (AI Copilot)
# ----------------------------------------------------------------------------
@router.get("/chat/sessions/")
def list_chat_sessions():
    sessions = db.all("chat_sessions")
    for s in sessions:
        s["messageCount"] = len(s.get("messages", []) or [])
    return {"data": sessions, "meta": {}}


@router.post("/chat/sessions/")
def create_chat_session(payload: sc.CreateChatSessionPayload):
    record = db.insert("chat_sessions", {
        "id": db.gen_id("chat_sessions", "CHS"),
        "title": payload.title or "Percakapan baru",
        "messages": [],
        "createdAt": "now",
        "updatedAt": "now",
    })
    return _one(record)


@router.get("/chat/sessions/{session_id}/")
def get_chat_session(session_id: str):
    record = db.get("chat_sessions", session_id)
    if not record:
        raise HTTPException(404, "Chat session not found")
    return _one(record)


@router.delete("/chat/sessions/{session_id}/")
def delete_chat_session(session_id: str):
    record = db.get("chat_sessions", session_id)
    if not record:
        raise HTTPException(404, "Chat session not found")
    db.delete("chat_sessions", session_id)
    return {"data": {"status": "deleted"}, "meta": {}}


@router.post("/chat/sessions/{session_id}/messages/")
def send_session_message(session_id: str, payload: sc.SendChatPayload):
    record = db.get("chat_sessions", session_id)
    if not record:
        raise HTTPException(404, "Chat session not found")
    record.setdefault("messages", []).append({"role": "user", "text": payload.text})
    history = "\n".join(f"{m.get('role', '')}: {m.get('text', '')}" for m in record["messages"][-8:])
    reply = ai.complete(
        "You are MauEkspor Copilot, a trade assistant for Indonesian exporters. Answer concisely in Indonesian, grounded in the workspace context given.",
        f"Conversation so far:\n{history}",
        kind="chat_reply",
    )
    if reply:
        record["messages"].append({"role": "ai", "text": reply})
    if record.get("title") in ("", "Percakapan baru") and payload.text:
        record["title"] = payload.text[:40]
    record["updatedAt"] = "now"
    return _one(record)


@router.get("/chat/suggestions/")
def chat_suggestions():
    products = db.all("products")
    suggestions = [
        {"question": "Apa langkah berikutnya untuk ekspor produk saya?", "context": "general"},
        {"question": "Bagaimana cara menentukan HS code produk?", "context": "hs"},
    ]
    if products:
        suggestions.append({"question": f"Apa syarat kepatuhan untuk {products[0].get('name', 'produk')}?", "context": "compliance"})
        suggestions.append({"question": "Berapa estimasi harga EXW/FOB/CIF produk saya?", "context": "pricing"})
    return {"data": suggestions, "meta": {}}


# ----------------------------------------------------------------------------
# EXPORT ANALYSIS
# ----------------------------------------------------------------------------
@router.get("/export-analysis/")
def list_analyses(search: str = "", status: str = "", limit: int = 0, offset: int = 0):
    return _filtered_query("export_analyses", search=search, search_fields=("productName", "destination", "hsCode"), status=status, limit=limit, offset=offset)


@router.get("/export-analysis/{analysis_id}/")
def get_analysis(analysis_id: str):
    record = db.get("export_analyses", analysis_id)
    if not record:
        raise HTTPException(404, "Export analysis not found")
    return _one(record)


@router.post("/export-analysis/")
def create_analysis(payload: sc.CreateExportAnalysisPayload):
    from app.services import compliance as compliance_svc
    from app.data.countries import resolve_country

    product = db.get("products", payload.productId)
    if not product:
        raise HTTPException(404, "Product not found")
    country_code = resolve_country(str(payload.destination))
    # Deduplikasi (product, country)
    existing = db.get_by("export_analyses", productId=payload.productId, countryCode=country_code)
    if existing:
        raise HTTPException(409, "Analysis for this product & country already exists")

    result = compliance_svc.analyze_product_compliance(product, country_code)
    snapshot = compliance_svc.snapshot_product(product)
    reg_snapshot = compliance_svc.snapshot_regulations(country_code)
    record = db.insert("export_analyses", {
        "id": db.gen_id("export_analyses", "ANL"),
        "productId": payload.productId,
        "productName": product["name"],
        "destination": country_code,
        "status": "Ready",
        "hsCode": product.get("hs", "TBD"),
        "confidence": max(len(result["issues"]) == 0 and 91 or 80, 60),
        "score": result["score"],
        "statusGrade": result["grade"],
        "complianceIssues": result["issues"],
        "recommendations": result["recommendations"],
        "productSnapshot": snapshot,
        "regulationSnapshot": reg_snapshot,
        "snapshotProductName": snapshot.get("name", ""),
        "productChanged": False,
        "countryCode": country_code,
        "marketDemand": "Medium",
        "duties": "Pending",
        "restrictions": [],
        "summary": result["recommendations"][:300] if result["recommendations"] else "Analysis complete.",
        "updatedAt": "now",
    })
    return _one(record)


def _compare_analyses_results(product: dict, country_codes: list[str]) -> tuple[dict, list[dict]]:
    """Jalankan/dapatkan analisis per negara & urutkan berdasarkan skor (dipakai compare JSON + PDF)."""
    from app.services import compliance as compliance_svc

    codes = [c.upper()[:2] for c in country_codes][:5]
    results = []
    for code in codes:
        analysis = db.get_by("export_analyses", productId=product.get("id"), countryCode=code)
        if not analysis:
            result = compliance_svc.analyze_product_compliance(product, code)
            analysis = db.insert("export_analyses", {
                "id": db.gen_id("export_analyses", "ANL"),
                "productId": product.get("id"),
                "productName": product["name"],
                "destination": code,
                "status": "Ready",
                "hsCode": product.get("hs", "TBD"),
                "confidence": 80,
                "score": result["score"],
                "statusGrade": result["grade"],
                "complianceIssues": result["issues"],
                "recommendations": result["recommendations"],
                "productSnapshot": compliance_svc.snapshot_product(product),
                "regulationSnapshot": compliance_svc.snapshot_regulations(code),
                "snapshotProductName": product["name"],
                "productChanged": False,
                "countryCode": code,
                "summary": result["recommendations"][:300] if result["recommendations"] else "",
                "updatedAt": "now",
            })
        critical_count = sum(1 for i in (analysis.get("complianceIssues") or []) if i.get("severity") == "critical")
        results.append({
            "analysis": analysis,
            "analysisId": analysis.get("id"),
            "country": code,
            "score": analysis.get("score", 0),
            "grade": analysis.get("statusGrade", "Warning"),
            "critical_issues": critical_count,
            "recommendation": (analysis.get("recommendations") or "")[:200],
        })
    results.sort(key=lambda r: r["score"], reverse=True)
    return {"data": {"product": {"id": product.get("id"), "name": product.get("name")}, "results": results}, "meta": {}}


@router.post("/export-analysis/compare/")
def compare_analyses(payload: sc.CompareExportAnalysisPayload):
    product = db.get("products", payload.product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return _compare_analyses_results(product, payload.country_codes)


@router.post("/export-analysis/compare/pdf/")
def compare_analyses_pdf(payload: sc.CompareExportAnalysisPayload):
    """PDF perbandingan analisis antar negara (dipakai laporan & revisi).

    Didefinisikan sebelum rute parameterized {analysis_id} agar tidak tertutup.
    """
    from app.services.pricing import build_compare_pdf

    product = db.get("products", payload.product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    response = _compare_analyses_results(product, payload.country_codes)
    pdf_bytes = build_compare_pdf(product, response["data"]["results"])
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="analysis-compare-{payload.product_id}.pdf"'},
    )

@router.post("/export-analysis/{analysis_id}/reanalyze/")
def reanalyze_analysis(analysis_id: str):
    from app.services import compliance as compliance_svc

    record = db.get("export_analyses", analysis_id)
    if not record:
        raise HTTPException(404, "Export analysis not found")
    product = db.get("products", str(record.get("productId", "")))
    if not product:
        raise HTTPException(404, "Product not found")
    from app.data.countries import resolve_country
    cc = resolve_country(str(record.get("countryCode") or record.get("destination", "")))
    result = compliance_svc.analyze_product_compliance(product, cc)
    record["score"] = result["score"]
    record["statusGrade"] = result["grade"]
    record["complianceIssues"] = result["issues"]
    record["recommendations"] = result["recommendations"]
    record["productSnapshot"] = compliance_svc.snapshot_product(product)
    record["regulationSnapshot"] = compliance_svc.snapshot_regulations(cc)
    record["countryCode"] = cc
    record["snapshotProductName"] = product.get("name", "")
    record["productChanged"] = False
    record["status"] = "Ready"
    record["updatedAt"] = "now"
    # Hapus cache rekomendasi regulasi
    for cached in db.find("regulation_recommendations", analysisId=analysis_id):
        db.delete("regulation_recommendations", cached.get("id"))
    return _one(record)


@router.delete("/export-analysis/{analysis_id}/")
def delete_analysis(analysis_id: str):
    record = db.get("export_analyses", analysis_id)
    if not record:
        raise HTTPException(404, "Export analysis not found")
    db.delete("export_analyses", analysis_id)
    for cached in db.find("regulation_recommendations", analysisId=analysis_id):
        db.delete("regulation_recommendations", cached.get("id"))
    return {"data": {"status": "deleted", "id": analysis_id}, "meta": {}}


@router.get("/export-analysis/{analysis_id}/regulation-recommendations/")
def get_regulation_recommendations(analysis_id: str, language: str = "id"):
    from app.services import compliance as compliance_svc
    from app.data.countries import resolve_country

    record = db.get("export_analyses", analysis_id)
    if not record:
        raise HTTPException(404, "Export analysis not found")
    country_code = resolve_country(str(record.get("countryCode") or record.get("destination", "")))
    cached = db.get_by("regulation_recommendations", analysisId=analysis_id, language=language)
    if cached:
        cached["fromCache"] = True
        return _one(cached)
    snapshot = record.get("productSnapshot") or compliance_svc.snapshot_product({})
    result = compliance_svc.generate_regulation_recommendations(snapshot, country_code, language)
    data = {
        "id": db.gen_id("regulation_recommendations", "REG"),
        "analysisId": analysis_id,
        "language": language,
        "sections": result["sections"],
        "country": result["country"],
        "fromCache": False,
    }
    db.insert("regulation_recommendations", data)
    return _one(data)


@router.get("/export-analysis/{analysis_id}/pdf/")
def export_analysis_pdf(analysis_id: str):
    record = db.get("export_analyses", analysis_id)
    if not record:
        raise HTTPException(404, "Export analysis not found")
    from app.services.pricing import build_analysis_pdf
    pdf_bytes = build_analysis_pdf(record)
    from fastapi.responses import Response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="analysis-{analysis_id}.pdf"'},
    )


@router.post("/export-analysis/{analysis_id}/regulation-recommendations/")
def run_regulation_check(analysis_id: str, payload: dict | None = None):
    record = db.get("export_analyses", analysis_id)
    if not record:
        raise HTTPException(404, "Export analysis not found")
    language = (payload or {}).get("language", "id")
    record["status"] = "Ready"
    recommendations = ai.ask_json(
        "You are a trade compliance analyst for Indonesian exports. Return JSON list in field recommendations: items with type, title, status (Required/Optional) and detail.",
        f"Product {record.get('productName', '')} to {record.get('destination', '')} (HS {record.get('hsCode', 'TBD')}). Regulations: {record.get('restrictions', [])}",
        kind="recommendations",
    )
    record["confidence"] = recommendations.get("confidence", 88) if recommendations else 88
    record["score"] = recommendations.get("score", 80) if recommendations else 80
    if recommendations and isinstance(recommendations.get("recommendations"), list):
        record["recommendations"] = recommendations["recommendations"]
    else:
        record["recommendations"] = [
            {"type": "Certificate", "title": "Certificate of Origin", "status": "Required", "detail": "Confirm rules-of-origin."},
            {"type": "Document", "title": "Packing list", "status": "Required", "detail": "Match weights against invoice."},
        ]
    record["updatedAt"] = "now"
    # Sinkronkan dengan cache regulasi 10-bagian
    for cached in db.find("regulation_recommendations", analysisId=analysis_id):
        db.delete("regulation_recommendations", cached.get("id"))
    return _one(record)


# ----------------------------------------------------------------------------
# COUNTRIES & REGULATIONS (read-only untuk semua role, admin untuk tulis)
# ----------------------------------------------------------------------------
@router.get("/countries/")
def list_countries(region: str = "", search: str = ""):
    from app.data.countries import get_countries
    items = get_countries()
    if region:
        items = [c for c in items if c["region"].lower() == region.lower()]
    if search:
        items = [c for c in items if search.lower() in (c["country_name"] + c["country_code"]).lower()]
    for item in items:
        item["regulationsCount"] = len([r for r in db.all("countries") if False])  # placeholder
    return {"data": items, "meta": {}}


@router.get("/countries/{country_code}/")
def get_country_detail(country_code: str):
    from app.data.countries import get_country, get_regulations
    country = get_country(country_code)
    if not country:
        raise HTTPException(404, "Country not found")
    regs = get_regulations(country_code)
    by_category: dict[str, list] = {}
    for r in regs:
        by_category.setdefault(r["rule_category"], []).append(r)
    country["regulations"] = regs
    country["regulations_by_category"] = by_category
    return {"data": country, "meta": {}}


# ----------------------------------------------------------------------------
# HS CODES (admin)
# ----------------------------------------------------------------------------
@router.get("/hs-codes/")
def list_hs_codes(search: str = "", chapter: str = "", limit: int = 50, offset: int = 0):
    from app.data.hs_loader import get_hs_loader
    loader = get_hs_loader()
    if search:
        items = loader.search_hs_codes(search, max_results=limit, min_level=2)
    else:
        items = loader.codes
        if chapter:
            items = [c for c in items if str(c.get("hs_code", "")).startswith(chapter.zfill(2))]
        items = items[offset:offset + limit]
    return {"data": items, "meta": {"total": len(loader.codes), "limit": limit, "offset": offset}}


@router.get("/hs-codes/autocomplete/")
def autocomplete_hs_codes(q: str = "", limit: int = 10):
    from app.data.hs_loader import get_hs_loader
    loader = get_hs_loader()
    return {"data": loader.autocomplete(q, limit), "meta": {}}


@router.get("/hs-codes/{hs_code}/")
def get_hs_code(hs_code: str):
    from app.data.hs_loader import get_hs_loader
    loader = get_hs_loader()
    record = loader.get_hs_code(hs_code)
    if not record:
        raise HTTPException(404, "HS code not found")
    record["section_name"] = loader.sections.get(record.get("section", ""), "")
    record["children"] = loader.children_of(hs_code)
    return {"data": record, "meta": {}}


@router.post("/hs-codes/")
def create_hs_code(payload: sc.CreateHSCodePayload):
    from app.data.hs_loader import get_hs_loader
    code = str(payload.hs_code).replace(".", "")
    level = 2 if len(code) <= 2 else 4 if len(code) <= 4 else 6 if len(code) <= 6 else 8
    record = db.insert("hs_codes", {
        "id": db.gen_id("hs_codes", "HS"),
        "hs_code": code,
        "description": payload.description,
        "description_id": payload.description_id,
        "section": payload.section,
        "level": level,
        "parent": code[: len(code) - 2] if len(code) > 2 else "TOTAL",
        "keywords": payload.keywords,
        "createdAt": "now",
    })
    return _one(record)


@router.put("/hs-codes/{hs_code}/update/")
def update_hs_code(hs_code: str, payload: dict):
    record = db.get_by("hs_codes", hs_code=hs_code.replace(".", ""))
    if not record:
        raise HTTPException(404, "HS code not found")
    for key in ("description", "description_id", "section", "keywords"):
        if payload.get(key) is not None:
            record[key] = payload[key]
    record["updatedAt"] = "now"
    return _one(record)


@router.delete("/hs-codes/{hs_code}/delete/")
def delete_hs_code(hs_code: str):
    record = db.get_by("hs_codes", hs_code=hs_code.replace(".", ""))
    if not record:
        raise HTTPException(404, "HS code not found")
    children = [c for c in db.all("hs_codes") if c.get("parent") == record["hs_code"]]
    if children:
        raise HTTPException(409, "HS code has children")
    db.delete("hs_codes", record.get("id"))
    return {"data": {"status": "deleted"}, "meta": {}}


@router.post("/hs-codes/import/")
def import_hs_codes_csv(file: UploadFile = File(...)):
    import csv as _csv
    content = file.file.read().decode("utf-8", errors="replace")
    reader = _csv.DictReader(content.splitlines())
    count = 0
    for row in reader:
        code = (row.get("hscode") or row.get("hs_code") or "").strip()
        if not code:
            continue
        if db.get_by("hs_codes", hs_code=code):
            continue
        db.insert("hs_codes", {
            "id": db.gen_id("hs_codes", "HS"),
            "hs_code": code,
            "description": row.get("description", ""),
            "section": row.get("section", ""),
            "parent": row.get("parent", ""),
            "level": int(row["level"]) if str(row.get("level", "")).isdigit() else 0,
            "keywords": [],
            "createdAt": "now",
        })
        count += 1
    return {"data": {"imported": count}, "meta": {}}


# ----------------------------------------------------------------------------
# ADMIN COUNTRIES & REGULATIONS
# ----------------------------------------------------------------------------
@router.post("/admin/countries/")
def admin_create_country(payload: sc.CreateCountryPayload):
    from app.data.countries import get_country
    if get_country(payload.country_code):
        raise HTTPException(409, "Country already exists")
    record = db.insert("countries", {
        "id": db.gen_id("countries", "CTY"),
        "country_code": payload.country_code.upper(),
        "country_name": payload.country_name,
        "region": payload.region,
        "createdAt": "now",
    })
    return _one(record)


@router.put("/admin/countries/{country_code}/")
def admin_update_country(country_code: str, payload: sc.UpdateCountryPayload):
    record = db.get_by("countries", country_code=country_code.upper())
    if not record:
        raise HTTPException(404, "Country not found")
    if payload.country_name:
        record["country_name"] = payload.country_name
    if payload.region:
        record["region"] = payload.region
    record["updatedAt"] = "now"
    return _one(record)


@router.delete("/admin/countries/{country_code}/delete/")
def admin_delete_country(country_code: str):
    record = db.get_by("countries", country_code=country_code.upper())
    if not record:
        raise HTTPException(404, "Country not found")
    if db.find("export_analyses", countryCode=country_code.upper()):
        raise HTTPException(409, "Country referenced by export analyses")
    db.delete("countries", record.get("id"))
    return {"data": {"status": "deleted"}, "meta": {}}


@router.get("/admin/countries/{country_code}/regulations/")
def admin_list_regulations(country_code: str, rule_category: str = ""):
    from app.data.countries import get_regulations
    items = get_regulations(country_code)
    if rule_category:
        items = [r for r in items if r["rule_category"].lower() == rule_category.lower()]
    return {"data": items, "meta": {}}


@router.post("/admin/countries/{country_code}/regulations/create/")
def admin_create_regulation(country_code: str, payload: sc.CreateRegulationPayload):
    from app.data.countries import get_country
    if not get_country(country_code):
        raise HTTPException(404, "Country not found")
    record = db.insert("regulations", {
        "id": db.gen_id("regulations", "REG"),
        "countryCode": country_code.upper(),
        "ruleCategory": payload.rule_category,
        "forbiddenKeywords": payload.forbidden_keywords,
        "requiredSpecs": payload.required_specs,
        "descriptionRule": payload.description_rule,
        "createdAt": "now",
    })
    return _one(record)


@router.put("/admin/regulations/{regulation_id}/")
def admin_update_regulation(regulation_id: str, payload: sc.UpdateRegulationPayload):
    record = db.get("regulations", regulation_id)
    if not record:
        raise HTTPException(404, "Regulation not found")
    record["ruleCategory"] = payload.rule_category
    record["forbiddenKeywords"] = payload.forbidden_keywords
    record["requiredSpecs"] = payload.required_specs
    record["descriptionRule"] = payload.description_rule
    record["updatedAt"] = "now"
    return _one(record)


@router.delete("/admin/regulations/{regulation_id}/delete/")
def admin_delete_regulation(regulation_id: str):
    record = db.get("regulations", regulation_id)
    if not record:
        raise HTTPException(404, "Regulation not found")
    db.delete("regulations", regulation_id)
    db.delete("countries", regulation_id)
    return {"data": {"status": "deleted"}, "meta": {}}


@router.post("/admin/regulations/import/")
def admin_import_regulations(file: UploadFile = File(...)):
    import csv as _csv
    content = file.file.read().decode("utf-8", errors="replace")
    reader = _csv.DictReader(content.splitlines())
    count = 0
    for row in reader:
        code = (row.get("country_code") or "").strip().upper()
        if not code:
            continue
        db.insert("regulations", {
            "id": db.gen_id("regulations", "REG"),
            "countryCode": code,
            "ruleCategory": row.get("rule_category", "Labeling"),
            "forbiddenKeywords": row.get("forbidden_keywords", ""),
            "requiredSpecs": row.get("required_specs", ""),
            "descriptionRule": row.get("description_rule", ""),
            "createdAt": "now",
        })
        count += 1
    return {"data": {"imported": count}, "meta": {}}


# ----------------------------------------------------------------------------
# SETTINGS (organisasi & akses)
# ----------------------------------------------------------------------------
DEFAULT_SETTINGS = {
    "companyName": "PT Kopi Gayo Nusantara",
    "country": "Indonesia",
    "entityType": "Manufacturer exporter",
    "nib": "",
    "taxId": "",
    "currency": "IDR",
    "language": "id",
    "notifications": True,
    "security": {"sessionType": "cookie"},
}


@router.get("/settings/")
def get_settings():
    records = db.all("settings")
    if records:
        data = dict(records[0])
        data.pop("id", None)
        return {"data": data, "meta": {}}
    return {"data": dict(DEFAULT_SETTINGS), "meta": {}}


@router.put("/settings/")
def update_settings(payload: dict):
    records = db.all("settings")
    if records:
        record = records[0]
    else:
        record = db.insert("settings", {"id": "SET-ORG-001", **dict(DEFAULT_SETTINGS)})
    for key, value in payload.items():
        record[key] = value
    record["updatedAt"] = "now"
    db.save(record)
    return _one(record)


# ----------------------------------------------------------------------------
# PENCARIAN GLOBAL (command palette)
# ----------------------------------------------------------------------------
@router.get("/search/")
def global_search(q: str = ""):
    """Cari di seluruh entitas workspace (produk, buyer, proyek, analisis, katalog, forwarder)."""
    query = q.strip().lower()
    if not query:
        return {"data": [], "meta": {}}
    results: list[dict] = []
    for p in db.all("products"):
        if query in str(p.get("name", "")).lower() or query in str(p.get("hs", "")).lower() or query in str(p.get("category", "")).lower():
            results.append({"label": p.get("name"), "href": f"/products/{p.get('id')}", "group": "Product", "sub": p.get("hs", "")})
    for b in db.all("buyers"):
        if query in str(b.get("name", "")).lower() or query in str(b.get("country", "")).lower():
            results.append({"label": b.get("name"), "href": f"/buyers/{b.get('id')}", "group": "Buyer", "sub": b.get("country", "")})
    for pr in db.all("projects"):
        if query in str(pr.get("name", "")).lower() or query in str(pr.get("product", "")).lower() or query in str(pr.get("buyer", "")).lower():
            results.append({"label": pr.get("name"), "href": f"/trade-projects/{pr.get('id')}", "group": "Trade Project", "sub": pr.get("product", "")})
    for a in db.all("export_analyses"):
        if query in str(a.get("productName", "")).lower() or query in str(a.get("destination", "")).lower():
            results.append({"label": f"{a.get('productName')} - {a.get('destination')}", "href": f"/export-analysis/{a.get('id')}", "group": "Export Analysis", "sub": a.get("hsCode", "")})
    for cat in db.all("catalogs"):
        if query in str(cat.get("title", "")).lower() or query in str(cat.get("targetMarket", "")).lower():
            results.append({"label": cat.get("title"), "href": f"/catalogs/{cat.get('id')}", "group": "Catalog", "sub": cat.get("targetMarket", "")})
    for f in db.all("forwarders"):
        if query in str(f.get("name", "")).lower() or query in str(f.get("coverage", "")).lower():
            results.append({"label": f.get("name"), "href": f"/forwarders/{f.get('id')}", "group": "Forwarder", "sub": f.get("coverage", "")})
    return {"data": results[:20], "meta": {"count": len(results)}}
