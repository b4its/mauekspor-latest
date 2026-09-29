"""Ekstraksi isi berkas untuk pratinjau & analisis AI (PRD §Fitur File).

Modul ini membaca isi berkas yang diunggah agar bisa ditampilkan di UI dan
dianalisis oleh asisten AI. Hanya memakai pustaka standar Python (zipfile +
xml.etree) sehingga tidak menambah dependensi baru:

- **Spreadsheet**: `.xlsx` (OOXML) dan `.csv` → baris/sel sebagai tabel.
- **Dokumen**: `.docx` (OOXML), `.txt` → paragraf teks.
- **Presentasi**: `.pptx` (OOXML) → teks per slide.
- **PDF**: ekstraksi teks sederhana dari aliran `Tj`/`TJ` (best-effort).
- **Gambar/arsip/lainnya**: dikembalikan sebagai metadata saja.

Semua fungsi bersifat *best-effort*: berkas yang rusak atau format tak dikenal
tidak melempar exception, melainkan mengembalikan struktur dengan `kind`
"unknown" dan catatan `note`.
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from dataclasses import dataclass, field
from typing import Any

# Batas ukuran teks yang diekstrak agar tidak membebani memori / kuota AI.
MAX_PREVIEW_CHARS = 20_000
MAX_ROWS = 200
MAX_SHEETS = 5
MAX_SLIDES = 30

_OOXML_NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/package/2006/relationships",
}


@dataclass
class Preview:
    """Hasil ekstraksi isi berkas yang siap dikirim ke klien/AI."""

    kind: str  # spreadsheet | document | presentation | pdf | image | archive | text | unknown
    summary: str = ""
    text: str = ""
    sheets: list[dict[str, Any]] = field(default_factory=list)
    slides: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    note: str = ""
    truncated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "summary": self.summary,
            "text": self.text,
            "sheets": self.sheets,
            "slides": self.slides,
            "paragraphs": self.paragraphs,
            "metadata": self.metadata,
            "note": self.note,
            "truncated": self.truncated,
        }


def _clip(text: str, limit: int = MAX_PREVIEW_CHARS) -> tuple[str, bool]:
    """Potong teks bila melebihi batas; kembalikan (teks, terpotong?)."""
    if len(text) <= limit:
        return text, False
    return text[:limit], True


def _zip_read(data: bytes, member: str) -> str | None:
    """Baca satu anggota zip sebagai teks UTF-8 (None bila tak ada)."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            with zf.open(member) as fh:
                return fh.read().decode("utf-8", errors="replace")
    except (zipfile.BadZipFile, KeyError, OSError):
        return None


def _zip_members(data: bytes, predicate) -> list[str]:
    """Daftar nama anggota zip yang lolos predicate, terurut."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            return sorted(name for name in zf.namelist() if predicate(name))
    except (zipfile.BadZipFile, OSError):
        return []


def _xml_texts(xml: str, ns: str, tag: str) -> list[str]:
    """Ambil semua teks elemen `tag` pada namespace `ns` secara berurutan."""
    from xml.etree import ElementTree as ET

    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return []
    out: list[str] = []
    for el in root.iter(f"{{{ns}}}{tag}"):
        if el.text:
            out.append(el.text)
    return out


# ── Spreadsheet (.xlsx) ───────────────────────────────────────────────────────
def _col_index(cell_ref: str) -> int:
    """Konversi referensi sel (mis. 'B3') → indeks kolom 0-based."""
    letters = re.match(r"([A-Z]+)", cell_ref or "")
    if not letters:
        return 0
    idx = 0
    for ch in letters.group(1):
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx - 1


def _extract_xlsx(data: bytes) -> Preview:
    shared: list[str] = []
    shared_xml = _zip_read(data, "xl/sharedStrings.xml")
    if shared_xml:
        from xml.etree import ElementTree as ET

        try:
            root = ET.fromstring(shared_xml)
            for si in root.iter(f"{{{_OOXML_NS['s']}}}si"):
                parts = [t.text or "" for t in si.iter(f"{{{_OOXML_NS['s']}}}t")]
                shared.append("".join(parts))
        except ET.ParseError:
            pass

    sheet_files = _zip_members(
        data, lambda n: n.startswith("xl/worksheets/sheet") and n.endswith(".xml")
    )
    sheets: list[dict[str, Any]] = []
    for sheet_path in sheet_files[:MAX_SHEETS]:
        xml = _zip_read(data, sheet_path)
        if not xml:
            continue
        from xml.etree import ElementTree as ET

        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            continue
        rows: list[list[str]] = []
        for row in root.iter(f"{{{_OOXML_NS['s']}}}row"):
            if len(rows) >= MAX_ROWS:
                break
            cells: dict[int, str] = {}
            for c in row.iter(f"{{{_OOXML_NS['s']}}}c"):
                ref = c.get("r", "")
                ctype = c.get("t", "")
                value = ""
                v_el = c.find(f"{{{_OOXML_NS['s']}}}v")
                if v_el is not None and v_el.text is not None:
                    value = v_el.text
                    if ctype == "s":
                        try:
                            value = shared[int(value)]
                        except (ValueError, IndexError):
                            pass
                elif ctype == "inlineStr":
                    parts = [t.text or "" for t in c.iter(f"{{{_OOXML_NS['s']}}}t")]
                    value = "".join(parts)
                cells[_col_index(ref)] = value
            if cells:
                width = max(cells) + 1
                rows.append([cells.get(i, "") for i in range(width)])
        sheets.append({"name": sheet_path.split("/")[-1].replace(".xml", ""), "rows": rows})

    total_rows = sum(len(s["rows"]) for s in sheets)
    summary = f"Spreadsheet dengan {len(sheets)} sheet dan {total_rows} baris data."
    flat_lines: list[str] = []
    for s in sheets:
        flat_lines.append(f"### Sheet: {s['name']}")
        for r in s["rows"]:
            flat_lines.append(" | ".join(str(x) for x in r))
    text, truncated = _clip("\n".join(flat_lines))
    return Preview(
        kind="spreadsheet",
        summary=summary,
        text=text,
        sheets=sheets,
        truncated=truncated,
        metadata={"sheet_count": len(sheets), "row_count": total_rows},
    )


def _extract_csv(data: bytes) -> Preview:
    raw = data.decode("utf-8", errors="replace")
    reader = csv.reader(io.StringIO(raw))
    rows: list[list[str]] = []
    for i, row in enumerate(reader):
        if i >= MAX_ROWS:
            break
        rows.append(row)
    summary = f"Berkas CSV dengan {len(rows)} baris dan {len(rows[0]) if rows else 0} kolom."
    fmt = "\n".join(" | ".join(r) for r in rows)
    text, truncated = _clip(fmt)
    return Preview(
        kind="spreadsheet",
        summary=summary,
        text=text,
        sheets=[{"name": "CSV", "rows": rows}],
        truncated=truncated,
        metadata={"row_count": len(rows)},
    )


# ── Dokumen (.docx) ───────────────────────────────────────────────────────────
def _extract_docx(data: bytes) -> Preview:
    xml = _zip_read(data, "word/document.xml")
    if not xml:
        return Preview(kind="document", note="Struktur .docx tidak dikenali.")
    paragraphs: list[str] = []
    from xml.etree import ElementTree as ET

    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return Preview(kind="document", note="Isi dokumen tidak dapat diparsing.")
    for p in root.iter(f"{{{_OOXML_NS['w']}}}p"):
        parts = [t.text or "" for t in p.iter(f"{{{_OOXML_NS['w']}}}t")]
        line = "".join(parts).strip()
        if line:
            paragraphs.append(line)
    text, truncated = _clip("\n\n".join(paragraphs))
    return Preview(
        kind="document",
        summary=f"Dokumen dengan {len(paragraphs)} paragraf teks.",
        text=text,
        paragraphs=paragraphs,
        truncated=truncated,
        metadata={"paragraph_count": len(paragraphs)},
    )


# ── Presentasi (.pptx) ────────────────────────────────────────────────────────
def _extract_pptx(data: bytes) -> Preview:
    slide_files = _zip_members(
        data,
        lambda n: n.startswith("ppt/slides/slide") and n.endswith(".xml"),
    )

    def _slide_num(path: str) -> int:
        m = re.search(r"slide(\d+)\.xml", path)
        return int(m.group(1)) if m else 0

    slide_files.sort(key=_slide_num)
    slides: list[str] = []
    for path in slide_files[:MAX_SLIDES]:
        xml = _zip_read(data, path)
        if not xml:
            continue
        texts = _xml_texts(xml, _OOXML_NS["a"], "t")
        slides.append("\n".join(t for t in texts if t.strip()))
    text, truncated = _clip("\n\n".join(f"## Slide {i + 1}\n{s}" for i, s in enumerate(slides)))
    return Preview(
        kind="presentation",
        summary=f"Presentasi dengan {len(slides)} slide.",
        text=text,
        slides=slides,
        truncated=truncated,
        metadata={"slide_count": len(slides)},
    )


# ── PDF (best-effort) ─────────────────────────────────────────────────────────
def _extract_pdf(data: bytes) -> Preview:
    """Ekstraksi teks PDF sederhana dari operator Tj/TJ (tanpa dependensi)."""
    text_parts: list[str] = []
    try:
        raw = data.decode("latin-1", errors="replace")
    except Exception:  # pragma: no cover - decode jarang gagal dgn latin-1
        return Preview(kind="pdf", note="PDF tidak dapat dibaca sebagai teks.")

    # Ambil literal string yang diapit tanda kurung lalu operator Tj/TJ.
    for match in re.finditer(r"\(((?:[^()\\]|\\.)*)\)\s*Tj", raw):
        text_parts.append(_unescape_pdf(match.group(1)))
    for match in re.finditer(r"\[(.*?)\]\s*TJ", raw, flags=re.DOTALL):
        for inner in re.finditer(r"\(((?:[^()\\]|\\.)*)\)", match.group(1)):
            text_parts.append(_unescape_pdf(inner.group(1)))
    joined = " ".join(t for t in text_parts if t.strip())
    joined = re.sub(r"[ \t]+", " ", joined).strip()
    if not joined:
        return Preview(
            kind="pdf",
            summary="PDF berisi teks yang tidak dapat diekstrak otomatis (kemungkinan hasil pemindaian/gambar).",
            note="Teks PDF tidak terekstrak (mungkin hasil scan).",
        )
    text, truncated = _clip(joined)
    return Preview(
        kind="pdf",
        summary=f"Dokumen PDF dengan sekitar {len(joined)} karakter teks.",
        text=text,
        truncated=truncated,
    )


def _unescape_pdf(s: str) -> str:
    return (
        s.replace("\\(", "(")
        .replace("\\)", ")")
        .replace("\\\\", "\\")
        .replace("\\n", "\n")
        .replace("\\r", "")
        .replace("\\t", "\t")
    )


# ── Dispatcher ────────────────────────────────────────────────────────────────
_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
_ARCHIVE_EXT = {".zip", ".rar"}


def extract(filename: str, content: bytes) -> Preview:
    """Ekstrak isi berkas berdasarkan ekstensi. Selalu mengembalikan Preview."""
    import os

    name = (filename or "").lower()
    ext = os.path.splitext(name)[1]

    try:
        if ext == ".xlsx":
            return _extract_xlsx(content)
        if ext == ".csv":
            return _extract_csv(content)
        if ext == ".docx":
            return _extract_docx(content)
        if ext == ".pptx":
            return _extract_pptx(content)
        if ext == ".pdf":
            return _extract_pdf(content)
        if ext == ".txt":
            raw = content.decode("utf-8", errors="replace")
            text, truncated = _clip(raw)
            return Preview(
                kind="text",
                summary=f"Berkas teks dengan sekitar {len(raw)} karakter.",
                text=text,
                truncated=truncated,
            )
        if ext == ".doc":
            return Preview(kind="document", note="Format .doc lama belum didukung pratinjau isi.")
        if ext == ".xls":
            return Preview(kind="spreadsheet", note="Format .xls lama belum didukung pratinjau isi.")
        if ext in _IMAGE_EXT:
            return Preview(kind="image", summary="Berkas gambar.", metadata={"bytes": len(content)})
        if ext in _ARCHIVE_EXT:
            return Preview(kind="archive", summary="Berkas arsip terkompresi.")
    except Exception as exc:  # pragma: no cover - pengaman terakhir
        return Preview(kind="unknown", note=f"Gagal membaca berkas: {type(exc).__name__}.")

    return Preview(kind="unknown", note=f"Tipe berkas '{ext or 'tanpa ekstensi'}' belum didukung pratinjau isi.")


def ai_context(preview: Preview, max_chars: int = 8_000) -> str:
    """Bentuk ringkasan isi berkas untuk konteks prompt AI."""
    body = preview.text or ""
    if len(body) > max_chars:
        body = body[:max_chars] + "\n...[isi dipotong]..."
    header = f"Jenis: {preview.kind}\nRingkasan: {preview.summary or '-'}"
    if not body:
        header += f"\nCatatan: {preview.note or 'Isi teks tidak tersedia.'}"
    return f"{header}\n\nIsi berkas:\n{body}".strip()
