# 00 — Platform Foundation (Auth, Shell, Global)

Fondasi yang dipakai **semua** halaman: autentikasi, kerangka tampilan, kontrol
peran, komponen global, dan klien API. Memahami bagian ini menjelaskan mengapa
halaman lain tampil/berperilaku demikian.

---

## Landing Publik

### `/`
- **Rute:** `frontend/src/routes/+page.svelte`
- **Peran:** publik (tanpa login)
- **Guna:** Halaman pemasaran/etalase produk MauEkspor (hero, fitur, CTA).
- **Fitur:** narasi nilai platform; statistik ringkas; menu (Sheet) untuk masuk;
  **tema** (`ThemeToggle`); tombol menuju `/login` atau `/dashboard` bila sudah login.
- **Terhubung ke:** store sesi (`getStatus`, `getUser`), `$lib/data/trade.ts`
  (angka contoh), komponen `Logo`, `AosInit`.
- **Manfaat:** Akuisisi pengguna; menjelaskan value proposition sebelum daftar.

---

## Autentikasi & Akun

### `/login`
- **Rute:** `frontend/src/routes/login/+page.svelte`
- **Peran:** publik (belum login)
- **Guna:** Masuk ke workspace ekspor dengan email + password.
- **Fitur:**
  - Form login (`LoginForm.svelte`) → `POST /api/v1/auth/login/`.
  - Menyimpan `access_token`/`refresh_token` (cookie HttpOnly + store sesi).
  - Rate-limit login (maks 5 gagal/60 detik → 429) dan pesan error yang jelas.
- **Terhubung ke:** `$lib/api/auth.ts`, store sesi `$lib/stores/session.svelte.ts`,
  halaman `/dashboard` setelah sukses.
- **Manfaat:** Gerbang keamanan tunggal; mencegah akses anonim ke data workspace.

### `/register`
- **Rute:** `frontend/src/routes/register/+page.svelte`
- **Peran:** publik
- **Guna:** Pendaftaran mandiri (self-signup) UMKM/eksportir/desa baru.
- **Fitur:** `SignupForm.svelte` → `POST /api/v1/auth/register/` dengan nama,
  email, password (kebijakan min 8 karakter + huruf & angka), peran, organisasi.
- **Terhubung ke:** `$lib/api/auth.ts`.
- **Manfaat:** Onboarding tanpa campur tangan admin; pertumbuhan pengguna.

### `/register-admin`
- **Rute:** `frontend/src/routes/register-admin/+page.svelte`
- **Peran:** publik (dengan `admin_code` rahasia)
- **Guna:** Membuat akun Admin pertama/terkontrol.
- **Fitur:** Pendaftaran admin yang divalidasi dengan `admin_code` (dibandingkan
  `hmac.compare_digest` di backend) untuk mencegah self-elevation sembarangan.
- **Terhubung ke:** `POST /api/v1/auth/register/` (jalur admin).
- **Manfaat:** Kontrol akses istimewa; mencegah eskalasi hak akses.

### `/users`
- **Rute:** `frontend/src/routes/users/+page.svelte` (dan `/users/[id]`)
- **Peran:** Admin
- **Guna:** Daftar & kelola seluruh akun pengguna.
- **Fitur:** cari (`search`), filter `role`, paginasi (`limit`/`offset`), detail
  `/users/[id]`, hapus akun `DELETE /users/{id}/`.
- **Terhubung ke:** `$lib/api/users.ts` → `GET/DELETE /api/v1/users/`.
- **Manfaat:** Tata kelola pengguna & kepatuhan akun.

---

## Kerangka & Navigasi

### `/dashboard`
- **Rute:** `frontend/src/routes/dashboard/+page.svelte`
- **Peran:** semua (ALWAYS_ALLOWED)
- **Guna:** Beranda workspace — ringkasan kesiapan ekspor & langkah berikutnya.
- **Fitur:**
  - Kartu KPI: jumlah produk, analisis pasar, nilai pipeline, permintaan buyer,
    forwarder terverifikasi, tinjauan risiko.
  - **Checklist kesiapan ekspor** (5 langkah) dengan progres %: lengkapi profil,
    tambah produk, jalankan enrichment, buat analisis, publikasikan katalog.
  - **Peta Potensi Desa** (`VillagePotentialMap`): sebaran desa mitra + skor kesiapan.
  - Grafik pipeline per tahap, kepatuhan per tingkat, peluang pasar, modul edukasi.
  - Peringatan bila profil bisnis belum lengkap.
  - **Aksi Cepat**: tambah produk, buat katalog, analisis pasar, permintaan buyer.
- **Terhubung ke:** `getDashboardSummary()` (`/business-profiles/dashboard/summary/`),
  `listProducts`, `listTradeProjects`, `listExportAnalyses`, `listBuyerRequests`,
  `listForwarders`, `listComplianceRequirements`, `listEducationalModulesV2`.
- **Manfaat:** Satu layar untuk tahu "apa yang menghambat" dan "apa langkah
  berikutnya" — mengurangi trial-and-error eksportir baru.

### `/about`
- **Rute:** `frontend/src/routes/about/+page.svelte`
- **Peran:** semua
- **Guna:** Penjelasan produk dan tujuan platform (public shell).
- **Fitur:** narasi sistem operasi dagang ekspor-impor; nilai & alur.
- **Manfaat:** Edukasi pengunjung; konteks sebelum mendaftar.

### `AppShell` — kerangka tiap halaman (komponen)
- **Berkas:** `frontend/src/lib/components/AppShell.svelte`
- **Guna:** Membungkus halaman: sidebar, breadcrumb, pencarian perintah,
  bel notifikasi, umpan aktivitas, toggle bahasa, toggle tema, tombol kembali,
  dan asisten AI.
- **Fitur global:**
  - **Command palette** (pencarian perintah) — lompat cepat antar modul.
  - **Activity drawer** — umpan audit terbaru (`listAuditEvents`).
  - **Notifications** — bell dengan pesan belum dibaca (`listNotifications`).
  - **ThemeToggle** — mode terang/gelap.
  - **Toggle bahasa (ID/EN)** — `$lib/i18n.svelte`.
  - **Breadcrumb + tombol kembali** untuk halaman detail.
- **Terhubung ke:** `$lib/roleAccess.ts` (filter navigasi), store sesi, audit,
  notifikasi.
- **Manfaat:** Konsistensi UX, navigasi cepat, dan kontrol akses yang tampak di UI.

### `AppSidebar` / `AdminSidebar` (komponen)
- **Berkas:** `frontend/src/lib/components/AppSidebar.svelte`, `AdminSidebar.svelte`
- **Guna:** Menu samping yang **disaring per peran**.
- **Fitur:** grup nav (Overview … Admin), badge tiket risiko pada Compliance,
  kartu "Nuxim AI active", menu akun (checklist, akun, billing, notifikasi, logout).
- **Terhubung ke:** `navGroups` (`$lib/data/trade.ts`), `visibleNavGroups()`.
- **Manfaat:** Menu yang tampil ⇔ yang boleh dibuka (mencegah "tampil tapi ditolak").

---

## Kontrol Peran & Akses

- **Sumber kebenaran UI:** `frontend/src/lib/roleAccess.ts`
  - `HREF_MODULE`: peta rute → modul backend.
  - `ROLE_READ_MODULES`: modul yang boleh dibaca per peran.
  - `allowedHrefs()`, `canViewPath()`, `visibleNavGroups()`.
- **Penegakan backend:** `backend/app/core/permissions.py` + middleware
  `require_auth_for_mutations` (`main.py`).
- **Manfaat:** Keamanan berlapis (UI + server), konsisten antara menu dan API.

---

## Komponen Global Lain

| Komponen | Guna | Dipakai di |
|---|---|---|
| `GlobalAiAssistant.svelte` | Asisten AI mengambang (regulasi, costing, kepatuhan) | Semua halaman (via AppShell) |
| `CountrySelect.svelte` | Pemilih negara searchable (kode ISO) | Form produk, analisis, marketing, dll. |
| `SearchableSelect.svelte` | Dropdown dengan pencarian | Pemilihan entitas |
| `Pagination.svelte` | Navigasi halaman list | Semua list |
| `SortSelect.svelte` | Urutkan kolom | List dengan sort |
| `BulkActionsBar.svelte` | Aksi massal (hapus/enrich) | List dengan seleksi |
| `ConfirmDialog.svelte` + `confirm.svelte.ts` | Konfirmasi terpusat | Hapus/aksi destruktif |
| `DataStateBanner.svelte` | Menampilkan mode data/fallback | Menandai data contoh vs nyata |
| `FileViewerDialog.svelte` | Pratinjau & analisa berkas | Files, dokumen |
| `LocationMapPicker.svelte` | Peta pilih titik + geocode | Villages, Business Profile |
| `ModuleQuiz.svelte` | Kuis interaktif | Educational |
| `VillagePotentialMap.svelte` | Peta Leaflet sebaran desa | Dashboard, Villages |
| `MarkdownRenderer/` | Render markdown aman | Reference, Educational |

---

## Klien API & Utilitas

- **`$lib/api/client.ts`**: `apiFetch<T>`, `ApiError`, `getAccessToken`,
  `downloadFile`, `exportPath`/`csvExportUrl`, `ExportScope` (search/status/ids).
- **`$lib/api/remote-list.svelte.ts`**: `createRemoteList` — state list + `load()`,
  `upsert()`, `remove()`, loading/error; **seed fallback hanya mode demo**.
- **`$lib/utils/`**: `format` (mata uang/status), `pagination`, `sort`,
  `urlFilters`, `date`, `labels` (terjemahan nilai enum), `confirm`, `bulkSelection`.
- **`$lib/i18n.svelte.ts`**: kamus ID/EN + `t()`.
- **`$lib/stores/`**: `session.svelte.ts` (auth), `aiAssistant.svelte.ts`.
- **`$lib/data/trade.ts`**: tipe domain + data seed demo + `navGroups`.

---

## Manfaat keseluruhan fondasi

- **Konsistensi**: pola list/filter/konfirmasi/error seragam di 100+ halaman.
- **Keamanan**: RBAC ditegakkan di UI dan server.
- **Efisiensi**: asisten AI, command palette, dan filter URL memangkas langkah.
- **Integritas**: pemisahan tegas data nyata vs fallback demo.
