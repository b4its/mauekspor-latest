"""HS code loader & search (adapted from ExportReadyAI `products/utils/hs_code_loader.py`).

Memuat dataset HS 2022 dari CSV (`app/data/harmonized-system.csv`, 6941 baris)
dan `sections.csv` (21 bagian) ke dalam memori, lalu menyediakan:
- `search_hs_codes(...)`: pencarian kode HS berdasarkan kata kunci dengan skor relevansi.
- `get_hs_code_context(...)`: konteks HS yang diformat untuk prompt AI.
- `autocomplete(...)`: saran kode HS untuk UI.
"""

from __future__ import annotations

import csv
import os
from functools import lru_cache
from typing import Any

_DATA_DIR = os.path.join(os.path.dirname(__file__))
_HS_CSV = os.path.join(_DATA_DIR, "harmonized-system.csv")
_SECTIONS_CSV = os.path.join(_DATA_DIR, "sections.csv")


class HSCodeLoader:
    """Singleton in-memory loader untuk dataset HS."""

    def __init__(self) -> None:
        self.sections: dict[str, str] = {}
        self.codes: list[dict[str, Any]] = []
        self._index: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        # Sections: Roman numeral -> name
        if os.path.isfile(_SECTIONS_CSV):
            with open(_SECTIONS_CSV, encoding="utf-8-sig") as fh:
                for row in csv.DictReader(fh):
                    section = (row.get("section") or "").strip()
                    name = (row.get("name") or "").strip()
                    if section:
                        self.sections[section] = name

        # HS codes: section, hscode, description, parent, level
        if os.path.isfile(_HS_CSV):
            with open(_HS_CSV, encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    code = (row.get("hscode") or "").strip()
                    if not code:
                        continue
                    record = {
                        "hs_code": code,
                        "section": (row.get("section") or "").strip(),
                        "description": (row.get("description") or "").strip(),
                        "parent": (row.get("parent") or "").strip(),
                        "level": int(row["level"]) if str(row.get("level", "")).isdigit() else 0,
                    }
                    self.codes.append(record)
                    self._index[code] = record

    # ------------------------------------------------------------------ search
    def search_hs_codes(self, keywords: str, max_results: int = 20, min_level: int = 6) -> list[dict[str, Any]]:
        """Cari kode HS dengan skor relevansi kata kunci.

        Skor: frase persis +15, kata per-kata +2, kecocokan 8-digit +3, 6-digit +1.
        """
        terms = [t.lower().strip() for t in keywords.replace(",", " ").split() if len(t.strip()) >= 2]
        if not terms:
            return []
        phrase = " ".join(terms)
        scored: list[tuple[int, dict[str, Any]]] = []
        for record in self.codes:
            desc = (record.get("description") or "").lower()
            if record.get("level", 0) < min_level:
                continue
            score = 0
            if phrase in desc:
                score += 15
            for term in terms:
                if term in desc:
                    score += 2
                if len(term) == 8 and term == record["hs_code"]:
                    score += 3
                if len(term) == 6 and term == record["hs_code"][:6]:
                    score += 1
            if score > 0:
                scored.append((score, record))
        scored.sort(key=lambda pair: (-pair[0], pair[1]["hs_code"]))
        return [r for _, r in scored[:max_results]]

    def get_hs_code(self, hs_code: str) -> dict[str, Any] | None:
        return self._index.get(hs_code)

    def get_hs_code_context(self, keywords: str, max_results: int = 15, min_level: int = 6) -> str:
        """Format blok 'RELEVANT HS CODES' untuk prompt AI."""
        results = self.search_hs_codes(keywords, max_results=max_results, min_level=min_level)
        if not results:
            return ""
        lines = ["RELEVANT HS CODES:"]
        for r in results:
            section_name = self.sections.get(r.get("section", ""), "")
            code = r["hs_code"]
            if len(code) == 6:
                code = f"{code}00"
            lines.append(f"- {code} | {r['description']} (Section {r.get('section', '?')} {section_name})")
        return "\n".join(lines)

    def autocomplete(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Saran HS code untuk UI: cocokkan awalan kode atau kata kunci deskripsi."""
        q = query.strip().lower()
        if not q:
            return []
        if q.isdigit():
            return [r for r in self.codes if r["hs_code"].startswith(q)][:limit]
        return self.search_hs_codes(q, max_results=limit, min_level=2)

    def children_of(self, hs_code: str) -> list[dict[str, Any]]:
        parent = self._index.get(hs_code)
        if not parent:
            return []
        return [r for r in self.codes if r.get("parent") == hs_code]


@lru_cache(maxsize=1)
def get_hs_loader() -> HSCodeLoader:
    return HSCodeLoader()
