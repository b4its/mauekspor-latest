# MauEkspor Frontend

SvelteKit 5 (Svelte 5 runes) + Tailwind v4 + shadcn-svelte — antarmuka workspace ekspor-impor untuk UMKM Indonesia.

## Struktur penting

- `src/routes/` — 50+ halaman workspace + landing/login/register
- `src/lib/api/` — klien HTTP per-domain (`apiFetch` di `client.ts`), satu file per modul
- `src/lib/api/remote-list.svelte.ts` — `createRemoteList`/`loadById`: ambil data dari backend, fallback ke seed saat API tak tersedia (seamless offline)
- `src/lib/data/trade.ts` — tipe TypeScript semua entitas + mock data (fallback)
- `src/lib/components/` — `AppShell`, `AppSidebar`, komponen shadcn-svelte (`ui/*`)

## Menjalankan

```bash
pnpm install
cp .env.example .env   # isi VITE_API_BASE_URL (default http://localhost:8000/api/v1)
pnpm run dev            # http://localhost:5173
```

## Verifikasi

```bash
pnpm run check    # svelte-check, target 0 errors 0 warnings
pnpm run build    # vite build (target .svelte-kit/output, adapter-node)
```

## Koneksi ke backend

- `src/lib/api/client.ts` — `apiFetch<T>` memanggil `VITE_API_BASE_URL`, `credentials: include`, dan otomatis me-refresh token saat `401` (sekali, lalu retry).
- Semua list page memakai `createRemoteList`; semua detail page memakai `loadById` (fallback ke seed, hasil API menimpa via merge).
- Semua tombol action (create/edit/approve/confirm/sync/…) memanggil helper API masing-masing; respons gagal ditampilkan sebagai error inline.
- Kontrak endpoint terhadap backend diuji di `backend/tests/test_frontend_contract.py` dan `test_payload_contract.py`.