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
- **Persistence** — data tersimpan ke SQLite via `app/db.py` (tetap tersedia dalam API memory store).
- **AI service** — `app/ai.py` dengan dua mode: `mock` (default, deterministik, tanpa API key — dipakai demo & test) dan `remote` (OpenAI-compatible `/chat/completions`, diatur via `MAUEKSPOR_AI_MODE`, `MAUEKSPOR_AI_API_KEY`, `MAUEKSPOR_AI_BASE_URL`, `MAUEKSPOR_AI_MODEL`). Dipakai untuk HS classification, deskripsi katalog, market insight, rekomendasi compliance, dan balasan chat Copilot. Bila remote gagal/tak terkonfigurasi, endpoint jatuh kembali ke nilai statis.
- CRUD & action endpoint: auth, products (+ enrich), trade-projects, business-profiles (+ certifications), users, export-analysis (+ regulation-recommendations), buyers, buyer-requests, forwarders, catalogs, costing, markets, RFQ, quotations, orders, compliance, documents, shipments, payments, tasks, dan modul statis lain.

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
| `MAUEKSPOR_CORS_ORIGINS` | `["http://localhost:5173", ...]` |

## Test

```bash
.venv/bin/python -m pytest tests -q -p no:cacheprovider
```

Meliputi auth flow, RBAC, refresh rotation, smoke semua koleksi, kontrak `path+method` frontend (`tests/test_frontend_contract.py`), dan kontrak payload runtime per-request persis seperti yang dikirim frontend (`tests/test_payload_contract.py`).

## Deployment

```bash
cd ../backend
docker build -t mauekspor-backend .
```

Atau pakai `docker-compose` di root repo (backend + frontend sekaligus), lihat `docker-compose.yml`.