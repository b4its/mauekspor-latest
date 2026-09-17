# MauEkspor Frontend

SvelteKit 5 (Svelte 5 runes) + Tailwind v4 + shadcn-svelte — antarmuka workspace ekspor-impor untuk UMKM Indonesia.

## Struktur penting

- `src/routes/` — 50+ halaman workspace + landing/login/register
- `src/lib/api/` — klien HTTP per-domain (`apiFetch` di `client.ts`), satu file per modul. Termasuk klien fitur inti ExportReadyAI: `marketing.ts` (Market Intelligence + Pricing), `countries.ts`, `hs-codes.ts`, serta upgrade `products.ts` (enrich + AI MI/pricing/description), `catalogs.ts` (gambar/varian/AI/publik), `export-analysis.ts` (compare/reanalyze/regulasi 10 bagian), `costing.ts` (EXW/FOB/CIF + PDF + exchange rate), `buyer-requests.ts` (matching), `forwarders.ts` (profil/review/rekomendasi/statistik), `buyers.ts` (profil buyer), `educational.ts` (CRUD + upload), `chat.ts` (sessions + suggestions)
- `src/lib/api/remote-list.svelte.ts` — `createRemoteList`/`loadById`: ambil data dari backend, fallback ke seed saat API tak tersedia (seamless offline)
- `src/lib/data/trade.ts` — tipe TypeScript semua entitas + mock data (fallback)
- `src/lib/components/` — `AppShell`, `AppSidebar`, komponen shadcn-svelte (`ui/*`)
- `src/lib/stores/session.svelte.ts` — state machine auth: `loading → authenticated | unauthenticated`

## Autentikasi (Auth Flow)

Frontend menggunakan **Bearer token** yang disimpan di **sessionStorage** browser:

1. **Login:** `LoginForm` → `session.login()` → `POST /auth/login/` → response berisi `access_token` & `refresh_token` di `meta`
2. **Token disimpan:** `setAccessToken()` + `setRefreshToken()` → sessionStorage (`mauekspor_access_token`, `mauekspor_refresh_token`)
3. **Setiap request:** `apiFetch()` menyertakan header `Authorization: Bearer <access_token>`
4. **Page reload:** Token dipulihkan dari sessionStorage (tahan reload browser)
5. **401 → Refresh:** `attemptRefresh()` mengirim `X-Refresh-Token: <refresh_token>` → dapat token baru. Jika gagal, token dibersihkan
6. **Logout:** `clearTokens()` → hapus sessionStorage + redirect ke `/login`

> **Penggunaan:** Buka `/login`, masuk dengan akun seed (admin@mauekspor.example / admin123). Setelah login, semua halaman workspace bisa melakukan operasi baca & tulis. Halaman dapat dilihat tanpa login (GET publik), tapi operasi tulis (buat/edit/hapus) perlu login.

## Koneksi ke backend

- `src/lib/api/client.ts` — `apiFetch<T>` memanggil `VITE_API_BASE_URL`, menyertakan `Authorization: Bearer` header, dan otomatis me-refresh token saat `401` (sekali, lalu retry). Juga menyertakan `credentials: 'include'` untuk cookie fallback.
- Semua list page memakai `createRemoteList`; semua detail page memakai `loadById` (fallback ke seed, hasil API menimpa via merge).
- Semua tombol action (create/edit/approve/confirm/sync/…) memanggil helper API masing-masing; respons gagal ditampilkan sebagai error inline.
- Kontrak endpoint terhadap backend diuji di `backend/tests/test_frontend_contract.py` dan `test_payload_contract.py`.

## Menjalankan

```bash
pnpm install
cp .env.example .env   # isi VITE_API_BASE_URL (default http://localhost:8000/api/v1)
pnpm run dev            # Development → http://localhost:5173
pnpm run build          # Production build → pnpm run preview (http://localhost:3000)
```

## Verifikasi

```bash
pnpm run check    # svelte-check, target 0 errors 0 warnings
pnpm run test     # vitest, 246 test
pnpm run build    # vite build (target .svelte-kit/output, adapter-node)
```