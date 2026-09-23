# MauEkspor Frontend

SvelteKit 5 (Svelte 5 runes) + Tailwind v4 + shadcn-svelte — antarmuka workspace ekspor-impor untuk UMKM Indonesia.

## Struktur penting

- `src/routes/` — 50+ halaman workspace + landing/login/register
- `src/lib/api/` — klien HTTP per-domain (`apiFetch` di `client.ts`), satu file per modul. Termasuk klien fitur inti ExportReadyAI: `marketing.ts` (Market Intelligence + Pricing), `countries.ts`, `hs-codes.ts`, serta upgrade `products.ts` (enrich + AI MI/pricing/description), `catalogs.ts` (gambar/varian/AI/publik), `export-analysis.ts` (compare/reanalyze/regulasi 10 bagian), `costing.ts` (EXW/FOB/CIF + PDF + exchange rate), `buyer-requests.ts` (matching), `forwarders.ts` (profil/review/rekomendasi/statistik), `buyers.ts` (profil buyer), `educational.ts` (CRUD + upload), `chat.ts` (sessions + suggestions)
- `src/lib/api/remote-list.svelte.ts` — `createRemoteList`/`loadById`: ambil data dari backend, fallback ke seed saat API tak tersedia (seamless offline)
- `src/lib/data/trade.ts` — tipe TypeScript semua entitas + mock data (fallback)
- `src/lib/components/` — `AppShell`, `AppSidebar`, komponen shadcn-svelte (`ui/*`)

## Halaman fitur inti (diadaptasi dari ExportReadyAI-fe)

- **Marketing** (`/marketing`) — dua tab: **Market Intelligence** (negara direkomendasikan + forwarder per negara) dan **Pricing Calculator** (EXW/FOB/CIF + breakdown + kurs), keduanya via AI backend.
- **Export Analysis** (`/export-analysis`, `/create`, `/compare`, `/[id]`, `/[id]/regulation-recommendations`) — compliance check, snapshot produk, reanalyze, compare 2-5 negara, panduan regulasi 10 bagian dengan toggle ID/EN.
- **Katalog** (`/catalogs/[id]`) — gambar, varian, AI description, publish/unpublish.
- **Costing** (`/costing/[id]`) — breakdown EXW/FOB/CIF, kapasitas kontainer, download PDF, kurs.
- **Chat** (`/chat`) — sesi CRUD + saran pertanyaan + balasan AI.
- **Buyer Request** (`/buyer-requests/[id]`) — matched catalogs dengan skor & alasan.
- **Forwarder** (`/forwarders/[id]`) — review, statistik rating, rekomendasi.
- **Profil Buyer/Forwarder** (`/buyers/profile`, `/buyers/my-profile`, `/forwarders/profile`, `/forwarders/my-profile`) — buat/lihat/update profil.
- **Educational Admin** (`/educational/admin/*`) — CRUD modul & artikel + upload file.

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