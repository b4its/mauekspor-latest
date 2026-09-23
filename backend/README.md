# MauEkspor API

FastAPI backend untuk workspace export-import MauEkspor. Kontrak endpoint meniru fungsi di `frontend/src/lib/api/*.ts` (prefix `/api/v1`, respons `{"data": T, "meta": {...}}`).

## Menjalankan (dev)

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Docs otomatis: http://localhost:8000/docs

Akun seed:

| Role       | Email                      | Password   |
| ---------- | -------------------------- | ---------- |
| Admin      | admin@mauekspor.example    | admin123   |
| Exporter   | rizal@kopigayo.example     | rizal123   |
| Buyer      | aya@hikari.example         | buyer123   |

## Fitur

- **Persistence SQLite** — semua tabel disimpan ke `records` (payload JSON) di `mauekspor.db`. Matikan dengan `MAUEKSPOR_DISABLE_PERSISTENCE=1` (dipakai test).
- **Auth** — PBKDF2 password hashing, JWT-like access + refresh token, cookie HttpOnly (`access_token`, `refresh_token`), juga bisa via header `Authorization: Bearer`.
- **Refresh token rotation** — setiap refresh mem-revoke token lama dan menerbitkan pasangan baru; token bekas/replay ditolak `401`. Logout me-revoke refresh token.
- **RBAC** — role `Admin | Exporter | Buyer | Forwarder | CustomsBroker | Finance`. Mutation diblokir `403` bila role tidak berhak atas modul; modul `users`, `audit`, `api-keys`, `settings` read-only untuk Admin.
- **Audit log** — semua mutasi tercatat ke `audit_events` (aktor, aksi, modul, entity, severity).
- **Master data HS codes** — `app/data/harmonized-system.csv` (6941 kode HS 2022) + `sections.csv`, dimuat via `app/data/hs_loader.py` (pencarian kata kunci + autocomplete + konteks AI).
- **Master data negara & regulasi** — `app/data/countries.py`: 14 negara tujuan + regulasi (Ingredient/Labeling/Physical) untuk compliance checker.
- **Service layer** — `app/services/`: `pricing.py` (EXW/FOB/CIF + exchange rate + kontainer + PDF), `compliance.py` (cek bahan/spesifikasi/kemasan + skor kesiapan + rekomendasi regulasi 10 bagian ID/EN), `matching.py` (skor buyer-request), `forwarders.py` (rating/rekomendasi/statistik), `market_intel.py` (market intelligence + pricing + deskripsi katalog AI).
- **AI service** — `app/ai.py` dengan dua mode: `mock` (default, deterministik, tanpa API key — dipakai demo & test) dan `remote` (OpenAI-compatible `/chat/completions`, diatur via `MAUEKSPOR_AI_MODE`, `MAUEKSPOR_AI_API_KEY`, `MAUEKSPOR_AI_BASE_URL`, `MAUEKSPOR_AI_MODEL`). Dipakai untuk HS classification, deskripsi katalog, market intelligence, pricing, rekomendasi compliance, dan balasan chat Copilot. Bila remote gagal/tak terkonfigurasi, endpoint jatuh kembali ke nilai statis.
- **230+ endpoint** — seluruh kontrak `src/lib/api/*.ts` + fitur inti ExportReadyAI: enrichment produk (HS + SKU), market intelligence & pricing per produk, export analysis (compliance + snapshot + reanalyze + compare + regulasi 10 bagian), costing nyata + PDF, katalog (gambar/varian/AI/publik), buyer request matching, forwarder (profil/review/rekomendasi/statistik), buyer profile, educational CRUD + upload, chat sessions + suggestions, countries + HS codes, admin CRUD negara/regulasi/HS + import CSV.

## Env vars (prefix `MAUEKSPOR_`)

Lihat `app/core/config.py`. Contoh produksi: `.env.production.example`.

| Variabel | Default |
| --- | --- |
| `MAUEKSPOR_DATABASE_URL` | `sqlite:///./mauekspor.db` |
| `MAUEKSPOR_SECRET_KEY` | `change-me-in-production` |
| `MAUEKSPOR_ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `MAUEKSPOR_REFRESH_TOKEN_EXPIRE_DAYS` | `7` |
| `MAUEKSPOR_UPLOAD_DIR` | `./uploads` (dir penyimpanan file upload) |
| `MAUEKSPOR_AI_MODE` | `mock` |
| `MAUEKSPOR_AI_API_KEY` | (kosong) |
| `MAUEKSPOR_AI_BASE_URL` | `https://api.openai.com/v1` |
| `MAUEKSPOR_AI_MODEL` | `gpt-4o-mini` |
| `MAUEKSPOR_ADMIN_CODE` | `admin-bootstrap-2026` (kode bootstrap `POST /auth/register-admin/`) |
| `MAUEKSPOR_CORS_ORIGINS` | `["http://localhost:5173", ...]` |

## Test

```bash
.venv/bin/python -m pytest tests -q -p no:cacheprovider
```

Meliputi auth flow, RBAC, refresh rotation, smoke semua koleksi, kontrak `path+method` frontend (`tests/test_frontend_contract.py`), kontrak payload runtime per-request persis seperti yang dikirim frontend (`tests/test_payload_contract.py`), dan **20 test fitur inti** (`tests/test_features.py`: enrichment, market intelligence, pricing, export analysis + snapshot + compare + regulasi, countries, HS codes, costing + PDF, katalog gambar/varian/AI/publik, buyer request matching, forwarder, buyer profile, educational, chat sessions, dashboard summary, filtering/pagination, notifikasi otomatis, settings, audit CSV).

## Deployment

```bash
cd ../backend
docker build -t mauekspor-backend .
```

Atau pakai `docker-compose` di root repo (backend + frontend sekaligus), lihat `docker-compose.yml`.