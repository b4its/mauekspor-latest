# guideline/features — Dokumentasi Fitur per Halaman

Folder ini mendokumentasikan **setiap halaman** aplikasi MauEkspor: apa gunanya,
apa saja fitur di dalamnya, ke modul/endpoint apa ia terhubung, dan apa manfaat
nyatanya. Dokumen ini adalah hasil analisis langsung dari kode (`frontend/src/routes`,
`frontend/src/lib/api`, `backend/app/api/routes.py`), bukan dari asumsi.

## Cara membaca

Setiap entri halaman mengikuti format tetap:

- **Rute** — path URL SvelteKit (`frontend/src/routes/<rute>/+page.svelte`).
- **Peran** — peran pengguna yang boleh melihat (selaras `roleAccess.ts` &
  `backend/app/core/permissions.py`). Lihat legenda di bawah.
- **Guna** — satu kalimat inti halaman ini untuk apa.
- **Fitur** — daftar fitur konkret (tombol/aksi/panel) beserta kegunaannya.
- **Terhubung ke** — API klien (`$lib/api/*`), endpoint backend
  (`/api/v1/...`), dan halaman lain yang ditaut.
- **Manfaat** — dampak bisnis/operasional.

## Legenda peran

| Peran | Fokus |
|---|---|
| **Admin** | Semua modul + panel admin, audit, users, settings |
| **Exporter** | Alur ekspor end-to-end (mayoritas modul) |
| **Buyer** | Portal importer, katalog publik, RFQ/quotations/orders |
| **Forwarder** | Shipments, dokumen, katalog, tracking |
| **CustomsBroker** | Kepatuhan, dokumen, shipment, pembayaran |
| **Finance** | Orders, quotations, payments, costing, billing |
| **KepalaDesa** | Produk desa, potensi desa, kepatuhan, dokumen |

Peran `Admin` memakai `'*'` (semua). `ALWAYS_ALLOWED` untuk **semua peran**:
`/dashboard`, `/about`, `/catalogs/public`, `/countries`, `/hs-codes`, `/reference`.

## Kelompok navigasi (sidebar)

`Overview` · `Trade Operations` · `Commercial` · `Fulfillment` · `Insights` ·
`Workspace` · `Admin` (definisi: `frontend/src/lib/data/trade.ts` → `navGroups`).

## Indeks file

| File | Cakupan |
|---|---|
| [`00-platform-foundation.md`](./00-platform-foundation.md) | Auth, shell, peran, komponen global, klien API, i18n, tema |
| [`01-trade-operations.md`](./01-trade-operations.md) | Business Profile, Trade Projects, Products, Villages, Export Analysis, Markets, Countries, HS Codes, Catalogs |
| [`02-commercial.md`](./02-commercial.md) | Buyers, Buyer Portal/Requests, Suppliers, Forwarders, RFQ, Quotations, Costing, Orders, Payments |
| [`03-fulfillment.md`](./03-fulfillment.md) | Compliance, Tasks, Documents, Shipments |
| [`04-insights.md`](./04-insights.md) | Analytics, Reports, Audit Log |
| [`05-workspace.md`](./05-workspace.md) | Team, Calendar, Messages, Chat, Files, Notifications, Automations, Integrations, Templates, Knowledge, Educational, Reference, Marketing |
| [`06-admin.md`](./06-admin.md) | Admin Panel, Users, Billing, Support, API Keys, Admin Countries, Settings |

## Konvensi lintas halaman

- **Klien API terpusat** (`$lib/api/client.ts`): `apiFetch` (JSON), `ApiError`,
  `downloadFile`, `exportPath`/`csvExportUrl` (unduh CSV/PDF), injeksi bearer token.
- **`createRemoteList`** (`$lib/api/remote-list.svelte.ts`): pembungkus state
  list + `seed` fallback **hanya** saat mode demo; default memakai API nyata.
- **Filter & pencarian persisten URL** (`$lib/utils/urlFilters.ts`): agar tahan
  refresh/back/dibagikan.
- **Konfirmasi terpusat** (`$lib/utils/confirm.svelte.ts` + `ConfirmDialog`),
  bukan `window.confirm`.
- **Prasyarat auth**: semua endpoint baca `/api/v1/*` butuh login; mutasi butuh
  peran yang sesuai (`backend/app/main.py`).
- **AI bersifat advisory**: rekomendasi AI tidak menggantikan temuan deterministik
  dan wajib ditinjau manusia.

## Prinsip integritas data (dipakai di seluruh dokumen ini)

1. Nilai turunan **dihitung backend**, bukan diinput manual (mis. kesiapan desa dari
   profil bisnis; `readiness` produk dari kelengkapan data).
2. UI **tidak** menampilkan kegagalan API sebagai data bisnis valid.
3. Rekomendasi regulasi wajib bersumber, bertanggal, dan bertanda status review.
