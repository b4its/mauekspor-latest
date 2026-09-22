"""Layanan kepatuhan ekspor: cek bahan, spesifikasi, kemasan + skor kesiapan + rekomendasi regulasi.

Diadaptasi dari `apps/export_analysis/services.py` ExportReadyAI.
"""

from __future__ import annotations

import re
from typing import Any

from app import ai, db
from app.data import countries as country_data

SEVERITY_POINTS = {"critical": 20, "major": 10, "minor": 5}


# ---------------------------------------------------------------------------
# Helper parsing LLM
# ---------------------------------------------------------------------------
def _parse_json_list(text: str | None) -> list | None:
    if not text:
        return None
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return None
    import json
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, list) else None


# ---------------------------------------------------------------------------
# Compliance checkers (berbasis snapshot / data produk)
# ---------------------------------------------------------------------------
def _material_keywords(description: str) -> str:
    return str(description or "")


def check_ingredient_compliance(product: dict, country_code: str) -> list[dict]:
    """Cek bahan terhadap `forbidden_keywords` pada regulasi Ingredient."""
    regs = [r for r in country_data.get_regulations(country_code) if r["rule_category"] == "Ingredient"]
    description = _material_keywords(product.get("description") or product.get("name") or "")
    material = str(product.get("material_composition") or "") or description
    issues: list[dict] = []
    for reg in regs:
        keywords = [k.strip() for k in reg.get("forbidden_keywords", "").split(",") if k.strip()]
        if not keywords:
            continue
        detected = [k for k in keywords if k.lower() in material.lower()]
        if detected:
            issues.append({
                "type": "Ingredient",
                "rule_key": "ingredient_compliance",
                "your_value": ", ".join(detected),
                "required_value": f"Bebas dari: {reg.get('forbidden_keywords')}",
                "description": reg.get("description_rule", ""),
                "severity": "critical",
            })
    # Remote AI judge bila tersedia
    if country_data.get_country(country_code) and ai.configured():
        issues = _ai_judge("ingredient", product, country_code, regs, issues)
    return issues


def check_specification_compliance(product: dict, country_code: str) -> list[dict]:
    """Cek spesifikasi terhadap `required_specs` pada regulasi Labeling."""
    regs = [r for r in country_data.get_regulations(country_code) if r["rule_category"] == "Labeling"]
    quality_specs = product.get("quality_specs") or {}
    spec_text = " ".join(f"{k}: {v}" for k, v in quality_specs.items()) if isinstance(quality_specs, dict) else str(quality_specs)
    issues: list[dict] = []
    for reg in regs:
        required = [s.strip() for s in reg.get("required_specs", "").split(",") if s.strip()]
        missing = [s for s in required if s.lower() not in (spec_text + " " + str(product.get("name", "")).lower())]
        if missing:
            issues.append({
                "type": "Labeling",
                "rule_key": "specification_compliance",
                "your_value": spec_text or "Belum ada spesifikasi",
                "required_value": ", ".join(missing),
                "description": reg.get("description_rule", ""),
                "severity": "major",
            })
    return issues


def check_packaging_compliance(product: dict, country_code: str) -> list[dict]:
    """Cek kemasan terhadap regulasi Physical (ISPM-15, sertifikasi, dll)."""
    regs = [r for r in country_data.get_regulations(country_code) if r["rule_category"] == "Physical"]
    packaging = str(product.get("packaging") or "")
    issues: list[dict] = []
    for reg in regs:
        required = [s.strip() for s in reg.get("required_specs", "").split(",") if s.strip()]
        missing = [s for s in required if s.lower() not in packaging.lower()]
        if missing:
            issues.append({
                "type": "Physical",
                "rule_key": "packaging_compliance",
                "your_value": packaging or "Belum ada info kemasan",
                "required_value": ", ".join(missing),
                "description": reg.get("description_rule", ""),
                "severity": "minor",
            })
    return issues


def _ai_judge(check_type: str, product: dict, country_code: str, regs: list[dict], issues: list[dict]) -> list[dict]:
    system = (
        "You are a trade compliance analyst. Return a JSON list of compliance issues. "
        "Each issue: {type, rule_key, your_value, required_value, description, severity} "
        "where severity is critical/major/minor."
    )
    user = (
        f"Check {check_type} compliance for product '{product.get('name', '')}' "
        f"(material: {product.get('material_composition', '')}, packaging: {product.get('packaging', '')}, "
        f"specs: {product.get('quality_specs', {})}) to country {country_code}. "
        f"Regulations: {regs}"
    )
    text = ai.complete(system, user, kind="compliance_check")
    parsed = _parse_json_list(text)
    if parsed:
        return parsed
    return issues


# ---------------------------------------------------------------------------
# Skor kesiapan
# ---------------------------------------------------------------------------
def calculate_readiness_score(issues: list[dict]) -> tuple[int, str]:
    """Skor 0-100 dan grade: Ready (>=80), Warning (>=50), Critical (<50)."""
    score = 100
    for issue in issues:
        score -= SEVERITY_POINTS.get(str(issue.get("severity", "minor")).lower(), 5)
    score = max(0, min(100, score))
    if score >= 80:
        grade = "Ready"
    elif score >= 50:
        grade = "Warning"
    else:
        grade = "Critical"
    return score, grade


def generate_recommendations(issues: list[dict]) -> str:
    """Rekomendasi teks (Indonesia) dari isu kepatuhan."""
    if not issues:
        return "Tidak ditemukan isu kepatuhan. Produk siap untuk analisis pasar."
    text = ai.complete(
        "You are an export readiness advisor. Reply in Indonesian with a numbered list of corrective actions.",
        f"Issues: {issues}",
        kind="recommendations_text",
    )
    if text and len(text.strip()) > 10:
        return text.strip()
    lines = []
    for i, issue in enumerate(issues, start=1):
        lines.append(
            f"{i}. Perbaiki {issue.get('type', 'kepatuhan')}: {issue.get('required_value', '')} "
            f"({issue.get('severity', 'minor')})."
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Rekomendasi regulasi (10 bagian, ID/EN)
# ---------------------------------------------------------------------------
_REGULATION_SECTIONS = [
    ("overview", "Overview", "Ikhtisar"),
    ("prohibited_items", "Prohibited Items", "Barang Terlarang"),
    ("import_restrictions", "Import Restrictions", "Pembatasan Impor"),
    ("certifications", "Certifications", "Sertifikasi"),
    ("labeling", "Labeling", "Pelabelan"),
    ("customs", "Customs & Duties", "Bea & Pabean"),
    ("testing", "Testing & Inspection", "Pengujian & Inspeksi"),
    ("ip", "Intellectual Property", "Kekayaan Intelektual"),
    ("shipping", "Shipping & Logistics", "Pengiriman & Logistik"),
    ("timeline_costs", "Timeline & Costs", "Waktu & Biaya"),
]


def generate_regulation_recommendations(snapshot: dict, country_code: str, language: str = "id") -> dict[str, Any]:
    """Susun 10 bagian panduan regulasi dari snapshot produk + regulasi negara.

    `from_cache` di-set false; pemanggil boleh men-cache hasilnya di DB.
    """
    is_id = language.lower().startswith("id")
    country = country_data.get_country(country_code) or {"country_name": country_code, "region": "Asia"}
    regs = country_data.get_regulations(country_code)
    product_name = snapshot.get("name") or snapshot.get("product_name") or "Produk"
    hs_code = snapshot.get("hs") or snapshot.get("hs_code") or "TBD"

    by_category: dict[str, list[dict]] = {}
    for reg in regs:
        by_category.setdefault(reg["rule_category"], []).append(reg)

    def label(text_en: str, text_id: str) -> str:
        return text_id if is_id else text_en

    sections: list[dict] = []
    for key, en_title, id_title in _REGULATION_SECTIONS:
        body = ""
        if key == "overview":
            body = label(
                f"Overview of export requirements for {product_name} (HS {hs_code}) to {country['country_name']}.",
                f"Ikhtisar persyaratan ekspor {product_name} (HS {hs_code}) ke {country['country_name']}.",
            )
        elif key == "prohibited_items":
            forbidden = []
            for reg in by_category.get("Ingredient", []):
                if reg.get("forbidden_keywords"):
                    forbidden.append(reg["forbidden_keywords"])
            body = label(
                "Prohibited ingredients/substances: " + ("; ".join(forbidden) if forbidden else "None found in current dataset."),
                "Bahan/zat terlarang: " + ("; ".join(forbidden) if forbidden else "Tidak ditemukan pada dataset saat ini."),
            )
        elif key == "import_restrictions":
            body = label(
                "Check import licensing, quotas, and special permits for the target country before shipping.",
                "Periksa lisensi impor, kuota, dan izin khusus negara tujuan sebelum pengiriman.",
            )
        elif key == "certifications":
            certs = []
            for reg in by_category.get("Physical", []):
                if reg.get("required_specs"):
                    certs.append(reg["required_specs"])
            body = label(
                "Required certifications: " + ("; ".join(certs) if certs else "Depends on product category."),
                "Sertifikasi yang diperlukan: " + ("; ".join(certs) if certs else "Tergantung kategori produk."),
            )
        elif key == "labeling":
            reqs = []
            for reg in by_category.get("Labeling", []):
                if reg.get("required_specs"):
                    reqs.append(reg["required_specs"])
            body = label(
                "Labeling requirements: " + ("; ".join(reqs) if reqs else "Standard commercial labeling."),
                "Persyaratan pelabelan: " + ("; ".join(reqs) if reqs else "Pelabelan komersial standar."),
            )
        elif key == "customs":
            body = label(
                f"Declare HS {hs_code} correctly; verify duty rates and any preferential trade agreements (e.g. EPA/FTA).",
                f"Deklarasikan HS {hs_code} dengan benar; verifikasi tarif bea dan perjanjian perdagangan preferensial (mis. EPA/FTA).",
            )
        elif key == "testing":
            body = label(
                "Arrange lab testing (pesticide residue, microbiology, nutrition) from accredited laboratories.",
                "Siapkan pengujian laboratorium (residu pestisida, mikrobiologi, nutrisi) dari laboratorium terakreditasi.",
            )
        elif key == "ip":
            body = label(
                "Ensure trademarks, patents, and geographical indications are protected in the destination market.",
                "Pastikan merek, paten, dan indikasi geografis dilindungi di pasar tujuan.",
            )
        elif key == "shipping":
            body = label(
                "Use ISPM-15 compliant packaging, book freight with forwarder, and prepare packing list + B/L.",
                "Gunakan kemasan patuh ISPM-15, booking freight dengan forwarder, dan siapkan packing list + B/L.",
            )
        elif key == "timeline_costs":
            body = label(
                "Budget 2-6 weeks for compliance preparation plus freight transit time; include certification costs.",
                "Anggarkan 2-6 minggu untuk persiapan kepatuhan ditambah waktu transit; sertakan biaya sertifikasi.",
            )
        sections.append({
            "key": key,
            "title_en": en_title,
            "title": id_title if is_id else en_title,
            "body": body,
        })
    return {"sections": sections, "country": country, "from_cache": False}


# ---------------------------------------------------------------------------
# Regulasi prioritas desa — khusus untuk komoditas pertanian/perikanan/kerajinan
# ---------------------------------------------------------------------------
from app.seed_village_commodities import commodity_group_for_chapter, chapter_of


VILLAGE_REGULATORY_PRIORITIES = {
    "pertanian": [
        {"title": "Karantina Pertanian — PP No. 28 Tahun 2024",
         "detail": "Semua hasil kebun/tanaman (biji-bijian, buah segar, rempah) wajib mendapat pemeriksaan karantina dan dokumen Phytosanitary Certificate (SKT). Periksa di https://www.barantan.pertanian.go.id/",
         "evidence_fields": ["phytosanitary", "karantina"], "priority": "critical"},
        {"title": "Sertifikat Kesehatan Tumbuhan (Phytosanitary Certificate / SKT)",
         "detail": "Dokumen wajib dari karantina pertanian yang menyatakan komoditas bebas hama & penyakit sesuai negara tujuan.",
         "evidence_fields": ["certificate", "phytosanitary", "hama bebas"], "priority": "critical"},
        {"title": "Pengemasan Standar ISPM-15 (jika menggunakan kemasan kayu)",
         "detail": "Pallet/kayu pembungkus wajib disemprot/fumigasi & diberi stempel IPPC ISPM-15.",
         "evidence_fields": ["ISPM-15", "fumigasi", "pallet kayu"], "priority": "major"},
    ],
    "perikanan": [
        {"title": "Karantina Ikan (KKP) — PP 28/2024",
         "detail": "Ikan hidup/dingin/diawetkan serta turunan produk ikan memerlukan sertifikat kesehatan dari Karantina Ikan (BKIPM Provinsi).",
         "evidence_fields": ["BKIPM", "karantina_ikan", "health_certificate"], "priority": "critical"},
        {"title": "Health Certificate & Traceability",
         "detail": "Surat keterangan kesehatan + traceability (asalnya mana, penangkapan/pelihara).",
         "evidence_fields": ["traceability", "origin", "health_certificate"], "priority": "major"},
        {"title": "HACCP / BPOM untuk produk olahan",
         "detail": "Produksi ikan olahan (fillet, kerupuk, abon) perlu HACCP atau izin BPOM untuk ekspor.",
         "evidence_fields": ["HACCP", "BPOM", "GMP"], "priority": "major"},
    ],
    "kerajinan": [
        {"title": "CITES — bahan dari spesies dilindungi?",
         "detail": "Kriya berbahan kayu/kulit/suku tertentu harus dicek apakah termasuk CITES Appendix. Jika ya, diperlukan CITES permit atau ganti material alternatif.",
         "evidence_fields": ["CITES", "bahan alam", "legalitas kayu", "SVLK"], "priority": "critical"},
        {"title": "Dokumen Asal Bahan Baku (Legalitas Timber/SVLK)",
         "detail": "Bukti legalitas kayu/rattan (SVLK SLE, FLETA, surat asal-usul dari penyuluh kehutanan).",
         "evidence_fields": ["SVLK", "legalitas", "FLETA", "surat asal"], "priority": "major"},
        {"title": "Fumigasi/HT & ISPM-15 untuk kemasan kayu",
         "detail": "Jika ada komponen kayu dalam kemasan kargo, perlu perlakuan HT & stempel IPPC.",
         "evidence_fields": ["ISPM-15", "fumigasi", "kemasan kayu"], "priority": "minor"},
    ],
}


def _evidence_in_record(record: str | None, fields: list[str]) -> bool:
    text = (record or "").lower()
    return any(f in text for f in fields)


def _material_matches_cites_keyword(material: str | None) -> bool:
    keywords = ["mahogany", "ebony", "rosewood", "ivory", "coral", "turtle shell", "rattan limited", "cites"]
    text = (material or "").lower()
    return any(kw in text for kw in keywords)


def infer_commodity_group(product: dict) -> str:
    """Infer commodity group dari `commodity_group` / `commodityGroup` atau HS chapter."""
    group = product.get("commodityGroup") or product.get("commodity_group", "")
    if group:
        return group.lower().strip()
    hs = product.get("hs", "")
    ch = chapter_of(hs)
    if ch is not None:
        return commodity_group_for_chapter(ch)
    cat = product.get("category", "").lower()
    if "kriya" in cat or "rotan" in cat or "anyaman" in cat:
        return "kerajinan"
    return "pertanian"


def normalize_jenis_komoditas(jenis: str | None) -> str | None:
    if not jenis:
        return None
    j = jenis.lower().strip()
    if j in ("pertanian", "peternakan", "kebun", "hasil_bumi"):
        return "pertanian"
    if j in ("perikanan", "laut", "ikan"):
        return "perikanan"
    if j in ("kerajinan", "kriya", "rotan", "anyaman"):
        return "kerajinan"
    return None


def village_regulatory_issues(product: dict, country_code: str, group: str) -> list[dict]:
    """Prioritas isu kepatuhan spesifik desa."""
    issues = []
    priorities = VILLAGE_REGULATORY_PRIORITIES.get(group, [])
    packaging = product.get("packaging", "") or ""
    material = product.get("material_composition", "") or ""
    certs = ", ".join(product.get("certificates", []) or [])

    for item in priorities:
        has_evidence = False
        evidence_fields = item.get("evidence_fields", [])
        if evidence_fields:
            has_evidence = (
                _evidence_in_record(packaging, evidence_fields) or
                _evidence_in_record(certs, evidence_fields) or
                _evidence_in_record(material, evidence_fields)
            )
        else:
            has_evidence = True

        title = item.get("title", "")
        detail = item.get("detail", "")
        severity = "critical" if item.get("priority") == "critical" else ("major" if item.get("priority") == "major" else "minor")
        needs_evidence = item.get("priority") != "minor"

        if not has_evidence:
            issues.append({
                "type": "Regulation",
                "rule_key": f"village_priority_{item.get('title','').replace(' ','')}",
                "your_value": f"Produk dari kelompok {group}",
                "required_value": f"{title}",
                "description": detail,
                "severity": severity,
            })

    if group == "kerajinan" and _material_matches_cites_keyword(material):
        issues.append({
            "type": "CITES",
            "rule_key": "cites_check_required",
            "your_value": material,
            "required_value": "Periksa appendix CITES; siapkan dokumen CITES permit jika applicable",
            "description": "Bahan baku dikategorikan berpotensi masuk CITES. Pastikan legalitas bahan terdokumentasi.",
            "severity": "critical",
        })

    return issues


def product_regulation_issues(product: dict, country_code: str) -> list[dict]:
    """Cek regulasi berbasis produk (EUDR, EU Plant Health, PPWR) dari regulatory_intel.

    Sumber: lampiran 7.1 dokumen proposal — EUDR (EU 2023/1115) wajib bagi
    kopi/kakao/karet/kayu ke EU mulai 30 Des 2026, dengan traceability geolokasi.
    """
    hs = str(product.get("hs") or product.get("hsCode") or product.get("hs_code") or "")
    if not hs:
        return []
    from app.data.regulatory_intel import product_regulations_for

    issues: list[dict] = []
    for reg in product_regulations_for(hs, country_code):
        issues.append({
            "rule_key": reg.get("id", "PRODUCT-REG"),
            "type": "product_regulation",
            "severity": "critical" if reg.get("id") == "EUDR" else "major",
            "title": reg.get("name", "Product regulation"),
            "detail": f"{reg.get('requirement', '')} ({reg.get('ref', '')}). "
                      f"Deadline: {reg.get('deadline', '-')} {reg.get('risk_note', '')}".strip(),
            "source": (reg.get("sources") or [{}])[0].get("url", ""),
            "evidence_fields": ["due_diligence", "geolocation", "traceability"]
            if reg.get("id") == "EUDR"
            else ["certificate", "compliance_doc"],
        })
    return issues


def analyze_product_compliance(product: dict, country_code: str, jenis_komoditas: str | None = None) -> dict[str, Any]:
    """Jalankan semua checker pada data produk dengan prioritas desa.

    pertanian → PP 28/2024+Phyto, kerajinan → CITES+SVLK.
    Ditambah regulasi produk global: EUDR (kopi/kakao/karet/kayu → EU),
    EU Plant Health (buah segar), EU PPWR (kemasan).
    Return menyimpan `commodityGroup`.
    """
    group = normalize_jenis_komoditas(jenis_komoditas) or infer_commodity_group(product)
    issues = []
    issues += village_regulatory_issues(product, country_code, group)
    issues += product_regulation_issues(product, country_code)
    issues += check_ingredient_compliance(product, country_code)
    issues += check_specification_compliance(product, country_code)
    issues += check_packaging_compliance(product, country_code)
    score, grade = calculate_readiness_score(issues)
    recommendations = generate_recommendations(issues)
    return {
        "issues": issues,
        "score": score,
        "grade": grade,
        "recommendations": recommendations,
        "commodityGroup": group,
    }


def analyze_product_from_snapshot(product_snapshot: dict, country_code: str) -> dict[str, Any]:
    """Jalankan compliance check dari data snapshot produk (historis).

    Diadaptasi dari ExportReadyAI ComplianceAIService.analyze_product_from_snapshot:
    memungkinkan analisis terhadap kondisi produk pada saat snapshot diambil,
    bukan data produk live yang mungkin sudah berubah.
    """
    issues = []
    issues += check_ingredient_compliance(
        {
            "name": product_snapshot.get("name", ""),
            "description": product_snapshot.get("description", ""),
            "material_composition": product_snapshot.get("material_composition", ""),
        },
        country_code,
    )
    issues += check_specification_compliance(
        {
            "name": product_snapshot.get("name", ""),
            "quality_specs": product_snapshot.get("quality_specs", {}),
        },
        country_code,
    )
    issues += check_packaging_compliance(
        {"name": product_snapshot.get("name", ""), "packaging": product_snapshot.get("packaging", "")},
        country_code,
    )
    score, grade = calculate_readiness_score(issues)
    return {
        "issues": issues,
        "score": score,
        "grade": grade,
        "recommendations": generate_recommendations(issues),
    }


def snapshot_product(product: dict) -> dict[str, Any]:
    """Buat snapshot produk + enrichment pada saat analisis."""
    enriched = db.get_by("product_enrichments", productId=str(product.get("id", "")))
    return {
        "id": product.get("id"),
        "name": product.get("name"),
        "category": product.get("category"),
        "description": product.get("description", ""),
        "material_composition": product.get("material_composition", ""),
        "production_technique": product.get("production_technique", ""),
        "finishing_type": product.get("finishing_type", ""),
        "quality_specs": product.get("quality_specs", {}),
        "packaging": product.get("packaging", ""),
        "dimensions_l_w_h": product.get("dimensions_l_w_h", {}),
        "weight_net": product.get("weight_net"),
        "weight_gross": product.get("weight_gross"),
        "hs": product.get("hs", "TBD"),
        "hs_code": product.get("hs", "TBD"),
        "sku": (enriched or {}).get("skuGenerated") or product.get("sku", ""),
        "origin": product.get("origin", ""),
        "updatedAt": product.get("updatedAt", ""),
    }


def snapshot_regulations(country_code: str) -> list[dict]:
    """Snapshot regulasi negara pada saat analisis."""
    return country_data.get_regulations(country_code)
