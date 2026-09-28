# guideline/plana — Dokumen Perencanaan Produk

Folder ini menampung dokumen perencanaan (PRD) yang **dilacak di git** (folder
`guideline/` lainnya diabaikan; lihat `.gitignore`).

## Isi
- **`PRD-MauEkspor.md`** — Product Requirements Document lengkap: latar belakang,
  tujuan & metrik, persona/journey, kebutuhan fungsional (FR-*) & non-fungsional
  (NFR-*), gap analysis, roadmap bertahap (Phase 0–6), risiko, dan sumber primer.
- **`regulatory-sources.json`** — Registry sumber regulasi/perdagangan primer
  (machine-readable) untuk provenance: `source_url`, tanggal berlaku, status
  review. Wajib diverifikasi ke dokumen resmi sebelum dipakai sebagai nasihat.

## Prinsip
1. Keamanan & integritas data sebelum fitur.
2. Alur ekspor = state machine bergerbang, bukan modul lepas.
3. Rekomendasi regulasi wajib bersumber, bertanggal, dan ditinjau manusia.
4. AI bersifat *advisory*, tidak menggantikan temuan deterministik.
5. UI tidak boleh menampilkan kegagalan API sebagai data bisnis valid.

## Cara memakai
- Gunakan PRD §8 (Gap Analysis) sebagai backlog prioritas.
- Gunakan PRD §9 (Roadmap) untuk urutan eksekusi & exit criteria.
- Saat menambah konten regulasi, isi provenance dari `regulatory-sources.json`
  dan tandai `review_status`.
