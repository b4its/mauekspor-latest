# MauEkspor

**Workspace ekspor-impor berbasis AI untuk UMKM Indonesia** — satu platform dari kesiapan produk, analisis pasar & kepatuhan, penawaran/costing, katalog digital, hingga dokumen dan pelacakan pengiriman.

> Status saat ini: **berfungsi penuh dengan backend.** Frontend adalah antarmuka kerja lengkap yang terhubung ke backend FastAPI (list, detail, form create, dan action/button di semua modul memakai `src/lib/api/*.ts`; mock di `src/lib/data/trade.ts` hanya fallback saat API tak tersedia). Backend punya auth JWT (refresh rotation), RBAC, audit log, dan persistensi SQLite. Fitur inti ExportReadyAI telah diadaptasi lengkap: **enrichment produk (HS code + SKU)**, **Market Intelligence**, **Pricing Calculator (EXW/FOB/CIF)**, **Costing nyata + exchange rate + PDF**, **Export Analysis dengan compliance check, snapshot produk/regulasi, reanalyze, compare, dan rekomendasi regulasi 10 bagian (ID/EN)**, **master data negara + regulasi + HS codes (6.941 kode)**, **katalog dengan gambar + varian + AI description + listing publik**, **buyer request matching**, **forwarder profile + review + rekomendasi + statistik**, **buyer profile**, **educational CRUD + upload file**, dan **chat sessions + suggestions**. Modul AI berjalan dua mode: `mock` (default) dan `remote` (OpenAI-compatible via `MAUEKSPOR_AI_MODE=remote`).

## ✨ Penjelasan untuk Orang Awam (Tanpa Jargon Teknis)

> Bagian ini khusus untuk yang **bukan programmer** — pemilik usaha, tim UMKM, atau siapa saja yang ingin paham "MauEkspor itu apa sih?" dengan bahasa sehari-hari.

### MauEkspor itu seperti apa? 🚢

Bayangkan Anda punya usaha ekspor kecil. Selama ini urusan ekspor biasanya berantakan:

- Data produk ada di **Excel**,
- Chat buyer ada di **WhatsApp**,
- Dokumen dan invoice tersebar di **email**,
- Jadwal pengiriman ada di **catatan tempel**.

MauEkspor menyatukan semuanya ke **satu "meja kerja" digital**. Semua data — produk, pembeli, penawaran harga, dokumen, sampai pengiriman — ada di satu tempat yang rapi, dan saling terhubung otomatis.

### Analogi sederhana

| Bagian | Analogi | Artinya |
|---|---|---|
| **Tampilan (frontend)** | Ruang tamu restoran | Yang Anda lihat dan klik di layar — halaman, tombol, tabel |
| **Mesin (backend)** | Dapur restoran | Bagian belakang yang mengolah data, menyimpan, dan menghitung — tidak terlihat, tapi semua kerjaan di sini |
| **Database** | Gudang penyimpanan | Tempat semua data tersimpan permanen (SQLite) |
| **API** | Menu pesanan | "Bahasa perantara" yang menghubungkan ruang tamu dan dapur — tampilan meminta data, mesin mengirimkannya |

### Fitur-fitur dalam bahasa manusia

1. **Profil usaha** — isi data perusahaan & sertifikasi sekali, dipakai di mana-mana.
2. **Data produk** — catat spesifikasi produk (berat, kemasan, kode HS). Kode HS itu seperti "nomor KTP" internasional untuk barang, supaya bea cukai mengenali barang Anda.
3. **Analisis pasar** — sistem memberi tahu: "Kalau kirim kopi ke Jepang, ini aturannya, ini sertifikat yang dibutuhkan, ini peluangnya." Semua dibantu AI.
4. **Hitung harga (costing)** — tinggal masukkan modal & target untung, sistem menghitung harga jual otomatis, termasuk ongkos kirim. Istilah **EXW/FOB/CIF** itu cuma "sejauh mana ongkos & tanggung jawab Anda" — dari pabrik, sampai pelabuhan, sampai ke pembeli.
5. **Katalog digital** — tampilkan produk Anda rapi seperti toko online, lengkap dengan foto dan varian.
6. **RFQ & quotation** — buyer kirim permintaan (RFQ), Anda balas dengan penawaran harga (quotation), jadi order.
7. **Dokumen & pengiriman** — sistem bantu siapkan invoice, packing list, dan lacak status kiriman sampai tiba.
8. **AI Copilot (chat)** — tanya-tanya seperti ke asisten: "Ringkas risiko ekspor ke Jepang" — dijawab otomatis.

### Peran pengguna

- **Eksportir / UMKM** — pemakai utama: mengelola produk, analisis, penawaran, pengiriman.
- **Buyer** — pembeli yang mengirim kebutuhan dan melihat katalog.
- **Forwarder** — jasa pengiriman/logistik yang muncul di rekomendasi rute.
- **Admin** — mengatur akun, paket, dan dukungan.

### Istilah teknis yang sering muncul (versi sederhana)

- **Login / autentikasi** — sistem memastikan hanya orang yang berhak yang bisa masuk, lewat email + kata sandi. Data login diacak (dihash) sehingga aman.
- **Peran & izin (RBAC)** — tiap orang hanya melihat & mengubah bagian yang jadi urusannya. Admin bisa semua; buyer tidak bisa mengubah data produk Anda.
- **Log audit** — catatan siapa melakukan apa, kapan. Berguna kalau ada masalah, bisa ditelusuri.
- **Mode AI mock vs remote** — mode *mock* memakai jawaban contoh (tanpa biaya, untuk demo); mode *remote* memakai AI sungguhan (OpenAI) kalau sudah siap.
- **Unit test** — "pemeriksaan kesehatan" otomatis untuk memastikan semua fitur tetap berfungsi setiap kali ada perubahan. Proyek ini punya ratusan pemeriksaan seperti itu, jadi perubahan tidak merusak yang lain.

### Cara memakai (untuk pemakai biasa)

1. Buka aplikasi (di komputer: `http://localhost:5173`).
2. Login dengan akun yang diberikan admin.
3. Mulai dari **Dashboard** — lihat ringkasan, lalu ikuti checklist "kesiapan ekspor".
4. Isi **profil bisnis**, lalu **tambahkan produk**.
5. Gunakan **AI** untuk analisis pasar & hitung harga.
6. Kelola **order, dokumen, dan pengiriman** sampai selesai.

> Kalau ada bagian yang masih membingungkan, tanya lewat **Chat Copilot** di dalam aplikasi — dijawab langsung.

---

## Daftar Isi
- [Penjelasan untuk Orang Awam](#-penjelasan-untuk-orang-awam-tanpa-jargon-teknis)
- [Tentang Proyek](#tentang-proyek)
- [Arsitektur](#arsitektur)
- [Tech Stack](#tech-stack)
- [Struktur Repository](#struktur-repository)
- [Prasyarat](#prasyarat)
- [Instalasi & Menjalankan](#instalasi--menjalankan)
- [Modul & Fitur](#modul--fitur)
- [Status Implementasi](#status-implementasi)
- [Dokumentasi Lanjutan](#dokumentasi-lanjutan)
- [Referensi & Inspirasi](#referensi--inspirasi)

---

## Tentang Proyek

MauEkspor menyatukan alur kerja ekspor-impor yang biasanya tersebar di spreadsheet, WhatsApp, dan email ke dalam satu workspace terstruktur:

1. **Siapkan** — lengkapi profil bisnis, sertifikasi, dan data produk (spesifikasi, kemasan, berat, HS code).
2. **Analisis** — jalankan analisis pasar & kepatuhan tujuan ekspor (regulasi, tarif, larangan, rekomendasi dokumen/sertifikat).
3. **Tawarkan** — bangun katalog digital, hitung costing (EXW/FOB/CIF/DAP), kelola RFQ dari buyer, dan konversi ke quotation.
4. **Eksekusi** — ubah quotation menjadi sales order, siapkan & validasi dokumen ekspor, pesan & lacak pengiriman lewat forwarder, kelola pembayaran/milestone.
5. **Kelola** — pantau semua proyek dagang lewat dashboard, compliance checklist, task, notifikasi, laporan, dan audit log.

Ditujukan untuk empat peran: **Exporter/UMKM** (pengguna utama), **Buyer**, **Forwarder**, dan **Admin** — mengikuti model peran yang sama dengan referensi [ExportReadyAI](https://github.com/ExportReadyAI/ExportReadyAI-fe), namun MauEkspor fokus pada satu workspace terintegrasi (bukan platform matchmaking multi-tenant) dengan penekanan pada **trade project lifecycle** end-to-end.

## Arsitektur

```
┌──────────────────────────┐        HTTP (JSON, /api/v1/*)        ┌───────────────────────────┐
│  Frontend (SvelteKit 5)  │ ────────────────────────────────────▶ │  Backend (FastAPI)        │
│  - Tailwind v4 + shadcn  │ ◀──────────────────────────────────── │  - Pydantic schemas       │
│  - src/lib/api/*.ts      │        {"data": T, "meta": {...}}     │  - SQLite persistence     │
│  - src/lib/data/trade.ts │                                       │  - JWT + refresh rotation │
│    (mock, fallback saat  │                                       │  - RBAC + audit log       │
│    API tak tersedia)     │                                       └───────────────────────────┘
└──────────────────────────┘
```

- **Frontend** memiliki dua sumber data secara sengaja: `src/lib/data/trade.ts` (mock statis, dipakai sebagai fallback saat API tidak tersedia) dan `src/lib/api/*.ts` (klien HTTP nyata ke backend, `apiFetch` di `src/lib/api/client.ts` menembak `VITE_API_BASE_URL` dengan `credentials: include` dan retry refresh saat 401). Semua halaman workspace — list, detail, form create/edit, dan tombol action — sudah terhubung ke endpoint backend (pola `createRemoteList`/`loadById` dengan fallback ke seed saat API tak tersedia).
- **Backend** menyediakan **230+ endpoint** yang kontraknya teruji penuh terhadap `src/lib/api/*.ts` (`tests/test_frontend_contract.py`) dan payload per-request persis seperti yang dikirim frontend (`tests/test_payload_contract.py`), plus auth JWT (refresh rotation), RBAC per-role, audit log, persistensi SQLite, **filtering/pagination** pada list utama, dan **notifikasi otomatis** pada aksi penting. Fitur inti diadaptasi dari repo referensi [ExportReadyAI](https://github.com/ExportReadyAI/ExportReadyAI): enrichment AI, market intelligence, pricing, costing EXW/FOB/CIF + PDF, export analysis + snapshots + compare + inline compliance editor, countries & regulations, HS codes (6941 kode dari CSV), katalog gambar/varian/publik, buyer-request matching, forwarder reviews/rekomendasi, educational CRUD + upload, chat sessions.

## Tech Stack

| Layer | Teknologi |
|---|---|
| Frontend framework | SvelteKit 5 (Svelte 5 runes), TypeScript |
| Styling & UI | Tailwind CSS v4, shadcn-svelte (`bits-ui`, `tailwind-variants`), `@lucide/svelte` |
| Animasi | AOS (Animate On Scroll) — landing page |
| Adapter deploy frontend | `@sveltejs/adapter-node` |
| Backend framework | FastAPI, Pydantic v2, Uvicorn |
| Testing backend | Pytest + `fastapi.testclient` |
| Package manager | pnpm (frontend, workspace-mode), pip/venv (backend) |

## Struktur Repository

```
mauekspor/
├── frontend/                  # SvelteKit app — lihat frontend/README.md
│   ├── src/routes/            # ~50 halaman workspace + landing/login/register
│   ├── src/lib/components/    # AppShell, AppSidebar, komponen shadcn (ui/*)
│   ├── src/lib/api/           # 30+ klien HTTP, satu file per domain (products.ts, buyers.ts, ...)
│   └── src/lib/data/trade.ts  # mock data & tipe TypeScript untuk semua entitas
```
├── backend/                   # FastAPI app — lihat backend/README.md
│   ├── app/main.py            # entrypoint FastAPI + CORS + auth guard + audit middleware
│   ├── app/api/routes.py      # semua endpoint /api/v1/* (230+)
│   ├── app/core/              # config, security (JWT/PBKDF2), permissions (RBAC)
│   ├── app/data/              # master data: HS codes (CSV 6941 baris) + countries & regulations
│   ├── app/services/          # business logic: pricing, compliance, matching, forwarders, market intel
│   ├── app/db.py              # store + persistensi SQLite
│   ├── app/schemas/           # Pydantic request models
│   ├── app/seed.py            # seed data demo
│   └── tests/                 # pytest: auth, RBAC, refresh, smoke, kontrak frontend, fitur inti
└── guideline/obsidian/        # dokumentasi desain & arsitektur (vault Obsidian)
    ├── frontend/               # design system, sidebar, landing, auth, educational
    └── backend/                # arsitektur FastAPI, kontrak endpoint, roadmap produksi
.github/workflows/ci.yml     # CI: pytest backend + svelte-check & build frontend
```

## Prasyarat

| Software | Versi | Untuk |
|---|---|---|
| Node.js | ≥ 20.x | Frontend |
| pnpm | ≥ 9.x | Frontend (package manager utama, ada `pnpm-lock.yaml`) |
| Python | ≥ 3.11 | Backend |
| pip / venv | bawaan Python | Backend |

## Instalasi & Menjalankan

### Frontend

```bash
cd frontend
pnpm install
cp .env.example .env      # isi VITE_API_BASE_URL (default: http://localhost:8000/api/v1)
pnpm run dev               # buka http://localhost:5173
```

Verifikasi sebelum commit:
```bash
pnpm run check   # svelte-check, harus 0 errors
pnpm run build    # vite build, harus sukses
```

### Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Dokumentasi API otomatis (Swagger): `http://localhost:8000/docs`
Health check: `http://localhost:8000/api/v1/health`

Jalankan test:
```bash
.venv/bin/pytest
```

### CI (GitHub Actions)

`.github/workflows/ci.yml` menjalankan dua job: pytest backend (Python 3.13) serta `pnpm check` + `pnpm build` frontend (Node 20, pnpm 9) — otomatis pada setiap push/PR ke `main`.

### Deployment (Docker)

```bash
docker compose up --build
```
- Backend → http://localhost:8000 (docs di `/docs`)
- Frontend → http://localhost:3000
- Data backend persisten di volume `backend-data` (SQLite).
- Atur secret/asal prod lewat `.env` (lihat `backend/.env.production.example`) dan `VITE_API_BASE_URL` saat build frontend.

## Modul & Fitur

| Kelompok Sidebar | Modul | Ringkasan |
|---|---|---|
| Overview | Dashboard, About | Ringkasan workspace, metrik pipeline |
| Trade Operations | Business Profile, Trade Projects, Products, Export Analysis, Markets, Catalogs | Data inti produk & proyek dagang, analisis kepatuhan & pasar tujuan, katalog digital |
| Commercial | Buyers, Buyer Requests, Suppliers, Forwarders, RFQ, Quotations, Costing, Orders, Payments | CRM buyer/supplier/forwarder, RFQ→Quotation→Order, kalkulasi harga EXW/FOB/CIF, pelacakan pembayaran |
| Fulfillment | Compliance, Tasks, Documents, Shipments | Checklist bukti kepatuhan, dokumen ekspor (invoice/packing list/COO), booking & milestone pengiriman |
| Insights | Analytics, Reports, Audit Log | Dashboard metrik, laporan terjadwal, log audit |
| Workspace | Team, Calendar, Messages, Chat, Files, Notifications, Automations, Integrations, Templates, Knowledge Base, Educational, Marketing | Kolaborasi internal, AI copilot chat, otomasi, dan **Educational** sebagai learning platform (kursus + artikel) |
| Admin | Users, Billing, Support, API Keys, Settings | Manajemen akun, paket, tiket dukungan, API key |

Detail per-modul (data model, halaman, endpoint) ada di dokumentasi Obsidian: [`guideline/obsidian/frontend`](guideline/obsidian/frontend/index.md) dan [`guideline/obsidian/backend`](guideline/obsidian/backend/index.md).

## Status Implementasi

| Bagian | Status |
|---|---|
| UI seluruh 50+ halaman workspace | ✅ Selesai (shadcn-svelte, dark/light, responsive) |
| Landing page, Login, Register | ✅ Selesai — login & register kini terhubung ke backend API (session store + redirect) |
| Educational sebagai learning platform | ✅ Selesai (course player + lesson tracking + admin CRUD modul/artikel + upload file) |
| Backend API (FastAPI, 230+ endpoint) | ✅ Selesai — kontrak `src/lib/api/*.ts` teruji 100% via `test_frontend_contract.py` |
| Autentikasi (JWT + refresh rotation) | ✅ Selesai — PBKDF2, access/refresh token, logout revoke, guard middleware, register-admin |
| RBAC per-role | ✅ Selesai — Admin/Exporter/Buyer/Forwarder/CustomsBroker/Finance |
| Persistensi database | ✅ Selesai — SQLite via `app/db.py`; bisa diganti `MAUEKSPOR_DATABASE_URL` |
| Audit log | ✅ Selesai — semua mutasi tercatat ke `audit_events` |
| Frontend → API (semua halaman) | ✅ Selesai — list, detail, form create/edit, dan action button di seluruh modul memakai backend; fallback ke mock tetap berfungsi |
| Product enrichment (HS code + SKU) | ✅ Selesai — `POST /products/{id}/enrich/` dengan HS loader (6941 kode) + SKU deterministik + fallback pencarian |
| Market Intelligence (AI) | ✅ Selesai — `GET/POST /products/{id}/ai/market-intelligence/` + per katalog; termasuk rekomendasi forwarder per negara |
| Pricing Calculator (AI) | ✅ Selesai — `GET/POST /products/{id}/ai/pricing/` EXW/FOB/CIF + breakdown + kurs |
| Costing nyata | ✅ Selesai — kalkulasi EXW/FOB/CIF (trucking, dokumen, freight per region, asuransi) + kapasitas kontainer **dari dimensi & berat produk** + **AI container optimization** + `GET /costing/{id}/pdf/` |
| Exchange rate service | ✅ Selesai — auto-fetch 24 jam (exchangerate-api), manual/refresh, fallback 15800 |
| Export Analysis | ✅ Selesai — create (compliance checker bahan/spesifikasi/kemasan), snapshot produk & regulasi, **analisis dari snapshot (historis)**, reanalyze, compare 2-5 negara, rekomendasi regulasi 10 bagian (ID/EN + cache) |
| Master data | ✅ Selesai — `GET /countries/` + detail regulasi; `GET /hs-codes/` + autocomplete; admin CRUD negara/regulasi/HS + import CSV |
| Katalog | ✅ Selesai — CRUD, publish/unpublish, gambar (list/add/update/delete), varian (type + option, 8 predefined), AI description, MI & pricing, listing publik + **detail publik** & forwarder |
| Buyer request matching | ✅ Selesai — skor berbobot (kategori 35%, HS 30%, spesifikasi 25%, kapabilitas 5%, volume 5%), status, matched-catalogs/umkm, **alur Buyer pilih katalog → close request** |
| Forwarder | ✅ Selesai — profil (create/me/update), review (CRUD + auto-recalc rating), rekomendasi, statistik |
| Buyer profile | ✅ Selesai — profil importer (create/me/update) |
| Chat Copilot | ✅ Selesai — sessions CRUD, suggestions, balasan AI per konteks |
| Integration AI (remote mode) | ✅ Selesai — `MAUEKSPOR_AI_MODE=remote` + `MAUEKSPOR_AI_API_KEY` (OpenAI-compatible); default `mock` deterministik |
| Upload file (dokumen, gambar, bukti) | ✅ Selesai — `POST /files/upload/` multipart (max 25MB), `POST /educational/articles/{id}/upload-file/` (max 10MB), `GET /files/{id}/download/` |

## Dokumentasi Lanjutan

Dokumentasi desain & arsitektur tersimpan sebagai vault Obsidian di [`guideline/obsidian/`](guideline/obsidian/):

- **Frontend** — [`guideline/obsidian/frontend/index.md`](guideline/obsidian/frontend/index.md): design system, struktur sidebar, landing page, halaman auth, educational learning platform, inventaris komponen.
- **Backend** — [`guideline/obsidian/backend/index.md`](guideline/obsidian/backend/index.md): arsitektur FastAPI, kontrak endpoint per-domain, skema data, dan roadmap menuju backend produksi.

Buka folder `guideline/obsidian/` sebagai vault di [Obsidian](https://obsidian.md/) untuk navigasi wikilink (`[[...]]`) antar-catatan.

## Referensi & Inspirasi

Model peran, daftar modul, dan pola fitur AI pada proyek ini merujuk pada platform sejenis:
- Frontend referensi: [ExportReadyAI/ExportReadyAI-fe](https://github.com/ExportReadyAI/ExportReadyAI-fe) (Next.js + Django REST)
- Komponen UI: [shadcn-svelte](https://www.shadcn-svelte.com/)
