# 02 — Commercial

Kelompok menu **Commercial**: menghubungkan permintaan buyer ↔ pasokan
eksportir ↔ mitra logistik, lalu mengelola penawaran, biaya, order, dan
pembayaran. Ini "mesin penjualan" platform.

---

## Buyers (CRM Buyer)

### `/buyers`
- **Peran:** Exporter
- **Guna:** CRM buyer ekspor (calon pembeli luar negeri).
- **Fitur:** daftar buyer + status (Negotiating/At Risk/Confirmed), **fit score**,
  nilai tahunan estimasi, tandai **qualified**, catat kontak, cari/filter, hapus.
- **Terhubung ke:** `$lib/api/buyers.ts` → `GET/POST/PATCH/DELETE /buyers/`,
  `POST /buyers/{id}/qualify/`, `POST /buyers/{id}/contacts/`.
- **Manfaat:** Pipeline pembeli terkelola; prioritas follow-up berbasis skor.

### `/buyers/[id]`
- **Peran:** Exporter
- **Guna:** Detail buyer: kontak, minat produk, proyek terkait, sinyal, catatan.
- **Terhubung ke:** `getBuyer`, `updateBuyer`, `logBuyerContact`.
- **Manfaat:** Konteks lengkap sebelum negosiasi.

### `/buyers/portal`
- **Peran:** Buyer (dan Exporter untuk pratinjau)
- **Guna:** Portal buyer — barang ekspor dikurasi per negara buyer.
- **Fitur:** jelajah katalog/pasokan sesuai negara; akses RFQ/permintaan.
- **Terhubung ke:** `listPublicCatalogs`, buyer profiles, buyer-requests.
- **Manfaat:** Buyer menemukan supplier Indonesia yang relevan; mempercepat matching.

### `/buyers/profile` dan `/buyers/my-profile`
- **Peran:** Buyer
- **Guna:** Identitas importer (buyer) milik pengguna.
- **Fitur:** buat/sunting profil buyer (perusahaan, kategori diminati, asal negara,
  tipe bisnis, volume impor tahunan).
- **Terhubung ke:** `getMyBuyerProfile`, `createBuyerProfile`, `updateBuyerProfile`
  (`/buyers/profile/`).
- **Manfaat:** Personalisasi pasokan & matching; data kontak untuk eksportir.

---

## Buyer Requests (Permintaan Masuk)

### `/buyer-requests`
- **Peran:** Exporter, Buyer
- **Guna:** Menangkap permintaan masuk (inbound demand) dari buyer.
- **Fitur:** daftar permintaan, status, cari/filter, paginasi; akses matching.
- **Terhubung ke:** `$lib/api/buyer-requests.ts` → `GET /buyer-requests/`.
- **Manfaat:** Menampung demand sebelum jadi RFQ/quotation.

### `/buyer-requests/create`
- **Peran:** Buyer (dan Exporter mencatat dari pihak buyer)
- **Guna:** Mencatat permintaan baru.
- **Fitur:** subjek, tujuan, kuantitas, deadline, requirement, kategori produk,
  target HS code, spesifikasi, tag kata kunci, target volume, `min_rank_required`.
- **Terhubung ke:** `createBuyerRequest` → `POST /buyer-requests/`.
- **Manfaat:** Data permintaan terstruktur → matching otomatis lebih akurat.

### `/buyer-requests/[id]` dan `/buyer-requests/[id]/edit`
- **Peran:** Exporter, Buyer
- **Guna:** Detail & penyuntingan permintaan; melihat hasil matching.
- **Fitur/terhubung ke:** `getBuyerRequest`, **`matchBuyerRequest`**
  (`POST /buyer-requests/{id}/match/`), `getMatchedCatalogs`, `getMatchedUmkm`,
  update status, edit.
- **Manfaat:** Menaut permintaan buyer ke katalog/UMKM yang cocok → peluang transaksi.

---

## Suppliers (Jaringan Pemasok)

### `/suppliers` dan `/suppliers/[id]`
- **Peran:** Exporter
- **Guna:** Jaringan pemasok/unit pengolahan hasil desa.
- **Fitur:** daftar + skor kapabilitas/kualitas/kepatuhan, status, **verifikasi
  pemasok**, **minta bukti**, buat/ubah/hapus, detail dengan produk terkait.
- **Terhubung ke:** `$lib/api/suppliers.ts` → `/suppliers/`,
  `POST /suppliers/{id}/verify/`, `POST /suppliers/{id}/request-evidence/`.
- **Manfaat:** Jaminan pasokan & mutu; dasar klaim ke buyer.

---

## Forwarders (Mitra Logistik)

### `/forwarders` dan `/forwarders/[id]`
- **Peran:** Exporter, Forwarder
- **Guna:** Jaringan mitra freight + minta & bandingkan kuotasi.
- **Fitur:** daftar forwarder + rating, on-time rate; **minta kuotasi**,
  daftar kuotasi freight, rekomendasi forwarder per negara tujuan, ulasan.
- **Terhubung ke:** `$lib/api/forwarders.ts` → `/forwarders/`,
  `requestForwarderQuote`, `listForwarderQuotes`, `getForwarderRecommendations`,
  `createForwarderReview`.
- **Manfaat:** Logistik kompetitif; biaya & keandalan terbaca.

### `/forwarders/profile`, `/forwarders/my-profile`
- **Peran:** Forwarder
- **Guna:** Identitas mitra freight milik pengguna.
- **Fitur:** buat/sunting profil (rute spesialisasi, jenis layanan, kontak),
  *statistik* performa.
- **Terhubung ke:** `createForwarderProfile`, `getMyForwarderProfile`,
  `getMyForwarderStatistics`, `updateForwarderProfile`.
- **Manfaat:** Profil publik forwarder; daya tarik bagi eksportir.

---

## RFQ (Request for Quotation)

### `/rfq` dan `/rfq/[id]`
- **Peran:** Exporter, Buyer
- **Guna:** Ruang kerja permintaan penawaran (demand buyer).
- **Fitur:** daftar RFQ + match score & daftar kandidat; buat RFQ; **shortlist
  kandidat** (mengisi `catalog` & memperbarui `matchScore`); update status; hapus;
  detail dengan kandidat pemasok.
- **Terhubung ke:** `$lib/api/rfq.ts` → `/rfqs/`, `POST /rfqs/{id}/shortlist/`.
- **Manfaat:** Menemukan supplier tepat; menghubungkan demand → quotation.

---

## Quotations (Penawaran)

### `/quotations` dan `/quotations/[id]`
- **Peran:** Exporter, Finance, Buyer
- **Guna:** Mengelola penawaran komersial (RFQ → harga).
- **Fitur:** daftar + filter status, buat quotation, **terima** (`accept`),
  **konversi ke order** (`to-order`, idempoten), update, hapus/batch delete,
  ekspor CSV; detail dengan baris biaya & margin.
- **Terhubung ke:** `$lib/api/quotations.ts` → `/quotations/`,
  `POST /quotations/{id}/accept/`, `POST /quotations/{id}/to-order/`.
  `to-order` menaut ke Orders.
- **Manfaat:** Alur penawaran formal; konversi satu-klik tanpa entri ganda.

---

## Costing (Kalkulasi Biaya & Harga)

### `/costing` dan `/costing/[id]`
- **Peran:** Exporter, Finance
- **Guna:** Simulasi harga per incoterm + landed cost (EXW/FOB/CIF/…).
- **Fitur:** daftar skenario, filter/sort/cari; **recalculate**, **compare**
  beberapa skenario berdampingan, unduh PDF, hapus (terpusat); set/lihat
  **kurs** (`getExchangeRate`, `updateExchangeRate`).
- **Terhubung ke:** `$lib/api/costing.ts` → `/costing/`,
  `POST /costing/{id}/recalculate/`, `POST /costing/compare/`,
  `GET/PUT /settings/exchange-rate/`.
- **Manfaat:** Harga akurat per skema pengiriman; margin terproteksi dari
  fluktuasi kurs.

### `/costing/create` dan `/costing/[id]/edit`
- **Peran:** Exporter, Finance
- **Guna:** Membuat/menyunting skenario biaya.
- **Fitur:** produk, project, incoterm, margin, tujuan, HPP/unit, biaya packing,
  jarak (untuk estimasi freight), kurs.
- **Terhubung ke:** `createCostingScenario`, `updateCostingScenario`.
- **Manfaat:** Dasar harga quotation/order yang konsisten.

---

## Orders (Pesanan)

### `/orders` dan `/orders/[id]`
- **Peran:** Exporter, Finance, Buyer
- **Guna:** Mengeksekusi pesanan dari quotation yang diterima.
- **Fitur:** daftar + skor kesiapan order (dihitung bentuknya), nilai, incoterm,
  pembayaran, jendela pengiriman; **konfirmasi** order, update (tahap dokumen),
  hapus/batch; detail dengan baris & checklist, tautan ke dokumen/shipment.
- **Terhubung ke:** `$lib/api/orders.ts` → `/orders/`, `POST /orders/{id}/confirm/`.
  Order dapat dibuat via `createOrder` atau `convertQuotationToOrder`.
- **Manfaat:** Eksekusi terstruktur; dasar dokumen & pengiriman.

---

## Payments (Pembayaran & Piutang)

### `/payments` dan `/payments/[id]`
- **Peran:** Exporter, Finance, CustomsBroker
- **Guna:** Memantau piutang ekspor & penyelesaiannya.
- **Fitur:** daftar + status (Deposit/Fully Paid/Due), jumlah terbayar vs total,
  risiko; **tandai diterima** (`mark-received`), **kirim pengingat** (`send-reminder`),
  buat/ubah/hapus/batch; detail dengan milestone & tautan ke order.
- **Terhubung ke:** `$lib/api/payments.ts` → `/payments/`,
  `POST /payments/{id}/mark-received/`, `POST /payments/{id}/send-reminder/`.
- **Manfaat:** Arus kas ekspor terkendali; penagihan tepat waktu.

---

## Alur komersial (ringkas)

```
Buyer Request ─▶ RFQ ─▶ Quotation ─▶(accept)─▶ Order ─▶ Payment
                     ▲            Costing menentukan harga/incoterm
   Buyers (CRM) ─────┘   Suppliers & Forwarders memasok & mengangkut
```
- **Manfaat rantai:** Demand tertangkap → penawaran berbiaya jelas → order →
  pembayaran, semuanya tertaut sehingga jejak transaksi utuh dan dapat diaudit.
