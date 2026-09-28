# PRD — MauEkspor: Platform Ekspor Komoditas Desa

> Product Requirements Document (PRD) + Rencana Implementasi
> Versi: 1.0 · Status: Baseline / untuk dieksekusi bertahap
> Lokasi: `guideline/plana/`

---

## 0. Ringkasan Eksekutif

**MauEkspor** adalah workspace ekspor berbasis AI untuk komoditas desa Indonesia (kopi, kakao, rempah, rotan, HHNK, buah). Produk saat ini **berfungsi penuh sebagai demo/pilot satu organisasi**: ~51 grup rute frontend, ~240 endpoint backend, 475 test backend + 348 test frontend hijau, seeding 100+ record per tabel, dan modul end-to-end dari kesiapan produk sampai pengiriman.

Namun audit menyeluruh (backend, frontend, operasi/CI) menemukan bahwa fondasi masih **prototype-grade**: penyimpanan JSON blob in-memory, tanpa isolasi tenant, otorisasi berbasis path string, dan sejumlah risiko keamanan. Sebagian sudah diperbaiki pada iterasi terakhir (lihat §7). PRD ini menetapkan **apa yang harus dibangun** agar MauEkspor naik dari *demo* menjadi **pilot internal yang aman** lalu **SaaS multi-tenant** yang layak produksi, dengan alur ekspor yang benar-benar governed dan tervalidasi regulasi.

**Prinsip panduan (non-negotiable):**
1. **Keamanan & integritas data sebelum fitur.** Tidak ada fitur baru yang menambah permukaan risiko tanpa kontrol setara.
2. **Alur ekspor adalah state machine, bukan kumpulan modul lepas.**
3. **Rekomendasi regulasi wajib punya provenance** (sumber, tanggal berlaku, yurisdiksi, status review manusia). AI bersifat *advisory*, tidak menggantikan temuan deterministik.
4. **Truth in UI:** kegagalan API tidak boleh tampak seperti data bisnis valid.
5. **Atomic, testable, reversible** perubahan.

---

## 1. Latar Belakang & Masalah

### 1.1 Pengguna & peran
- **KepalaDesa / Kepala BUMDes** — menu sederhana: komoditas, kepatuhan, dokumen.
- **Eksportir Desa / UMKM (BUMDes, Kelompok Tani)** — pemilik alur utama (produk → analisis → costing → katalog → RFQ → quotation → order → dokumen → pengiriman → pembayaran).
- **Buyer** — importir global; portal katalog & permintaan.
- **Forwarder** — logistik; profil, quote, tracking.
- **CustomsBroker** — dokumen & kepatuhan kepabeanan.
- **Finance** — pembayaran, billing, costing.
- **Admin** — operasi sistem, master data, audit.

### 1.2 Masalah nyata di lapangan (yang MauEkspor selesaikan)
1. Data produk/HS tersebar di Excel; klasifikasi HS salah → risiko tarif & penolakan.
2. Persyaratan regulasi negara tujuan (label, sertifikat, karantina) tidak diketahui di muka → barang tertahan.
3. Harga ekspor (EXW/FOB/CIF) dihitung manual → margin bocor.
4. Komunikasi buyer tersebar (WhatsApp/email) → kehilangan jejak penawaran.
5. Dokumen ekspor tidak tervalidasi → eskalasi biaya pelabuhan.

### 1.3 Kondisi sistem saat ini (aset vs utang)
| Aspek | Status | Catatan |
|---|---|---|
| Cakupan fitur | **Kuat (demo)** | Hampir semua modul ekspor ada. |
| Testing | **Kuat** | 475 backend + 348 frontend + contract test. |
| Penyimpanan | **Utang berat** | JSON blob, in-memory read cache, tanpa FK/index/transaksi. |
| Multi-tenant | **Tidak ada** | Satu workspace global. |
| Otorisasi | **Parsial** | RBAC tingkat modul; tanpa kepemilikan record. |
| AI tata kelola | **Lemah** | Fallback mock menyamar sebagai analisis; tanpa provenance. |
| Operasi/CI/CD | **Lemah** | Banyak docker-compose kontradiktif, tanpa TLS/backup/monitoring. |
| Dokumentasi hukum | **Berisiko** | Klaim regulasi tanpa sitasi/tanggal berlaku. |

---

## 2. Tujuan & Metrik Keberhasilan

### 2.1 Tujuan produk
- **G1** Eksportir desa dapat menyiapkan satu pengiriman ekspor lengkap dan tervalidasi dalam satu workspace.
- **G2** Setiap rekomendasi regulasi dapat ditelusuri ke sumber resmi + tanggal berlaku.
- **G3** Biaya ekspor (EXW/FOB/CIF/DAP) akurat, dapat diaudit, dan konsisten mata uang.
- **G4** Buyer/forwarder/dinas dapat berkolaborasi pada objek yang sama dengan peran jelas.

### 2.2 Tujuan teknis
- **T1** Isolasi tenant pada semua entitas bisnis.
- **T2** Otorisasi berbasis kebijakan eksplisit (bukan inferensi path string).
- **T3** Integritas transaksional untuk alur multi-record.
- **T4** Observability & operasi produksi (log/metrics/trace/backup/CI).

### 2.3 Metrik (North Star & pendukung)
| Metrik | Baseline | Target 2 kuartal |
|---|---|---|
| Waktu menyiapkan 1 kasus ekspor siap kirim | manual/berhari-hari | < 1 hari kerja |
| % analisis dengan seluruh rekomendasi bersumber & tanggal berlaku | 0% | ≥ 95% |
| Insiden kebocoran lintas-tenant | tak terukur | 0 |
| Test otomatis yang gagal di CI untuk perubahan berisiko | sebagian | 100% gate |
| p95 latensi daftar (≤ 5k record/tenant) | tak terukur | < 400 ms |

---

## 3. Ruang Lingkup

**Termasuk:** penyempurnaan arsitektur, keamanan, alur ekspor governed, tata kelola AI/regulasi, kualitas data master, operasi & CI, dokumentasi.

**Tidak termasuk (v1):** integrasi langsung ke CEISA/INSW produksi, gateway pembayaran live, e-signature legal, pengiriman email/SMS produksi (dirancang sebagai *adapter* yang dapat dinyalakan).

---

## 4. Persona & Journey (end-to-end)

### 4.1 Journey utama ekspor (target state)
1. **Identitas usaha** — profil, legalitas (NIB/NPWP), sertifikasi.
2. **Master produk** — spesifikasi, kemasan, berat, asal.
3. **HS enrichment + konfirmasi manusia** — AI usul, manusia menetapkan.
4. **Analisis pasar & kepatuhan** — skor, isu, dokumen wajib per negara.
5. **Remediasi** — unggah bukti, tutup isu kritis.
6. **Costing** — EXW/FOB/CIF, margin, kurs bertanggal.
7. **Katalog buyer-facing** — konten, varian, publikasi.
8. **RFQ / permintaan buyer** — matching.
9. **Quotation** — berbasis costing, tervalidasi internal.
10. **Order** — dari quotation diterima; terms terkunci.
11. **Dokumen** — invoice, packing list, COO, sertifikat; versi & approval.
12. **Pembayaran** — termin, jatuh tempo, rekonsiliasi.
13. **Pengiriman & kepabeanan** — booking, PEB, tracking sampai tiba.
14. **Penutupan & dossier ekspor** — paket lengkap + checksum.

Setiap tahap punya **gate**, **pemilik**, **blocker**, **timestamp**, dan **next action**.

### 4.2 Journey pendukung
- Buyer: telusuri katalog publik → kirim permintaan → terima quotation.
- Forwarder: terima permintaan quote → kirim penawaran → booking.
- KepalaDesa: lihat komoditas desa → cek kepatuhan → cetak dokumen ringkas.
- Admin: master data (negara/regulasi/HS), audit, kesehatan sistem.

---

## 5. Kebutuhan Fungsional

Penomoran: `FR-<area>-<n>` dengan prioritas **P0** (blocker), **P1** (tinggi), **P2** (sedang).

### 5.1 Autentikasi & Akun (`AUTH`)
- **FR-AUTH-1 (P0)** Sesi: pilih satu model tepercaya. Rekomendasi: access token jangka pendek di memori + refresh token rotasi di cookie `HttpOnly; Secure; SameSite`, dengan proteksi CSRF wajib saat cookie aktif. Sertakan CSP ketat.
- **FR-AUTH-2 (P0)** Nonaktifkan/aktifkan akun; tolak akses dari akun nonaktif di semua jalur.
- **FR-AUTH-3 (P1)** Rotasi & revokasi refresh token (hash di DB), deteksi reuse.
- **FR-AUTH-4 (P1)** Invitasi tim yang benar-benar dapat diterima: buat token kedaluwarsa, endpoint accept, tautkan user, konsumsi token.
- **FR-AUTH-5 (P1)** API key nyata: generate secret, simpan hash + prefix, tegakkan scope, perbarui `lastUsed`.
- **FR-AUTH-6 (P2)** Kebijakan password & MFA opsional (TOTP).

### 5.2 Tenant & Kepemilikan (`TENANT`)
- **FR-TENANT-1 (P0)** Model organisasi/workspace + keanggotaan + peran; `tenant_id` pada semua entitas bisnis.
- **FR-TENANT-2 (P0)** Semua query/mutasi ter-scope tenant; validasi kepemilikan parent–child saat menautkan record.
- **FR-TENANT-3 (P0)** Master data global (negara/HS/regulasi) dipisah dari data tenant.
- **FR-TENANT-4 (P1)** Berbagi selektif (mis. buyer melihat katalog perusahaan tertentu) via ACL eksplisit.
- **FR-TENANT-5 (P1)** Ekspor/impor data per tenant (portabilitas + hak subjek data).

### 5.3 Produk & Klasifikasi HS (`PROD`)
- **FR-PROD-1 (P0)** Skema produk tervalidasi (tipe, satuan, berat > 0, kemasan terenumerasi).
- **FR-PROD-2 (P0)** HS code: usul AI + **konfirmasi manusia**; simpan sumber & keyakinan.
- **FR-PROD-3 (P1)** Master HS buatan admin **masuk** ke pipeline pencarian/enrichment (bukan hanya tabel terpisah).
- **FR-PROD-4 (P1)** Lot/batch & ketertelusuran (farm-gate → kontainer).
- **FR-PROD-5 (P2)** Normalisasi satuan (kg/ton/dus) & kemasan berjenjang.

### 5.4 Analisis Pasar & Kepatuhan (`COMPL`)
- **FR-COMPL-1 (P0)** Analisis per (produk × negara), idempoten, dengan snapshot produk & regulasi berversi.
- **FR-COMPL-2 (P0)** Isu deterministik **tidak boleh ditimpa** AI; AI hanya *menambah/saran* yang ditandai.
- **FR-COMPL-3 (P0)** Setiap rekomendasi memiliki: sumber URL, penerbit, tanggal berlaku, yurisdiksi, produk yang berlaku, **status review** (Draft/Reviewed/Deprecated), penanggung jawab.
- **FR-COMPL-4 (P0)** Aturan buatan admin **menggerakkan** hasil analisis (bukan hanya halaman negara).
- **FR-COMPL-5 (P1)** Registry dokumen wajib per (negara × komoditas × incoterm) dengan dependensi.
- **FR-COMPL-6 (P1)** Deteksi kedaluwarsa sertifikat & pengingat perpanjangan.
- **FR-COMPL-7 (P1)** Skrining sanksi/denied-party dasar + peringatan.
- **FR-COMPL-8 (P2)** Mesin bea/tarif (asal × tujuan × HS × tanggal × FTA) sebagai perhitungan terstruktur.

### 5.5 Costing & Pricing (`COST`)
- **FR-COST-1 (P0)** Uang memakai tipe desimal (bukan float); setiap nilai uang menyimpan mata uang, unit, presisi, inklusivitas pajak.
- **FR-COST-2 (P0)** Kurs menyimpan pasangan mata uang + tanggal + sumber; harga historis immutable.
- **FR-COST-3 (P0)** EXW/FOB/CIF/DAP dengan rincian komponen yang dapat diaudit.
- **FR-COST-4 (P1)** Estimasi kapasitas kontainer & saran AI (ditandai advisory).
- **FR-COST-5 (P1)** Costing → quotation mewarisi angka nyata (bukan nilai hardcode).
- **FR-COST-6 (P2)** Simulasi skenario ganda & bandingkan.

### 5.6 Katalog (`CAT`)
- **FR-CAT-1 (P0)** Katalog & gambar/varian CRUD; unggah gagal harus **gagal keras** (tidak boleh klaim sukses palsu).
- **FR-CAT-2 (P1)** Publikasi ter-gate: deskripsi, harga, minimal 1 gambar, kepatuhan pra-syarat.
- **FR-CAT-3 (P1)** Deskripsi AI ditandai & dapat ditinjau; multibahasa.
- **FR-CAT-4 (P2)** Katalog publik: SEO, atribut terstruktur, tautan aman berbatas waktu.

### 5.7 Komersial: RFQ → Quotation → Order → Payment (`COMM`)
- **FR-COMM-1 (P0)** Quotation hanya dari costing terpilih; nilai/kuantitas/incoterm/kurs nyata (bukan `42800` hardcode).
- **FR-COMM-2 (P0)** State machine: `RFQ → Quotation(Draft→In Review→Sent→Accepted/Rejected) → Order(Draft→Confirmed→…)`; transisi divalidasi.
- **FR-COMM-3 (P0)** Konversi quotation→order **aman konkuren** (idempoten via kunci unik `quotationId`).
- **FR-COMM-4 (P0)** Order mewarisi terms (incoterm, pembayaran, jadwal) dari quotation; pembuatan shipment/payment dari template terms, bukan nilai hardcode.
- **FR-COMM-5 (P1)** Baris order/invoice immutable setelah confirm; revisi via versi baru.
- **FR-COMM-6 (P1)** Alokasi pembayaran & rekonsiliasi (parsial, kurs, selisih).
- **FR-COMM-7 (P2)** Flow response/negosiasi/akseptasi quote forwarder.

### 5.8 Dokumen & Kepatuhan Dokumen (`DOC`)
- **FR-DOC-1 (P0)** Dukungan nyata untuk tipe yang diklaim UI: invoice, packing list, COO, proforma, **plus** health/phytosanitary, insurance, B/L. (UI tidak boleh menjanjikan yang belum ada.)
- **FR-DOC-2 (P0)** Rendering PDF valid (teks terekstraksi, bukan kontainer kosong) via pustaka mapan + uji ekstraksi teks.
- **FR-DOC-3 (P1)** Versi dokumen, penerbit, hash, tanggal kedaluwarsa, pihak penandatangan.
- **FR-DOC-4 (P1)** Approval authority; dokumen tervalidasi sebelum rilis paket.
- **FR-DOC-5 (P2)** Generasi bilingual & watermark/redaksi untuk pihak eksternal.

### 5.9 Pengiriman & Kepabeanan (`SHIP`)
- **FR-SHIP-1 (P0)** Data pelabuhan, rute, vessel, booking, kontainer terstruktur.
- **FR-SHIP-2 (P0)** Milestone divalidasi (transisi status tidak boleh lompat sembarang).
- **FR-SHIP-3 (P1)** Titik integrasi deklarasi (PEB/e-Customs) sebagai adapter (mulai manual + validator).
- **FR-SHIP-4 (P1)** Kepemilikan & SLA pengecualian/insiden.

### 5.10 Alur & Dossier (`FLOW`)
- **FR-FLOW-1 (P0)** Objek "kasus ekspor" kanonik yang mengikat modul-modul, dengan stage machine + gate.
- **FR-FLOW-2 (P0)** Gate contoh: tidak bisa publish katalog tanpa deskripsi+harga+gambar; tidak bisa rilis paket dokumen tanpa isu kritis tertutup; tidak bisa booking tanpa dokumen wajib.
- **FR-FLOW-3 (P1)** Handoff antar peran dengan accept/reject & SLA.
- **FR-FLOW-4 (P1)** Timeline imutabel per kasus (siapa, apa, kapan).
- **FR-FLOW-5 (P1)** **Paket dossier** (ZIP) berisi invoice, packing list, COA, sertifikat, ringkasan kepatuhan, dokumen pengiriman + **manifest & checksum**.

### 5.11 Ekspor Data & Unduhan (`EXP`)
- **FR-EXP-1 (P0)** Semua unduhan terautentikasi (bearer/blob) — PDF analisis, costing, dokumen, file. Sudah sebagian; lengkapi.
- **FR-EXP-2 (P0)** Export menghormati **cakupan**: terpilih / hasil filter saat ini / halaman ini / seluruh yang diizinkan; scope tampak di nama berkas & manifest.
- **FR-EXP-3 (P1)** Unduhan punya status (busy/sukses/gagal), audit event, verifikasi MIME & non-kosong.
- **FR-EXP-4 (P1)** Job ekspor latar untuk dataset besar (progres, batal, retry, riwayat).
- **FR-EXP-5 (P2)** Pilih kolom, watermark, tautan berbagi berbatas waktu, retensi.

### 5.12 AI & Tata Kelola Regulasi (`AI`)
- **FR-AI-1 (P0)** Skema keluaran AI tervalidasi ketat (Pydantic); tolak yang menyimpang.
- **FR-AI-2 (P0)** Mode mock **tidak boleh** menyamar sebagai analisis produksi; tandai jelas & jangan dipakai untuk keputusan kepatuhan.
- **FR-AI-3 (P0)** Simpan provenance: provider, model, versi prompt, hash input, waktu, indikator fallback, status review manusia.
- **FR-AI-4 (P1)** Konteks workspace di-scope tenant & diredaksi sebelum dikirim ke penyedia eksternal.
- **FR-AI-5 (P1)** Kuota/biaya per tenant; timeout & circuit breaker; human-in-the-loop untuk regulasi.
- **FR-AI-6 (P1)** Kewajiban sitasi untuk nasihat regulasi + disclaimer hukum.

### 5.13 Kolaborasi, Notifikasi, Dukungan (`COLLAB`)
- **FR-COLLAB-1 (P0)** Notifikasi ter-scope pemilik (sudah untuk single + batch; jaga konsistensi).
- **FR-COLLAB-2 (P1)** Gateway pesan nyata (email/WhatsApp) di belakang adapter.
- **FR-COLLAB-3 (P2)** Dukungan tiket dengan SLA & eskalasi.

### 5.14 Admin & Master Data (`ADMIN`)
- **FR-ADMIN-1 (P0)** Penulisan master (HS/regulasi/negara) terhubung ke pipeline runtime.
- **FR-ADMIN-2 (P0)** Field sensitif (password) tidak bisa ditimpa via admin generik.
- **FR-ADMIN-3 (P1)** Audit imutabel: aktor (ID), tenant, request ID, IP, before/after, target.
- **FR-ADMIN-4 (P1)** Config ter-validasi skema (enum mode AI; tolak nilai tak dikenal).

### 5.15 Ekspor Framework (kebutuhan lintas-modul)
- **FR-X-1 (P0)** Rutekan pembuatan entitas dalam transaksi; ID unik (UUID/ULID atau DB-generated).
- **FR-X-2 (P0)** Tidak ada "create" yang berubah menjadi "update" diam-diam saat ID tabrakan.
- **FR-X-3 (P1)** Paginasi server-side, filter, sort, hitung total, pembatalan request.
- **FR-X-4 (P1)** Health check liveness/readiness (DB, storage, dependensi).

---

## 6. Kebutuhan Non-Fungsional

- **NFR-SEC-1** Threat model terdokumentasi; CSP; header keamanan; rahasia via secret manager.
- **NFR-SEC-2** Skrining dependency (SCA), SAST, secret scanning, image scanning di CI.
- **NFR-DATA-1** Integritas transaksional; foreign key; constraint unik/check; migrasi (Alembic).
- **NFR-DATA-2** Backup terenkripsi DB **dan** uploads; restore teruji; RPO/RTO ditetapkan.
- **NFR-PERF-1** p95 daftar < 400 ms pada 5k record/tenant; ekspor besar via job latar.
- **NFR-SCALE-1** Aman multi-worker/multi-instance (sumber kebenaran = PostgreSQL per request).
- **NFR-OBS-1** Log JSON terstruktur, metrik (latensi/error/rate-limit/AI), trace, alert.
- **NFR-A11Y-1** WCAG 2.1 AA pada jalur kritis; uji otomatis (axe) di CI.
- **NFR-I18N-1** ID/EN konsisten; kunci hilang terdeteksi di CI; `<html lang>` reaktif.
- **NFR-COMP-1** Kepatuhan data (UU PDP Indonesia): klasifikasi, retensi, hak subjek data, transfer lintas negara untuk AI.
- **NFR-LEGAL-1** Lisensi proyek, NOTICE, provenance dataset & binari pihak ketiga.

---

## 7. Status Baseline — yang SUDAH diperbaiki pada iterasi ini

Commit atomik yang sudah masuk (audit → perbaikan):

1. **`fix(security): enforce auth/role on generic exports and notification ownership`**
   - Endpoint export generik kini wajib login; izin per-tabel via `module_for_data_table()` + `can_read_module`.
   - Batch-delete notifikasi memakai `_owned_notification` (cegah hapus lintas-pemilik).
   - CSV escape formula injection (`= + - @`, kontrol).
2. **`fix(security): make demo seeding opt-in and fail-closed in production`**
   - `MAUEKSPOR_SEED_DEMO_DATA` (default true dev/demo); production menolak boot bila true.
3. **`fix(security): sanitize markdown rendering to prevent stored XSS`**
   - `escapeHtml` sebelum parse Markdown + `sanitizeGeneratedHtml` (buang `on*`, `javascript:`/`data:`, tag berbahaya); halaman artikel edukasi memakai `renderSafeInlineMarkdown`.
4. **`docs(env): document MAUEKSPOR_SEED_DEMO_DATA and de-fang production example`**
5. **`feat(prd): provenance, document types, and workflow gates (PRD Phase 3/4)`**
   - Provenance service (sumber, effective date, review status) + AI provenance yang
     selalu menandai *advisory* & fallback mock; blok `trust` per analisis + disclaimer.
   - Tipe dokumen terpusat (tambah Proforma, Phytosanitary, Health, Insurance, B/L);
     `GET /documents/types/`; `/documents/generate/` menolak tipe tak didukung (422).
   - Gate publikasi katalog (deskripsi + pasar + harga + 1 gambar).
   - State machine quotation→order (hanya Accepted/In-Review; warisi terms).
6. **`feat(prd): surface document types and analysis provenance in the UI`**
7. **`feat(prd): authenticated downloads and scoped exports (FR-EXP-1/2/3)`**
   - `downloadFile` mendukung POST/body + pesan error; `exportPath()` ber-scope;
     tombol export di 9 halaman mengikuti filter/pencarian/pilihan; tombol PDF di
     halaman dokumen/costing/analisis memakai unduhan terautentikasi.
8. **`feat(prd): admin HS codes feed the runtime search pipeline (FR-ADMIN-1)`**
9. **`fix(security): atomic create, CSRF fail-closed, and proxy trust default off`**
   - `db.create()` mengalokasikan id + menulis di satu lock dan menolak id
     duplikat (create tak pernah jadi update diam-diam); `replace()` mempertahankan
     metadata `__table`.
   - CSRF wajib untuk mutasi berbasis cookie di production (fail-closed); Bearer
     tidak terpengaruh.
   - `MAUEKSPOR_TRUST_PROXY` default OFF (anti-spoof X-Real-IP).
10. **`fix(ux): stop showing demo seed data as valid business data (FR-EXP/G-09)`**
    - Seed fallback hanya aktif di mode demo (`VITE_DEMO_DATA=1` / `?demo=1`);
      gagal API → daftar kosong + banner `DataStateBanner` (9 halaman list).
11. **`fix(security): validate uploads by magic bytes and use safe stored names`**
    (G-16) + koreksi URL unduh berkas edukasi.
12. **`fix(docs): emit valid, text-extractable PDFs (FR-DOC-2 / G-08)`**
13. **`feat(ops): add liveness/readiness probes with real dependency checks (FR-X-4)`**

Verifikasi terkini: backend 503 test hijau; frontend 344 test hijau; `svelte-check` 0 error; build produksi sukses.

Sisa temuan P0/P1 dari audit yang **belum** ditangani menjadi backlog di §8.

---

## 8. Gap Analysis & Prioritas (Backlog)

Tabel ringkas. Status: ✅ selesai · 🟡 sebagian · ❌ belum.

| ID | Temuan | Dampak | Prioritas | Status |
|---|---|---|---|---|
| G-01 | Export generik tanpa otorisasi | Kebocoran data sensitif | P0 | ✅ |
| G-02 | Batch-delete notifikasi lewat ownership | Integritas/kebocoran | P0 | ✅ |
| G-03 | Demo seed akun admin password tetap | Kompromi akun | P0 | ✅ |
| G-04 | Stored XSS (Markdown/edukasi) | Curi token | P0 | ✅ |
| G-05 | Tanpa isolasi tenant | Kebocoran lintas-org | P0 | ❌ |
| G-06 | ID non-atomik → overwrite | Kehilangan data | P0 | ✅ |
| G-07 | Unduhan PDF/file via `<a href>` | 401 / tidak dapat unduh | P0 | ✅ |
| G-08 | PDF kustom tak valid | Dokumen klaim gagal | P0 | ✅ |
| G-09 | Truth in UI: seed fallback | Keputusan salah | P1 | ✅ |
| G-10 | Export abaikan filter/scope | Data tak sesuai tinjauan | P1 | ✅ |
| G-11 | Nilai hardcode (42800, L/C, 30 hari) | Record komersial salah | P1 | 🟡 (order mewarisi terms; wizard shipment/payment belum) |
| G-12 | AI fallback menyamar | Nasihat kepatuhan keliru | P0/P1 | ✅ (ditandai advisory + fallback) |
| G-13 | Regulasi HS/admin tak terhubung runtime | Master data sia-sia | P1 | 🟡 (HS ✅; regulasi admin → analisis parsial) |
| G-14 | CSRF off + cookie auth | Risiko CSRF | P1 | ✅ (fail-closed di production) |
| G-15 | Trust proxy default | Bypass rate-limit | P1 | ✅ (default off) |
| G-16 | Upload extension-only, buffer penuh | Malware/DoS | P1 | 🟡 (magic bytes + nama acak ✅; streaming belum) |
| G-17 | Multi-worker tidak aman | Stale/duplikasi | P1 | ❌ |
| G-18 | Operasi: TLS/backup/monitoring/CI | Risiko produksi | P1 | ❌ |
| G-19 | Rahasia bocor (ngrok token di Makefile.backup) | Kompromi tunnel | P0 | ❌ |
| G-20 | Klaim regulasi tanpa sitasi | Risiko hukum | P0/P1 | ✅ (sumber+review status di analisis; sumber primer perlu diverifikasi) |
| G-21 | Tanpa alur/dossier kanonik | Nilai inti tak tercapai | P0 | ❌ |
| G-22 | i18n kunci hilang | UX campur bahasa | P2 | 🟡 |

---

## 9. Rencana Implementasi (Roadmap)

### Phase 0 — Kontainmen (segera, hari ini–minggu 1)
- ❌ Revoke/rotate kredensial ngrok di `Makefile.backup`; hapus berkas; pindai riwayat git; aktifkan secret scanning.
- Rotasi kunci AI lokal bila berisiko.
- Nonaktifkan workflow tunnel publik sampai Phase 1 mengunci akun demo & otorisasi.
- Tetapkan **satu** worker backend sampai persistensi direfaktor.
- Tandai semua output AI sebagai *advisory*; matikan fallback mock untuk kepatuhan.

**Exit criteria:** tidak ada rahasia di repo; tidak ada jalur publik tanpa auth; guard production aktif.

### Phase 1 — Keamanan & Integritas (minggu 2–6)
- Tenant: `organizations`, `memberships`, `tenant_id` pada entitas; scoping query/mutasi.
- Otorisasi berbasis kebijakan eksplisit per-route (ganti inferensi string).
- ID → UUID/ULID atau DB-generated; create non-overwrite.
- Hash refresh token; revokasi sesi; tolak akun nonaktif.
- Upload aman (streaming, magic-byte, nama UUID, kuota).
- CSRF wajib bila cookie; trust proxy off default.
- Formula-safe export (sudah) + audit export.

**Exit criteria:** matriks test lintas-tenant hijau; tidak ada IDOR/bulk-bypass; SCA/secret scan gate.

### Phase 2 — Persistensi & Refactor Layanan (minggu 4–10)
- Ganti in-memory source-of-truth dengan repository/ORM; migrasi Alembic; FK/unique/check.
- Pecah `routes.py` per domain; service layer + unit-of-work; optimistic locking.
- Uji integrasi PostgreSQL; ekspor & AI berat → job latar.
- Paginasi/filter/sort server-side.

**Exit criteria:** multi-worker aman; test integrasi DB hijau; latensi target tercapai.

### Phase 3 — Alur Ekspor Governed (minggu 8–16)
- Objek kasus ekspor + state machine + gate.
- Baris order/invoice immutable; uang Decimal + kurs bertanggal.
- Dokumen: versi, hash, penerbit, kedaluwarsa, approval; PDF valid.
- Flow quote forwarder → booking; alokasi pembayaran; sertifikat expiry.
- **Paket dossier** + manifest/checksum.

**Exit criteria:** satu kasus ekspor end-to-end lulus E2E; paket dokumen terverifikasi.

### Phase 4 — Tata Kelola AI & Regulasi (minggu 12–20)
- Skema AI ketat; provenance; sitasi wajib; redaksi konteks.
- Master HS/regulasi admin masuk pipeline runtime; effective date & status review.
- Human review & revalidasi; disclaimer di setiap keluaran.

**Exit criteria:** ≥ 95% analisis bersumber & bertanggal; tidak ada mock menyamar.

### Phase 5 — Operasi & Supply Chain (minggu 16–26)
- TLS + CSP + HSTS; hardening nginx; ingress hanya TLS.
- Structured logging, metrics, tracing, SLO, alert; liveness/readiness.
- Backup DB+uploads terenkripsi; restore drill; RPO/RTO.
- CI: pin aksi (SHA), lockfile frozen, SCA/SAST/image scan, SBOM, sign; staging+approval.
- Kontainer minimal & digest-pinned.

**Exit criteria:** drill restore sukses; alert aktif; rilis immutable tersigned.

### Phase 6 — Legal, Privasi, Artefak (paralel)
- LICENSE + NOTICE; provenance dataset (HS/world_countries/regulatory_intel) & binari.
- Kebijakan privasi (UU PDP), retensi, hak subjek data, transfer AI.
- Pindahkan korpus screenshot ke CI artifact/LFS; kebijakan artefak tergenerasi.

---

## 10. Risiko & Mitigasi

| Risiko | Dampak | Likelihood | Mitigasi |
|---|---|---|---|
| Refactor persistensi besar merusak kontrak | Tinggi | Sedang | Contract test + adopter bertahap + feature flag |
| Data regulasi salah/kedaluwarsa | Tinggi | Sedang | Provenance + review manusia + effective date + disclaimer |
| Migrasi tenant mengganggu data demo | Sedang | Tinggi | Seed dev terpisah; migrasi idempoten; backup sebelum migrasi |
| Biaya AI tak terkendali | Sedang | Sedang | Kuota per tenant; cache; circuit breaker |
| Scope creep alur ekspor | Sedang | Tinggi | Gate berbasis exit criteria per Phase |

---

## 11. Sumber & Validasi (provenance)

Bagian ini mencatat sumber **primer/tepercaya** untuk desain konten regulasi. **Penting:** banyak klaim di README saat ini belum tervalidasi dan sebagian terbukti salah (mis. URL yang diklaim "PP 28/2024 Karantina" mengarah ke peraturan daerah tentang SPBE, bukan regulasi karantina). Semua entri di bawah **wajib diverifikasi ulang ke dokumen resmi** dan disertai tanggal akses sebelum dipakai sebagai nasihat kepatuhan.

> Konvensi: setiap item regulasi di sistem disimpan sebagai `{title, publisher, source_url, retrieved_at, effective_from, effective_to, jurisdiction, applies_to, review_status, reviewer, notes}`.

### 11.1 Sumber resmi Indonesia (primer)
| Domain | Penerbit | Tautan resmi | Kegunaan |
|---|---|---|---|
| Peraturan (JDIH nasional) | BPK RI | https://peraturan.bpk.go.id/ | Teks resmi UU/PP/Perpres/Permen + metadata berlaku |
| Kepabeanan & ekspor | DJBC (Bea Cukai) | https://www.beacukai.go.id/ (Tata Laksana Ekspor, FAQ Ekspor, BTKI) | Prosedur ekspor, PEB, klasifikasi, tarif |
| Perizinan & lartas | INSW | https://www.insw.go.id/ | Larangan/pembatasan, perizinan tunggal |
| Karantina | Badan Karantina Indonesia (Barantin) | https://karantinaindonesia.go.id/ (PTK Online, Phyto-req, IKH/IKI/IKT) | Sertifikat fitosanitari/kesehatan, tindakan karantina |
| Perdagangan luar negeri | Kementerian Perdagangan | https://www.kemendag.go.id/ | Kebijakan ekspor, persyaratan |
| Standardisasi & izin edar pangan | BPOM | https://www.pom.go.id/ | Keamanan pangan, registrasi |
| Statistik ekspor | BPS | https://www.bps.go.id/ | Data ekspor per HS/negara |

### 11.2 Kerangka internasional (primer)
| Domain | Penerbit | Tautan resmi | Kegunaan |
|---|---|---|---|
| Incoterms® 2020 | ICC | https://iccwbo.org/business-solutions/incoterms-rules/ | 11 istilah, alokasi biaya/risiko (berlaku 1 Jan 2020) |
| Tarif & bound/applied rates | WTO | https://www.wto.org/english/tratop_e/tariffs_e/tariffs_e.htm | Tarif MFN, jadwal komitmen |
| Klasifikasi HS | World Customs Organization | https://www.wcoomd.org/ | Nomenklatur Harmonized System |
| Data perdagangan | UN Comtrade | https://comtradeplus.un.org/ | Statistik arus dagang |
| Codex (pangan) | FAO/WHO Codex | https://www.fao.org/fao-who-codexalimentarius/en/ | Standar pangan |
| Fitofitotarif | IPPC (ePhyto) | https://www.ippc.int/ | Standar fitosanitari internasional |

### 11.3 Aturan validasi data (harus diterapkan di sistem)
- **V-1** Tidak ada entri regulasi tanpa `source_url` + `retrieved_at`.
- **V-2** Tampilkan `disclaimer` + `review_status` di setiap keluaran regulasi.
- **V-3** Data `regulatory_intel.py`/`countries.py` saat ini bersifat *indikatif*; tandai `_is_template`/`verified` dan jangan tampilkan sebagai definitif.
- **V-4** Perubahan regulasi memerlukan alur review & tanggal berlaku.
- **V-5** Audit berkala (kuartalan) untuk memverifikasi tautan & status "Berlaku".

> Catatan: permintaan PRD ini menekankan "riset dengan data valid dari sumber terpercaya". Karena agregator pencarian eksternal tidak dapat diakses pada lingkungan ini, rujukan di atas adalah **daftar sumber primer** yang harus dipakai saat mengisi konten, **bukan** klaim fakta final. Implementasi wajib melakukan verifikasi per dokumen.

---

## 12. Definisi Selesai (Definition of Done)

Sebuah item dianggap selesai bila:
1. Kode + test (unit/integrasi/E2E sesuai risiko) hijau.
2. Gate CI relevan lulus (lint, type, test, contract, secret/SCA).
3. Dokumentasi diperbarui (env, README, runbook).
4. Tidak menambah permukaan risiko tanpa kontrol setara.
5. Observability memadai (log/metric untuk jalur baru).
6. Commit atomik dengan pesan sesuai konvensi repo.

---

## 13. Lampiran

- Arsitektur as-is: `guideline/system-flow.drawio`.
- Audit backend/frontend/ops (hasil agen) tersedia pada riwayat sesi; ringkasannya menjadi §7–§8.
- Baseline test: backend `pytest -q` (480), frontend `npm test` (348), `npm run check` (0 error).
