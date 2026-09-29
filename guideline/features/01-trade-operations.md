# 01 — Trade Operations

Kelompok menu **Trade Operations**: membangun identitas usaha, master data
produk, potensi desa, analisis pasar, regulasi negara, dan katalog jual.
Ini fondasi yang harus lengkap sebelum modul komersial berjalan.

---

## Business Profile (Identitas UMKM)

### `/business-profile`
- **Peran:** Exporter, KepalaDesa (semua kecuali Admin-only)
- **Guna:** Identitas inti UMKM/desa yang dipakai di seluruh alur (produk,
  kepatuhan, kutipan harga).
- **Fitur:**
  - Skor **Kesiapan Ekspor** yang **dihitung otomatis** dari kelengkapan profil
    (nama & alamat, kapasitas produksi, tahun berdiri, penanggung jawab, status,
    sertifikasi) dan **dipakai juga sebagai dasar kesiapan desa**.
  - Daftar multi-profil dengan dropdown searchable (menangani duplikat nama).
  - Ringkasan detail perusahaan + panel "Wawasan kesiapan".
  - Kelola sertifikasi (checkbox) — mengubah skor.
  - Hapus profil terpusat dengan konfirmasi.
- **Terhubung ke:** `$lib/api/business-profile.ts` → `GET/POST/PATCH/PUT/DELETE
  /api/v1/business-profiles/`, `POST /business-profiles/{id}/certifications/`.
  Menjadi sumber skor bagi `/villages` (via `businessProfileId`) dan langkah
  checklist di `/dashboard`.
- **Manfaat:** Satu sumber kebenaran identitas; kesiapan terukur dari data nyata,
  bukan isian manual.

### `/business-profile/create` dan `/business-profile/edit`
- **Peran:** Exporter
- **Guna:** Membuat / menyunting identitas UMKM.
- **Fitur:** form nama, alamat, kapasitas, tahun, pemilik, status; **pemilih
  lokasi peta** (`LocationMapPicker`) untuk koordinat; simpan ke API.
- **Terhubung ke:** `createBusinessProfile` / `updateBusinessProfile`.
- **Manfaat:** Input terstruktur; lokasi presisi untuk peta.

### `/business-profile/certifications`
- **Peran:** Exporter
- **Guna:** Mengelola klaim sertifikasi **beserta bukti berkas** (dokumen/gambar).
- **Fitur:**
  - Centang sertifikasi (Halal, ISO, HACCP, SVLK, …) **lalu unggah bukti**
    (dokumen/gambar) per sertifikasi → `POST /files/upload/` → `fileId`.
  - Badge "Berbukti" vs "Tanpa bukti" per sertifikasi; tombol lihat/hapus bukti.
  - Simpan ke `POST /business-profiles/{id}/certifications/` (body `items: [{name, fileId}]`).
- **Terhubung ke:** `updateCertifications` (mengirim `items`), `uploadFileBinary`.
  Backend menyimpan `certificationItems` + `certifiedCount`.
- **Manfaat:** **Hanya sertifikasi BERBUKTI yang menambah skor kesiapan** (lihat
  `app/services/readiness.py` → `evidenced_certification_count`); klaim tanpa
  dokumen tetap tersimpan sebagai klaim tetapi tidak menaikkan skor. Mencegah
  "klaim kosong" menggelembungkan kesiapan desa/UMKM.

---

## Trade Projects (Proyek Dagang)

### `/trade-projects`
- **Peran:** Exporter, Forwarder, CustomsBroker
- **Guna:** Mengelola pekerjaan ekspor berbasis proyek (satu proyek = satu
  transaksi/lane ke negara tujuan).
- **Fitur:** daftar + filter status, cari, sort, paginasi; skor kesiapan proyek;
  nilai & risiko; tautan ke detail.
- **Terhubung ke:** `$lib/api/trade-projects.ts` → `GET /api/v1/trade-projects/`.
  Proyek merujuk produk, buyer, negara, incoterm, dan ditaut dari/ke
  quotations, orders, shipments, documents, compliance.
- **Manfaat:** Menyatukan seluruh dokumen/komunikasi per transaksi; memudahkan audit.

### `/trade-projects/new`
- **Peran:** Exporter
- **Guna:** Membuat proyek + workspace transaksi baru.
- **Fitur:** form nama, tipe, produk, buyer, negara, incoterm, target value, ETA.
- **Terhubung ke:** `createTradeProject` → `POST /trade-projects/`.
- **Manfaat:** Memulai alur ekspor terstruktur (bukan chat/email lepas).

### `/trade-projects/[id]`
- **Peran:** Exporter, Forwarder, CustomsBroker
- **Guna:** Halaman kerja satu proyek: ringkasan, tahap, kesiapan, dokumen/pihak terkait.
- **Fitur:** detail lengkap, **sunting kesiapan (%) & tahap**, hapus proyek.
- **Terhubung ke:** `getTradeProject`, `updateTradeProject`, `deleteTradeProject`;
  menaut ke entitas terkait (produk, quotes, shipments).
- **Manfaat:** Pusat kendali per transaksi; progres jelas.

---

## Products (Master Data Komoditas)

### `/products`
- **Peran:** Exporter, KepalaDesa, Buyer, Forwarder
- **Guna:** Katalog master data komoditas/produk ekspor.
- **Fitur:**
  - Filter status (`All/Ready/Enriched/Needs HS Review`), cari, paginasi,
    **filter tersimpan di URL** (tahan refresh/dibagikan).
  - **Batch enrich** (AI menyarankan HS code + SKU + deskripsi B2B) dan batch delete.
  - Penanda `is_village_priority` (komoditas desa unggulan) & kelompok komoditas.
  - Skor **kesiapan produk** + status kesiapan HS.
  - Ekspor CSV.
- **Terhubung ke:** `$lib/api/products.ts` → `GET /products/`,
  `POST /products/batch/enrich/`, `POST /products/batch/delete/`,
  `{id}/ai/*` (market intel & pricing). Data village → `villageId`.
- **Manfaat:** Data terstruktur siap ekspor; HS code & SKU otomatis mengurangi
  salah klasifikasi.

### `/products/new`
- **Peran:** Exporter, KepalaDesa
- **Guna:** Menambah produk baru.
- **Fitur:** form nama, kategori, origin, kemasan, berat, MOQ, lead time,
  deskripsi, komposisi, spesifikasi mutu, sertifikat.
- **Terhubung ke:** `createProduct` → `POST /products/`.
- **Manfaat:** Titik masuk data produk; dasar enrichment & analisis.

### `/products/[id]`
- **Peran:** Exporter, KepalaDesa
- **Guna:** Detail produk + aksi AI.
- **Fitur:** tombol **Enrich** (`POST /products/{id}/enrich/`), **Generate
  deskripsi katalog** (AI), hapus; lihat skor kesiapan dan HS.
- **Terhubung ke:** `enrichProduct`, `generateCatalogDescription`, `deleteProduct`.
- **Manfaat:** Menyiapkan materi jual & klasifikasi dari satu tempat.

### `/products/[id]/enrich`
- **Peran:** Exporter
- **Guna:** Meninjau/menimpa hasil enrichment AI (HS code, SKU, deskripsi EN).
- **Fitur:** tampilkan rekomendasi AI; override manual; simpan.
- **Terhubung ke:** `updateProduct` (`hs`, `sku`, `name_english_b2b`, …).
- **Manfaat:** *Human-in-the-loop* — AI mengusulkan, manusia menetapkan.

### `/products/[id]/edit`
- **Peran:** Exporter
- **Guna:** Menyunting master data produk.

---

## Villages (Potensi & Komoditas Desa)

### `/villages`
- **Peran:** Exporter, KepalaDesa (dan semua via data publik terkait)
- **Guna:** Memetakan potensi komoditas unggulan desa yang siap masuk rantai ekspor.
- **Fitur:**
  - KPI: total desa binaan, desa siap ekspor, butuh pendampingan, komoditas unggulan.
  - Kartu desa dengan **Skor Kesiapan (otomatis)** + label jika belum tertaut profil.
  - CRUD desa (tambah/edit/hapus) dengan **pemilih lokasi peta**.
  - Filter status kesiapan, provinsi, kelompok komoditas; cari; paginasi.
  - Tautan cepat: Analisis Ekspor, Permintaan, Intelijen, Produk terkait.
- **Terhubung ke:** `$lib/api/villages.ts` →
  `GET/POST/PUT/DELETE /villages/`, `GET /villages/map/`.
  **Kesiapan desa dihitung dari profil bisnis pengelola** (`businessProfileId`),
  bukan input manual — lihat `app/services/readiness.py`.
- **Manfaat:** Angka kesiapan konsisten dengan data profil; pendampingan desa
  tepat sasaran; transparansi rantai pasok desa.

### Detail desa (di dalam `/villages` & `/villages/{id}/`)
- **Fitur:** daftar produk terkait (`villageId`), koordinat untuk peta.
- **Terhubung ke:** `getVillage` mengembalikan `products` desa.
- **Manfaat:** Menghubungkan desa ↔ produk ↔ peluang pasar.

---

## Export Analysis (Analisis Pasar & Kepatuhan)

### `/export-analysis`
- **Peran:** Exporter
- **Guna:** Intelijen kesiapan produk per negara tujuan.
- **Fitur:** daftar analisis, filter status, cari, paginasi, tautan
  **deep-link** (`?country=` & `?product=` untuk menyorot analisis target),
  ekspor PDF per analisis.
- **Terhubung ke:** `$lib/api/export-analysis.ts` → `GET /export-analysis/`.
- **Manfaat:** Pilih pasar berbasis kepatuhan & permintaan, bukan asumsi.

### `/export-analysis/create`
- **Peran:** Exporter, KepalaDesa
- **Guna:** Memulai analisis pasar/kepatuhan untuk produk → negara.
- **Fitur:** pilih produk (mendukung deep-link id **atau nama** produk) & negara;
  validasi; buat analisis.
- **Terhubung ke:** `createExportAnalysis` → `POST /export-analysis/`.
- **Manfaat:** Menjawab "produk ini boleh/layak ke negara mana?".

### `/export-analysis/[id]`
- **Peran:** Exporter
- **Guna:** Hasil analisis lengkap + tindakan.
- **Fitur:** skor & grade, isu kepatuhan, unduh PDF, **jalankan ulang**
  (`reanalyze`), **Regulation Check** (menghasilkan rekomendasi 10 bagian),
  hapus; tautan menyunting produk.
- **Terhubung ke:** `getExportAnalysis`, `reanalyzeExportAnalysis`,
  `runRegulationCheck`, `deleteExportAnalysis`, `analysisPdfUrl`.
- **Manfaat:** Dasar keputusan ekspor dengan jejak sumber.

### `/export-analysis/compare`
- **Peran:** Exporter
- **Guna:** Membandingkan beberapa negara tujuan untuk satu produk (decision support).
- **Fitur:** skor per negara, isu kritis, rekomendasi; **unduh PDF perbandingan**.
- **Terhubung ke:** `compareExportAnalyses` (`POST /export-analysis/compare/`),
  `downloadComparePdf` (`/compare/pdf/`).
- **Manfaat:** Memilih pasar terbaik secara objektif.

### `/export-analysis/[id]/regulation-recommendations`
- **Peran:** Exporter
- **Guna:** Panduan regulasi 10 bagian untuk produk→negara.
- **Fitur:** bagian (overview, larangan, sertifikasi, labeling, bea cukai, uji lab,
  IP, pengiriman, biaya) dengan penanda `generatedBy` (ai/template) & daftar sumber.
- **Terhubung ke:** `getRegulationRecommendations` →
  `/export-analysis/{id}/regulation-recommendations/` (memakai
  `app/data/trade_reference.py`, provenance `research_only`).
- **Manfaat:** panduan bertindak yang bersumber; AI advisory, bukan nasihat final.

---

## Markets (Intelijen Pasar)

### `/markets` dan `/markets/[id]`
- **Peran:** Exporter
- **Guna:** Memilih & memantau negara pasar utama.
- **Fitur:** skor pasar, kompleksitas kepatuhan, kelayakan logistik, estimasi margin,
  pertumbuhan, tarif; **refresh** untuk skor/insight terbaru; buat market.
- **Terhubung ke:** `$lib/api/markets.ts` → `GET/POST/PATCH/DELETE /markets/`,
  `POST /markets/{id}/refresh/`. Field turunan diisi backend agar kartu UI tidak kosong.
- **Manfaat:** Fokus pasar berbasis data; memantau perubahan tarif/insight.

---

## Countries & HS Codes (Referensi Publik)

### `/countries` dan `/countries/[code]`
- **Peran:** semua (ALWAYS_ALLOWED)
- **Guna:** Regulasi ekspor-impor per negara.
- **Fitur:** daftar negara + tingkat risiko; detail berisi sistem kepabeanan,
  tarif, aturan impor/ekspor, dokumen, otoritas, dan **regulasi terkurasi**
  (dengan `source`, `source_url`, `snapshot_date`, `review_status`).
- **Terhubung ke:** `GET /countries/`, `GET /countries/{code}/`
  (dari `app/data/regulatory_intel.py`, `app/data/countries.py`,
  dan `app/data/trade_reference.py`).
- **Manfaat:** Cek syarat tujuan sebelum transaksi; transparan soal status data.

### `/hs-codes` dan `/hs-codes/[code]`
- **Peran:** semua (ALWAYS_ALLOWED)
- **Guna:** Menelusuri nomenklatur HS.
- **Fitur:** pencarian kode/deskripsi, autocomplete, detail (kode, deskripsi,
  bagian, anak/children).
- **Terhubung ke:** `$lib/api/hs-codes.ts` → `GET /hs-codes/`,
  `/hs-codes/autocomplete/`, `/hs-codes/{code}/`.
- **Manfaat:** Klasifikasi barang akurat → tarif & lartas yang benar.

### `/reference`
- **Peran:** semua (ALWAYS_ALLOWED)
- **Guna:** Referensi regulasi faktual bertanggal (snapshot riset).
- **Fitur:** timeline kebijakan penting, fakta HS 2028, daftar FTA/CEPA dengan status,
  penanda sumber & `review_status`; read-only.
- **Terhubung ke:** `$lib/api/reference.ts` → `GET /reference/`
  (dari `app/data/trade_reference.py` + `regulatory_intel.py`).
- **Manfaat:** Rujukan cepat yang dapat ditelusuri; mencegah "halu" informasi.

---

## Catalogs (Katalog Jual)

### `/catalogs`
- **Peran:** Exporter, Buyer, Forwarder
- **Guna:** Katalog menghadap-buyer dari produk ekspor.
- **Fitur:** daftar katalog, status (Draft/Published/Needs Review), pencarian,
  paginasi, tautan buat/edit/detail, publikasi.
- **Terhubung ke:** `$lib/api/catalogs.ts` → `GET /catalogs/`.
- **Manfaat:** Materi jual siap kirim ke buyer; menaut produk ↔ pasar.

### `/catalogs/create` dan `/catalogs/[id]/edit`
- **Peran:** Exporter
- **Guna:** Membuat/menyunting katalog.
- **Fitur:** produk, project, judul, target market, MOQ, lead time, rentang harga,
  deskripsi, highlight, spesifikasi, tag.
- **Terhubung ke:** `createCatalog`/`updateCatalog`.
- **Manfaat:** Menyusun penawaran rapi & konsisten.

### `/catalogs/[id]`
- **Peran:** Exporter
- **Guna:** Mengelola detail katalog: gambar, varian, AI, harga & intelijen.
- **Fitur:**
  - **Gambar katalog** (unggah/ubah alt/hapus, harga & sort).
  - **Varian** (tipe & opsi: tambah/ubah/hapus).
  - **Deskripsi AI** (`generateCatalogAiDescription`) + deskripsi manual.
  - **Pricing** & **Market Intelligence** per katalog.
  - Publikasi/unpublikasi (mengunci kesiapan ≥95 saat terbit).
- **Terhubung ke:** `catalogs.ts` (images, variants, AI, pricing, publish),
  `marketing` (MI & pricing).
- **Manfaat:** Katalog kaya & konsisten; data harga/margin tersimpan.

### `/catalogs/public` dan `/catalogs/public/[id]`
- **Peran:** semua (ALWAYS_ALLOWED)
- **Guna:** Katalog publik (etalase) untuk dilihat tanpa login.
- **Fitur:** penelusuran katalog terbit, filter pencarian & tag, detail katalog.
- **Terhubung ke:** `listPublicCatalogs`, `getPublicCatalog`.
- **Manfaat:** Kanal akuisisi buyer; promosi produk desa.

### `/forwarders/catalogs`
- **Peran:** Forwarder
- **Guna:** Inventaris katalog/kuotasi freight yang relevan bagi forwarder.
- **Terhubung ke:** `listForwarderCatalogs`.
- **Manfaat:** Forwarder melihat permintaan yang bisa dilayani.
