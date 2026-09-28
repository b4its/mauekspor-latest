"""Daftar tipe dokumen ekspor yang didukung + matriks dokumen wajib.

PRD §5.8 (FR-DOC-1/FR-COMPL-5): UI tidak boleh menjanjikan tipe dokumen yang
belum didukung. Modul ini menjadi satu sumber kebenaran untuk tipe dokumen,
persyaratan minimal tiap tipe, serta registry dokumen wajib per (negara,
komoditas, incoterm).
"""

from __future__ import annotations

# Tipe dokumen yang benar-benar dapat dibuat sistem.
SUPPORTED_DOCUMENT_TYPES: list[dict] = [
    {"type": "Commercial Invoice", "group": "Commercial", "requiredFields": ["buyer", "value"]},
    {"type": "Packing List", "group": "Commercial", "requiredFields": ["product"]},
    {"type": "Proforma Invoice", "group": "Commercial", "requiredFields": ["buyer", "value"]},
    {"type": "Certificate of Origin", "group": "Certificate", "requiredFields": ["origin", "hsCode"]},
    {"type": "Phytosanitary Certificate", "group": "Certificate", "requiredFields": ["origin", "product"]},
    {"type": "Health Certificate", "group": "Certificate", "requiredFields": ["product"]},
    {"type": "Insurance Certificate", "group": "Logistics", "requiredFields": ["value"]},
    {"type": "Bill of Lading", "group": "Logistics", "requiredFields": ["buyer"]},
]

SUPPORTED_DOCUMENT_TYPE_NAMES: list[str] = [d["type"] for d in SUPPORTED_DOCUMENT_TYPES]

# Kelompok dokumen wajib per komoditas (indikatif, untuk registry & gate).
# Nilai merepresentasikan "type" pada SUPPORTED_DOCUMENT_TYPES.
_REQUIRED_BY_GROUP: dict[str, list[str]] = {
    "pertanian": ["Phytosanitary Certificate", "Certificate of Origin", "Commercial Invoice", "Packing List"],
    "perikanan": ["Health Certificate", "Certificate of Origin", "Commercial Invoice", "Packing List"],
    "kerajinan": ["Certificate of Origin", "Commercial Invoice", "Packing List"],
}
_DEFAULT_REQUIRED = ["Certificate of Origin", "Commercial Invoice", "Packing List"]


def required_documents(commodity_group: str | None, incoterm: str | None = None) -> list[str]:
    """Dokumen wajib berdasarkan kelompok komoditas + incoterm.

    CIF/DAP/DDP menambahkan Insurance Certificate (penjual menanggung asuransi).
    """
    group = (commodity_group or "").lower().strip()
    required = list(_REQUIRED_BY_GROUP.get(group, _DEFAULT_REQUIRED))
    term = (incoterm or "").upper()
    if term in {"CIF", "CIP", "DAP", "DDP"} and "Insurance Certificate" not in required:
        required.append("Insurance Certificate")
    return required


def is_supported(doc_type: str) -> bool:
    return doc_type in SUPPORTED_DOCUMENT_TYPE_NAMES


def spec_for(doc_type: str) -> dict | None:
    for d in SUPPORTED_DOCUMENT_TYPES:
        if d["type"] == doc_type:
            return d
    return None
