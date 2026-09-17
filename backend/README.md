# MauEkspor API

FastAPI backend untuk workspace export-import MauEkspor. Kontrak endpoint meniru fungsi di `frontend/src/lib/api/*.ts` (prefix `/api/v1`, respons `{"data": T, "meta": {...}}`).

## Dokumentasi API (Swagger / OpenAPI)

| URL | Deskripsi |
|-----|-----------|
| `http://localhost:8000/docs` | **Swagger UI** — explore & test semua 240+ endpoint langsung dari browser. Klik "Authorize" → paste `access_token` |
| `http://localhost:8000/redoc` | **ReDoc** — dokumentasi alternatif |
| `http://localhost:8000/openapi.json` | **OpenAPI JSON** — impor ke Postman/Insomnia |

## Autentikasi & Keamanan

- **Login:** `POST /api/v1/auth/login/` → dapatkan `access_token` & `refresh_token` di response `meta`
- **Kirim token:** Sertakan header `Authorization: Bearer <access_token>` di setiap request
- **Refresh:** `POST /api/v1/auth/refresh/` dengan header `X-Refresh-Token: <refresh_token>`
- **Logout:** `POST /api/v1/auth/logout/` — revoke refresh token + hapus cookie
- **Fallback cookie:** Backend juga menerima cookie `access_token` (HttpOnly, SameSite=Lax) untuk kompatibilitas GET
- **Login rate limiting:** max 5 percobaan gagal/60 detik per IP → `429`
- **Password policy:** min 8 karakter + wajib huruf & angka (register)
- **Security headers:** `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection`, `Referrer-Policy`, `Permissions-Policy`, `Cache-Control: no-store`
- **RBAC ketat:** modul `users`, `audit`, `api-keys`, `settings` → hanya Admin (read & write)

> Semua endpoint write (POST/PUT/PATCH/DELETE) memerlukan autentikasi. Endpoint GET publik untuk modul non-admin.

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

- **Persistence** — semua tabel disimpan ke tabel `records` (payload JSONB) di **PostgreSQL** (`postgresql://...`) untuk production/Docker, atau **SQLite** (`sqlite:///...`) untuk dev lokal. Pilih lewat `MAUEKSPOR_DATABASE_URL`. Matikan dengan `MAUEKSPOR_DISABLE_PERSISTENCE=1` (dipakai test).
- **Auth** — PBKDF2 password hashing, JWT-like access + refresh token. Token dikirim via **`Authorization: Bearer`** header. Juga via cookie HttpOnly (`access_token`, `refresh_token`) untuk fallback.
- **Refresh token rotation** — setiap refresh mem-revoke token lama dan menerbitkan pasangan baru; token bekas/replay ditolak `401`. Logout me-revoke refresh token.
- **RBAC** — role `Admin | Exporter | Buyer | Forwarder | CustomsBroker | Finance`. Mutation diblokir `403` bila role tidak berhak atas modul; modul `users`, `audit`, `api-keys`, `settings` khusus Admin (read & write).
- **Rate limiting** — login dibatasi 5 percobaan gagal/60 detik per IP → `429` (anti brute-force).
- **Password policy** — register wajib password min 8 karakter + huruf & angka.
- **Security headers** — middleware menambahkan header keamanan di semua response.
- **Audit log** — semua mutasi tercatat ke `audit_events` (aktor, aksi, modul, entity, severity).
- **Seeder 100+ record/tabel** — saat DB kosong, `app/seed_large.py` meng-seed 100+ record per tabel (50+ tabel) mengikuti alur ekspor: users → products → projects → orders → payments, plus **250 negara** & **6.941 HS codes** dari master data.
- **OpenAPI / Swagger / ReDoc** — dokumentasi API otomatis dengan Bearer auth scheme (tombol "Authorize" di Swagger UI).
- **Master data HS codes** — `app/data/harmonized-system.csv` (6941 kode HS 2022) + `sections.csv`, dimuat via `app/data/hs_loader.py` (pencarian kata kunci + autocomplete + konteks AI).
- **Master data negara & regulasi** — `app/data/countries.py`: 250 negara + regulasi (Ingredient/Labeling/Physical) untuk compliance checker.
- **Service layer** — `app/services/`: `pricing.py` (EXW/FOB/CIF + exchange rate + kontainer + PDF), `compliance.py` (cek bahan/spesifikasi/kemasan + skor kesiapan + rekomendasi regulasi 10 bagian ID/EN), `matching.py` (skor buyer-request), `forwarders.py` (rating/rekomendasi/statistik), `market_intel.py` (market intelligence + pricing + deskripsi katalog AI).
- **AI service** — `app/ai.py` dengan dua mode: `mock` (default, deterministik, tanpa API key — dipakai demo & test) dan `remote` (OpenAI-compatible `/chat/completions`, diatur via `MAUEKSPOR_AI_MODE`, `MAUEKSPOR_AI_API_KEY`, `MAUEKSPOR_AI_BASE_URL`, `MAUEKSPOR_AI_MODEL`). Dipakai untuk HS classification, deskripsi katalog, market intelligence, pricing, rekomendasi compliance, dan balasan chat Copilot. Bila remote gagal/tak terkonfigurasi, endpoint jatuh kembali ke nilai statis.
- **240+ endpoint** — seluruh kontrak `src/lib/api/*.ts` + fitur inti ExportReadyAI: enrichment produk (HS + SKU), market intelligence & pricing per produk, export analysis (compliance + snapshot + reanalyze + compare + regulasi 10 bagian), costing nyata + PDF, katalog (gambar/varian/AI/publik), buyer request matching, forwarder (profil/review/rekomendasi/statistik), buyer profile, educational CRUD + upload, chat sessions + suggestions, countries + HS codes, admin CRUD negara/regulasi/HS + import CSV.

## Env vars (prefix `MAUEKSPOR_`)

Lihat `app/core/config.py`. Contoh produksi: `.env.production.example`.

| Variabel | Default |
| --- | --- |
| `MAUEKSPOR_DATABASE_URL` | `sqlite:///./mauekspor.db` (dev) / `postgresql://mauekspor:mauekspor@localhost:5432/mauekspor` (docker) |
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