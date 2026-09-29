# 04 — Insights

Kelompok menu **Insights**: mengubah data operasional menjadi keputusan
(analytics), laporan (reports), dan jejak tata kelola (audit).

---

## Analytics (Intelijen Eksekutif)

### `/analytics`
- **Peran:** Exporter, Finance, Forwarder, CustomsBroker, Buyer, KepalaDesa
  (semua peran yang punya modul analytics)
- **Guna:** Dasbor ringkas performa perdagangan: pipeline, piutang, risiko,
  jaringan mitra, dan lane prioritas.
- **Fitur:**
  - Metrik dari `GET /analytics/overview/` (proyek aktif, nilai pipeline,
    produk, analisis, katalog, buyer aktif, forwarder, nilai order).
  - **Lane** dari `GET /analytics/lanes/` (proyek teratas dengan kesiapan & risiko).
  - **Refresh** (`POST /analytics/refresh/`) menghitung ulang + stempel waktu.
  - **Ringkasan AI** (`POST /analytics/ai/summary/`) — narasi kondisi & fokus.
  - Metrik klien: piutang (`amount - paid`), compliance kritis, shipment exception,
    jaringan buyer/supplier berkualifikasi.
- **Terhubung ke:** `$lib/api/analytics.ts` + `listTradeProjects`, `listPayments`,
  `listComplianceRequirements`, `listShipments`, `listBuyers`, `listSuppliers`.
- **Manfaat:** Pandangan eksekutif satu layar; fokus pada hambatan bernilai besar.

---

## Reports (Laporan)

### `/reports` dan `/reports/[id]`
- **Peran:** semua peran dengan modul reports
- **Guna:** Membuat & mengelola laporan intelijen ekspor.
- **Fitur:** daftar laporan (tipe, periode, status, owner); buat laporan,
  **generate** (isi bagian & insight), **jadwalkan** (`schedule`), ubah, hapus;
  detail dengan bagian & insight.
- **Terhubung ke:** `$lib/api/reports.ts` → `/reports/`,
  `POST /reports/{id}/generate/`, `POST /reports/{id}/schedule/`.
- **Manfaat:** Pelaporan berkala (mis. executive brief) tanpa menyusun manual.

---

## Audit Log (Tata Kelola)

### `/audit`
- **Peran:** Admin
- **Guna:** Jejak audit semua aksi di workspace (traceability & governance).
- **Fitur:** daftar event (waktu, aktor, aksi, modul, entitas, keparahan, detail);
  juga dipakai di **activity drawer** AppShell (umpan terbaru).
- **Terhubung ke:** `$lib/api/audit.ts` → `GET /audit/`.
- **Manfaat:** Kepatuhan & investigasi; membuktikan siapa melakukan apa.

---

## Manfaat kelompok Insights

- Mengubah volume transaksi menjadi **keputusan**: pasar mana, risiko apa, arus kas.
- Menyediakan **bukti tata kelola** yang diminta auditor/mitra.
- Semua angka berasal dari modul operasional (bukan diinput terpisah), sehingga
  konsisten dan dapat dipercaya.
