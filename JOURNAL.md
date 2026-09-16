# MauEkspor — Project Journal

Log kerja per sesi. Diupdate di akhir setiap sesi kerja, lalu di-commit.
Format: satu entri per sesi, terbaru di atas.

---

## Sesi: Debug browser sungguhan — bug nyata ditemukan & diperbaiki (CORS preflight + tasks)

**Tanggal:** 15 Agustus 2026 (lanjutan sesi "Debug halaman tidak berfungsi")
**Status sesi:** Bug nyata ditemukan & difix; **3 perubahan kode + test + pustaka**.
**Keputusan yang diambil:** Sesi sebelumnya menyimpulkan "auth behavior intended, 0
perubahan kode". Kesimpulan itu **salah** — reproduksi browser sungguhan menemukan bug
nyata. Kini diperbaiki dan diuji.

### Reproduksi browser (puppeteer, login sebagai admin)
Sweep seluruh 40-an route aplikasi (logged-in) → **semua halaman bersih** kecuali:
- `/audit`, `/users`, `/api-keys`, `/settings` → `OPTIONS <modul>/` → **403**,
  browser: `No 'Access-Control-Allow-Origin' header is present` (halaman rusak total).
- `/tasks` → `TypeError: Cannot read properties of undefined (reading 'filter')`.
Login + `/chat` + kirim pesan → **berfungsi penuh** (201/200 dari backend).

### Root cause #1 — CORS preflight dibunuh middleware auth (bug nyata)
`backend/app/main.py`:
- Middleware auth (`@app.middleware("http") require_auth_for_mutations`) meng-gate
  **OPTIONS preflight** untuk modul admin-only (`settings`, `users`, `audit`,
  `api-keys`) dengan `403 Admin access required` **sebelum** CORSMiddleware sempat
  meng-attach header CORS. Browser lalu memblokir request: "No ACAO header".
- Ternyata pula: **urutan middleware salah** dalam framework. `CORSMiddleware`
  didaftarkan di `app.add_middleware(...)` SEBELUM `@app.middleware("http")`,
  sehingga CORS terpasang paling dalam; middleware auth di luarnya. Akibatnya
  **setiap** 401/403 yang di-short-circuit auth middleware keluar TANPA header
  `Access-Control-Allow-Origin` → browser menampilkan error CORS membingungkan,
  bukan error auth yang bisa dibaca.

**Fix (main.py):**
1. Auth middleware: `if request.method == "OPTIONS": return await call_next(request)`
   (preflight selalu diteruskan ke CORS).
2. Pindah `app.add_middleware(CORSMiddleware, ...)` ke PALING AKHIR (setelah
   deklarasi semua middleware `@app.middleware("http")`) agar CORS menjadi
   middleware ***terluar*** dan membungkus semua respons — termasuk 401/403 dari
   middleware auth.

**Verifikasi live (instans uvicorn baru port 8099, sama kode):**
- `OPTIONS /api/v1/settings/` → sekarang **200 + ACAO** (sebelumnya 403).
- anon `POST /api/v1/chat/sessions/` → **401 + ACAO** (browser bisa baca errornya).
- anon `GET /api/v1/settings/` → **403 + ACAO** (real error, bukan CORS blok).

### Root cause #2 — /tasks crash (bug nyata)
`frontend/src/routes/tasks/+page.svelte:145` memanggil `task.checklist.filter(...)`,
tapi record seed backend `backend/app/seed.py:230` (`TSK-COF-LABEL-01`) **tidak punya
field `checklist`** → template crash. Fix: guard `(task.checklist ?? [])` dan
`task.checklist?.length ?? 0`. Halaman detail aman (`{#each undefined}`).

### Perubahan kode
- `backend/app/main.py` — 2 baris OPTIONS pass-through + reorder registrasi CORS
  ke paling akhir (menjadi middleware terluar).
- `frontend/src/routes/tasks/+page.svelte` — guard checklist.
- `backend/tests/test_cors_preflight.py` — 2 test preflight + 1 test BARU
  `test_auth_error_responses_carry_cors_headers` (401/403 dari auth tetap bawa ACAO).
- `JOURNAL.md` — revisi kesimpulan sesi sebelumnya (salah), catat fix.

### Status pengujian
- Backend: `263 passed` (262 lama + 1 test CORS baru).
- Frontend: vitest `246 passed` (19 files), `svelte-check` 0 error / 0 warning.
- Browser: sweep 40 route logged-in → semua bersih pasca-fix (kode lama di :8000
  belum, karena server proses eksternal + `uvicorn` tanpa `--reload`).

### Keadaan & titik terbuka (honest)
- **IMPORTANT:** server live di `:8000` masih menjalankan kode LAMA (pre-fix).
  Proses uvicorn hidup di luar akses agent (`kill` → Operation not permitted;
  `/usr/local/bin/python3.13` tidak ada di sandbox → tidak bisa di-respawn dari sini).
  **User harus merestart backend** agar fix aktif: hentikan `uvicorn app.main:app
  --port 8000` dan jalankan ulang dari `backend/`.
- Setelah restart, verifikasi cepat: `curl -i -X OPTIONS
  http://localhost:8000/api/v1/settings/ -H "Origin: http://localhost:3000"`
  → harus `200` + `access-control-allow-origin: http://localhost:3000`.
- Perilaku auth tetap intended (tulis wajib login → 401 "Not authenticated"); yang
  kita perbaiki adalah lapisan CORS-nya, sehingga browser bisa membaca error itu
  dengan jujur (bukan ditampilkannya sebagai CORS failure).
- 6 endpoint 404 dari template (kpi-reports, budget-report, insurance,
  shipping-companies, subscriptions, statistics) tidak dipanggil halaman mana pun
  di sweep logged-in → belum jadi blocker.

---

## Sesi: Debug "halaman tidak berfungsi" di `localhost:3000` (chat & lainnya)

**Tanggal:** 15 Agustus 2026
**Status sesi:** Investigasi selesai; **tanpa perubahan kode** (working tree bersih).
**Keputusan yang diambil:** Perilaku auth dibiarkan apa adanya (intended). **Tidak ada perubahan kode.**

### Latar belakang
- User melaporkan halaman `http://localhost:3000/chat` (dan halaman lain) "tidak berfungsi"
  dan ingin seluruh sistem berkomunikasi dengan backend dengan benar, tanpa error.
- Instruksi kerja: test dan commit setiap perubahan. (Sesi ini ternyata tidak menghasilkan
  perubahan yang perlu di-commit — lihat bagian Keputusan.)

### Apa yang diverifikasi (semua via HTTP langsung, bukan browser)
Frontend (`:3000`) — app sudah jadi (production build SvelteKit, bukan vite dev):
- Semua 17 route utama (`/`, `/login`, `/dashboard`, `/products`, `/chat`, `/countries`,
  `/export-analysis`, `/buyers`, `/buyer-requests`, `/forwarders`, `/catalogs`, `/costing`,
  `/educational`, `/marketing`, `/settings`, `/notifications`, `/trade-projects`) → **HTTP 200**.
- HTML ter-render SSR penuh (bukan shell kosong); marker SvelteKit `<!--12qhfyh-->`.
- Bundle client dimuat: `start.JIsTzRsL.js` dan `app.CW4fV97H.js` → 200.
- Bukan vite dev: `/@vite/client` → 404; `_app/env.js` = `export const env={}`.
- API base sudah benar & ter-bake di bundle: `http://localhost:8000/api/v1` (ditemukan 7×
  di chunk build). Hipotesis awal "perlu `frontend/.env`" **tidak relevan** — fallback-nya
  sama persis dan sudah masuk ke build. Build lebih baru dari source (13:00 vs 10:11).

Backend (`:8000`) — semua sehat:
- `countries/`, `products/`, `business-profiles/`, `chat/sessions/`, `chat/suggestions/` → 200.
- CORS: preflight dari origin `http://localhost:3000` → `access-control-allow-origin:
  http://localhost:3000` ✓ (allow_credentials=True, methods `*`) — dari
  `backend/app/main.py` + `backend/app/core/config.py`.
- Flow auth + chat end-to-end: `login` → 200 + cookie; `/auth/me/` → 200 dgn cookie,
  401 tanpa cookie; `POST /chat/sessions/` → **200** dgn cookie, **401** tanpa cookie.
- Sweep 36 module endpoint (baca/anon): 26 module → 200; `settings`, `api-keys`, `users`,
  `audit` → 403 (hanya Admin boleh baca); 6 path → 404 (belum ada: `kpi-reports`,
  `budget-report`, `insurance`, `shipping-companies`, `subscriptions`, `statistics`,
  `compliance`).

### Root cause sebenarnya
Bukan bug, bukan CORS, bukan build basi, bukan env yang kurang. Ini **perilaku auth yang
memang didesain**:

`backend/app/main.py:80` — middleware `require_auth_for_mutations`:
- **Semua request tulis** (`POST/PATCH/PUT/DELETE`) di `/api/v1/{module}/...` **wajib
  punya token** (kecuali module `auth` dan path publik: login/register/refresh/logout).
- Tanpa token → `401 Not authenticated`.
- Reads dibuka, kecuali `ADMIN_ONLY_MODULES` (`users`, `audit`, `api-keys`, `settings`)
  → `403 Admin access required` untuk pengguna anonim/non-Admin.
- Modul `chat` ada di daftar tulis Exporter & Buyer (`backend/app/core/permissions.py`).

Konsekuensi di browser saat **belum login**:
- Membaca sesi/saran chat → OK (reads terbuka).
- Klik "+ Baru", kirim pesan, atau klik saran → `POST` → **401** → UI menampilkan
  "Gagal membuat sesi baru." / "Gagal mengirim pesan." — inilah yang dirasakan user
  sebagai "halaman tidak berfungsi".

Dengan kata lain: **first render & semua baca jalan; aksi-aksi (tulis) gagal 401 kalau
belum login.** Ini konsisten di seluruh API, bukan hanya chat.

### Keputusan
- **Perilaku auth dibiarkan as-is (intended).** Tidak mengubah middleware, tidak membuka
  tulis anonim, tidak menambah guard frontend. Sesi ini **0 perubahan kode**; `git status`
  bersih. Sisa sesi teknis yang bisa di-commit = tidak ada (semua sudah di-commit pada
  sesi-sesi sebelumnya).

### Laporan agent lain vs temuan kita — catatan jujur
- Ada laporan ringkasan sebelumnya yang menyatakan sesi "selesai" dan halaman "ok", dengan
  klaim hanya "4 write 401 terisolasi yang memang diharapkan". **Itu tidak akurat**:
  bukan 4 endpoint terisolasi — seluruh jalur tulis API digate oleh satu middleware global.
- Investigasi kita langsung (curl + bundle + preflight + alur login→chat) menunjukkan
  penyebab yang lebih sistematis: gate 401 pada semua aksi tulis tanpa sesi login.
- Tidak ada subagent yang benar-benar dijalankan pada sesi ini; semua verifikasi dilakukan
  langsung, jadi tidak ada laporan subagent yang perlu dibandingkan selain ringkasan tersebut.

### Keadaan & titik terbuka (honest)
- **Belum ada reproduksi browser sungguhan** (mis. Playwright). Kesimpulan di atas kuat
  (dari kode route + curl + CORS + bundle), tapi error eksak yang dilihat user di console
  browser belum terkonfirmasi.
- **Belum ada keputusan produk** soal "harus login untuk pakai fitur aksi":
  - Opsi A (status quo): wajib login untuk semua tulis — perilaku SaaS standar.
  - Opsi B: buka tulis anonim untuk modul tertentu (mis. chat) agar visitor bisa mencoba.
  Opsi belum dipilih. Jika user ingin Opsi B, itu adalah **perubahan kode + keputusan
  keamanan** yang butuh konfirmasi dulu.
- Kemungkinan perbaikan UI di masa depan (belum dilakukan): guard/redirect `/login` untuk
  halaman yang butuh aksi tulis, atau pesan error yang membedakan "401 → silakan login".
- 6 endpoint 404 (`kpi-reports`, `budget-report`, `insurance`, `shipping-companies`,
  `subscriptions`, `statistics`, `compliance`) menandakan halaman yang memanggilnya akan
  gagal — perlu cek korelasi route → endpoint kalau user report "halaman X tidak berfungsi".

### Langkah lanjutan yang disarankan (untuk sesi berikutnya)
1. Reproduksi browser sungguhan (Playwright/puppeteer) untuk menangkap error console
   aktual di `/chat`.
2. Konfirmasi ke user: Opsi A (wajib login) atau Opsi B (tulis anonim utk chat)?
3. Jika Opsi A: tambahkan guard `/login` + pesan "harus login" yang jelas di halaman aksi.
4. Cek 6 module 404: apakah ada halaman frontend yang memanggilnya dan perlu dibuat/aliaskan.
