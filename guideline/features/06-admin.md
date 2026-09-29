# 06 — Admin & Platform Controls

Kelompok menu **Admin** plus kontrol platform (billing, support, API keys,
settings). Akses paling sensitif — umumnya **Admin-only** (selaras
`ADMIN_ONLY_MODULES` di UI dan `ADMIN_ONLY_MODULES` di backend).

---

## Admin Panel (Pusat Komando Data)

### `/admin`
- **Peran:** Admin
- **Guna:** Pusat komando & administrasi lintas 50+ tabel data.
- **Fitur:**
  - Daftar **semua tabel** + jumlah record (`GET /admin/tables/`).
  - **CRUD generik** semua tabel: list dengan search/pagination
    (`GET /admin/data/{table}/`), detail, buat, ubah, hapus
    (`/admin/data/{table}/{id}/`).
  - Status AI + tombol **test AI** (`/admin/ai/status/`, `/admin/ai/test/`).
  - Memakai `AdminSidebar` (sidebar khusus).
- **Terhubung ke:** `$lib/api/admin.ts` → `/api/v1/admin/...`.
- **Manfaat:** Pemeliharaan data & operasi darurat tanpa akses DB langsung;
  visibilitas kesehatan sistem.

---

## Users (Manajemen Akun)

### `/users` dan `/users/[id]`
Lihat `00-platform-foundation.md`. Ringkas:
- **Peran:** Admin.
- **Guna:** Kelola akun (cari, filter peran, paginasi, detail, hapus).
- **Terhubung ke:** `$lib/api/users.ts` → `/users/`, `/users/{id}/`.
- **Manfaat:** Tata kelola pengguna & keamanan akun.

---

## Billing (Langganan & Penggunaan)

### `/billing`
- **Peran:** Admin
- **Guna:** Kelola langganan & penggunaan workspace.
- **Fitur:** tampilkan record billing (plan, status, periode, penggunaan vs limit);
  **ganti plan** (`change-plan`); **unduh invoice** (JSON) & **PDF invoice**.
- **Terhubung ke:** `$lib/api/billing.ts` → `/billing/`,
  `POST /billing/change-plan/`, `POST /billing/{id}/invoice/`,
  `GET /billing/{id}/invoice.pdf/`.
- **Manfaat:** Kontrol biaya & tagihan; transparansi kuota.

---

## Support (Help Desk)

### `/support`
- **Peran:** semua peran (tiket miliknya); Admin mengelola
- **Guna:** Dukungan produk & tiket bantuan.
- **Fitur:** daftar tiket (kategori, status, prioritas, owner), buat tiket,
  **selesaikan**, ubah, hapus/batch; ekspor CSV.
- **Terhubung ke:** `$lib/api/support.ts` → `/support/`,
  `POST /support/{id}/resolve/`.
- **Manfaat:** Masalah pengguna tertangani; umpan balik produk.

---

## API Keys (Kontrol Akses Developer)

### `/api-keys`
- **Peran:** Admin
- **Guna:** Mengelola kunci akses API untuk integrasi.
- **Fitur:** daftar kunci (prefix, status, scope, pemilik, terakhir dipakai);
  buat (nama + scope), **cabut** (`revoke`), hapus.
- **Terhubung ke:** `$lib/api/api-keys.ts` → `/api-keys/`,
  `POST /api-keys/{id}/revoke/`.
- **Manfaat:** Integrasi aman dengan kontrol akses terbatas (scope).

---

## Countries & Regulations (Admin Intelijen)

### `/admin/countries`
- **Peran:** Admin
- **Guna:** Mengelola master negara & regulasi yang tampil di `/countries`.
- **Fitur:**
  - CRUD negara buatan admin (`createAdminCountry`, `updateAdminCountry`,
    `deleteAdminCountry`).
  - CRUD regulasi per negara (kategori aturan, kata kunci terlarang, spesifikasi
    wajib, deskripsi).
  - **Impor regulasi dari berkas** (`importAdminRegulations(file)`).
  - Menampilkan `regulationsCount`, `_has_profile`, `_is_template`.
- **Terhubung ke:** `$lib/api/admin-countries.ts` → `/admin/countries/...`.
  Regulasi statis (`app/data/countries.py`) + terkurasi (`trade_reference.py`)
  digabung di endpoint `/countries/{code}/`.
- **Manfaat:** Memperkaya basis regulasi tanpa rilis kode; menjaga data tujuan tetap akurat.

---

## Settings (Organisasi & Kontrol Akses)

### `/settings`
- **Peran:** Admin
- **Guna:** Pengaturan organisasi & preferensi workspace.
- **Fitur:** identitas organisasi (nama, negara, jenis entitas, NIB, NPWP),
  mata uang & bahasa, notifikasi, opsi keamanan sesi.
  (Ringkasan dashboard juga memuat konteks internal.)
- **Terhubung ke:** `$lib/api/settings.ts` → `GET/PUT /settings/`.
  Mata uang tampilan terkait `$lib/api/currency.ts`
  (`/settings/currencies/`).
- **Manfaat:** Konfigurasi tenant; dasar legalitas (NIB/NPWP) & lokalisasi.

---

## Manfaat kelompok Admin

- **Tata kelola penuh**: akun, akses, audit, data master.
- **Operasional**: billing, support, integrasi aman (API keys).
- **Kualitas data**: admin negara/regulasi menjaga referensi tetap benar & mutakhir.
- **Keamanan berlapis**: modul admin ditutup di UI maupun backend.

---

## Catatan konsistensi

- Menu Admin hanya tampil untuk `Admin` (`ADMIN_ONLY_HREFS`).
- Middleware backend menegakkan modul `users/audit/api-keys/settings/admin`
  hanya untuk Admin — sehingga "tampil ⇔ boleh dibuka ⇔ boleh diakses".
