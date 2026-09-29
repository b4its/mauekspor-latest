# 03 — Fulfillment

Kelompok menu **Fulfillment**: memastikan produk lolos syarat (compliance),
pekerjaan terkelola (tasks), dokumen lengkap (documents), dan barang sampai
(shipments). Ini jembatan dari kesepakatan komersial ke pengiriman nyata.

---

## Compliance (Kesiapan Berbasis Bukti)

### `/compliance`
- **Peran:** Exporter, CustomsBroker, KepalaDesa
- **Guna:** Daftar syarat kepatuhan ekspor dengan bukti yang dapat diaudit.
- **Fitur:**
  - Filter status (`Blocked/In Review/Evidence Uploaded/Verified`), cari,
    **sort kolom** (keparahan, tenggat, judul, kategori, status), paginasi,
    filter tersimpan di URL.
  - Buat requirement (judul, kategori, keparahan, owner, sumber, bukti wajib,
    project).
  - Hapus terpusat; tanggal diformat; nilai enum diterjemahkan.
  - **Gate bukti server-side:** `PATCH` tidak bisa men-set `Verified` tanpa
    `evidenceFileId` (422) — tombol dari halaman daftar mengarahkan ke detail
    untuk mengunggah bukti lebih dulu.
- **Terhubung ke:** `$lib/api/compliance.ts` → `/compliance/requirements/`.
  Requirement ditaut ke proyek/produk; sinyal keparahan muncul di dashboard & sidebar.
- **Manfaat:** Mencegah barang ditahan saat pengapalan; **"Verified" hanya sah
  bila ada bukti berkas** (klaim tanpa bukti ditolak), sehingga kesiapan terukur
  dan dapat diaudit.

### `/compliance/[id]`
- **Peran:** Exporter, CustomsBroker, KepalaDesa
- **Guna:** Detail satu requirement + unggah bukti.
- **Fitur:** unggah bukti (`POST .../evidence/`, termasuk `fileId` untuk unduhan),
  ubah/hapus.
- **Terhubung ke:** `getComplianceRequirement`, `uploadComplianceEvidence`,
  `updateComplianceRequirement`, `deleteComplianceRequirement`.
- **Manfaat:** Bukti tersimpan → lolos audit buyer/bea cukai.

---

## Tasks (Antrean Kerja Operasional)

### `/tasks` dan `/tasks/[id]`
- **Peran:** Exporter (dan peran operasional)
- **Guna:** Antrean tugas operasional ekspor.
- **Fitur:** daftar + prioritas & status, buat tugas, **selesaikan**, **tugaskan**
  ke anggota, ubah, hapus/batch, ekspor CSV; detail tugas.
- **Terhubung ke:** `$lib/api/tasks.ts` → `/tasks/`, `POST /tasks/{id}/complete/`,
  `POST /tasks/{id}/assign/`. Tugas sering dibuat otomatis oleh automations
  (mis. saat compliance terblokir).
- **Manfaat:** Tidak ada langkah terlewat; tanggung jawab jelas.

---

## Documents (Pusat Dokumen Dagang)

### `/documents` dan `/documents/[id]`
- **Peran:** Exporter, Forwarder, CustomsBroker, KepalaDesa
- **Guna:** Pusat dokumen ekspor (invoice, packing list, COO, PEB, dll.).
- **Fitur:**
  - Katalog **tipe dokumen** + dokumen wajib sesuai konteks (`commodityGroup`,
    `incoterm`).
  - Buat dokumen, **generate** dokumen dari template, **setujui** (approve),
    validasi field & kecocokan (mis. HS cocok produk), unduh **PDF**, hapus/batch.
- **Terhubung ke:** `$lib/api/documents.ts` → `/documents/`,
  `POST /documents/generate/`, `POST /documents/{id}/approve/`,
  `documentPdfUrl`. Tipe dokumen dari `app/services/document_types.py`.
- **Manfaat:** Dokumen standar siap; mengurangi penolakan kepabeanan.

---

## Shipments (Pelacakan Pengiriman)

### `/shipments` dan `/shipments/[id]`
- **Peran:** Exporter, Forwarder, CustomsBroker
- **Guna:** Melacak milestone logistik pengiriman ekspor.
- **Fitur:**
  - Daftar + filter status (`Booking Requested/Customs Submitted/Loaded/Exception`),
    sort (progres, ETA, forwarder, moda, status), cari, paginasi, seleksi massal.
  - Buat shipment (forwarder, rute, moda, ETA, project, order).
  - **Perbarui milestone**, **selesaikan exception**, ubah, hapus/batch, ekspor CSV.
  - Detail: progres %, container, booking no, milestol, tautan ke proyek/dokumen.
- **Terhubung ke:** `$lib/api/shipments.ts` → `/shipments/`,
  `POST /shipments/{id}/milestones/`, `POST /shipments/{id}/exceptions/resolve/`.
- **Manfaat:** Visibilitas rantai pasok; penanganan gangguan lebih cepat.

---

## Alur fulfillment (ringkas)

```
Order dikonfirmasi
   │
   ├─ Compliance: penuhi syarat + unggah bukti (blokir → tugas otomatis)
   ├─ Documents : generate & approve invoice/packing list/COO/PEB
   └─ Shipments : booking → milestone → resolved exception → sampai
```
- **Manfaat rantai:** Setiap langkah berbukti dan tertaut, sehingga eksportir
  tahu persis apa yang menghambat dan apa tindakan berikutnya.
