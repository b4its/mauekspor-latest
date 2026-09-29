# 05 — Workspace

Kelompok menu **Workspace**: kolaborasi tim, jadwal, komunikasi, berkas,
otomatisasi, integrasi, materi edukasi, dan pemasaran. Membuat workspace
layak dipakai harian, bukan sekadar pencatat transaksi.

---

## Team (Tim & Peran)

### `/team`
- **Peran:** Exporter (dan peran dengan modul team); Admin melihat semua
- **Guna:** Mengelola anggota tim & peran mereka di workspace.
- **Fitur:** daftar anggota + peran/status/beban kerja; **undang anggota**
  (email, peran, nama), ubah peran, ubah data, keluarkan anggota; ekspor CSV.
- **Terhubung ke:** `$lib/api/team.ts` → `/team/`, `POST /team/invite/`,
  `POST /team/{id}/role/`. Peran menentukan akses (lihat `roleAccess.ts`).
- **Manfaat:** Kolaborasi aman; hak akses sesuai tanggung jawab.

---

## Calendar (Jadwal Tenggat)

### `/calendar`
- **Peran:** semua peran dengan kalender
- **Guna:** Jadwal milestone penting ekspor (tenggat, pengiriman, kepatuhan).
- **Fitur:** tampilan grid kalender (`CalendarGrid`), buat event (judul, tanggal,
  tipe, project), **tandai selesai**, ubah, hapus.
- **Terhubung ke:** `$lib/api/calendar.ts` → `/calendar/`, `POST /calendar/{id}/done/`.
  Event terkait dengan deadline kepatuhan/tugas.
- **Manfaat:** Tenggat kritis terlihat; mengurangi keterlambatan.

---

## Messages (Komunikasi Terstruktur)

### `/messages`
- **Peran:** semua peran relevan
- **Guna:** Komunikasi buyer/supplier/internal per-thread.
- **Fitur:** buat thread (subjek, pihak, kanal, peserta), **kirim** pesan,
  **selesaikan** thread, ubah, hapus/batch.
- **Terhubung ke:** `$lib/api/messages.ts` → `/messages/`, `POST /messages/{id}/send/`,
  `POST /messages/{id}/resolve/`.
- **Manfaat:** Riwayat komunikasi tersimpan & tertaut ke transaksi.

---

## Chat (Asisten Dagang AI)

### `/chat`
- **Peran:** semua peran dengan modul chat
- **Guna:** Sesi percakapan dengan asisten AI (regulasi, costing, kepatuhan).
- **Fitur:** daftar sesi, buat/ubah nama/hapus sesi, kirim pesan dengan konteks
  halaman (`page_context`), **saran pertanyaan**, status AI (`getAiStatus`).
- **Terhubung ke:** `$lib/api/chat.ts` → `/chat/sessions/`, `sendSessionMessage`,
  `getChatSuggestions`. Juga tersedia via `GlobalAiAssistant` (AppShell).
- **Manfaat:** Bantuan cepat in-context; menurunkan hambatan pengetahuan.

---

## Files (Pustaka Bukti & Aset)

### `/files`
- **Peran:** semua peran dengan modul files
- **Guna:** Menyimpan berkas bukti & aset ekspor.
- **Fitur:** daftar berkas (nama, tipe, status, project, ukuran, tag); unggah,
  **verifikasi**, ubah, hapus; **pratinjau** (`previewFileAsset`) dan **analisa
  berkas** (`analyzeFileAsset`) via `FileViewerDialog`; unduh.
- **Terhubung ke:** `$lib/api/files.ts` → `/files/`, `POST /files/{id}/verify/`,
  `/files/{id}/preview/`, `/files/{id}/analyze/`.
- **Manfaat:** Bukti siap audit; analisis dokumen dibantu AI.

---

## Notifications (Peringatan Operasional)

### `/notifications`
- **Peran:** semua peran
- **Guna:** Peringatan operasional (tenggat, blokir, perubahan).
- **Fitur:** daftar notifikasi (modul, keparahan, status), **tandai dibaca**,
  **arsipkan**, hapus/batch; bell di AppShell menampilkan yang belum dibaca.
- **Terhubung ke:** `$lib/api/notifications.ts` → `/notifications/`,
  `POST /notifications/{id}/read/`, `/archive/`.
- **Manfaat:** Tidak ada yang terlewat; fokus pada yang mendesak.

---

## Automations (Aturan Alur Kerja)

### `/automations`
- **Peran:** semua peran dengan modul automations
- **Guna:** Aturan otomatis (trigger → aksi) di dalam workspace.
- **Fitur:** daftar aturan (trigger, aksi, modul, status, jumlah eksekusi);
  buat/ubah/hapus; **aktifkan/jeda**; **jalankan** manual.
- **Terhubung ke:** `$lib/api/automations.ts` → `/automations/`,
  `POST /automations/{id}/activate|pause|run/`. Contoh: blokir compliance →
  buat tugas kritis + notifikasi.
- **Manfaat:** Mengurangi kerja manual berulang; konsistensi proses.

---

## Integrations (Sistem Terhubung)

### `/integrations`
- **Peran:** semua peran dengan modul integrations
- **Guna:** Menghubungkan layanan pihak ketiga (mis. gateway rate forwarder).
- **Fitur:** daftar integrasi (kategori, status, scope, sinkron terakhir);
  buat/ubah/hapus; **hubungkan/putuskan/sinkronkan**.
- **Terhubung ke:** `$lib/api/integrations.ts` → `/integrations/`,
  `POST /integrations/{id}/connect|disconnect|sync/`.
- **Manfaat:** Data antar-sistem mengalir otomatis (rates, bookings).

---

## Templates (Aset yang Dapat Dipakai Ulang)

### `/templates`
- **Peran:** semua peran dengan modul templates
- **Guna:** Template dokumen/aset ekspor yang dapat dipakai ulang.
- **Fitur:** daftar template (kategori, status, dipakai di modul, field);
  buat/ubah/hapus; **gunakan** template.
- **Terhubung ke:** `$lib/api/templates.ts` → `/templates/`,
  `POST /templates/{id}/use/`. Dipakai Documents.
- **Manfaat:** Standarisasi dokumen; menghemat waktu.

---

## Knowledge Base (Playbook Operasional)

### `/knowledge`
- **Peran:** semua peran
- **Guna:** Basis pengetahuan/playbook ekspor.
- **Fitur:** daftar artikel (kategori, status, waktu baca, langkah);
  buat/ubah/hapus; **publikasikan**.
- **Terhubung ke:** `$lib/api/knowledge.ts` → `/knowledge/`,
  `POST /knowledge/{id}/publish/`.
- **Manfaat:** SOP internal mudah diakses; onboarding lebih cepat.

---

## Educational (Platform Belajar)

### `/educational`
- **Peran:** semua peran; konten dikelola `educational/admin`
- **Guna:** Materi belajar ekspor (modul & artikel).
- **Fitur:** daftar modul (level, status, jumlah lesson, progres), artikel,
  pencarian; **pelajaran interaktif** dengan **kuis** (`ModuleQuiz`), **progres
  per user** (`getLessonProgress`, `setLessonComplete`).
- **Terhubung ke:** `$lib/api/educational.ts` → `/educational/`, `/educational/modules/`,
  `getModuleQuiz`, `getLessonProgress`.
- **Manfaat:** Peningkatan kapasitas eksportir/desa; meningkatkan kualitas data & kepatuhan.

### `/educational/modules/[id]` dan `/educational/articles/[id]`
- **Peran:** semua
- **Guna:** Detail modul (dengan lesson & kuis) dan detail artikel.
- **Manfaat:** Pembelajaran terstruktur & terukur.

### `/educational/admin`, `/educational/admin/modules`, `/educational/admin/articles`
- **Peran:** Admin/Exporter (pengelola konten)
- **Guna:** Operasi konten edukasi (buat/ubah/publikasi modul & artikel).
- **Terhubung ke:** `createEducationalModule`, `publishEducationalModule`, dst.
- **Manfaat:** Materi selalu diperbarui sesuai regulasi terkini.

---

## Reference (Regulasi Faktual)

Lihat juga `01-trade-operations.md` → `/reference`. Ringkas: referensi
regulasi bertanggal (timeline, HS 2028, FTA) dengan provenance; read-only.

---

## Marketing (Intelijen Pasar AI & Pricing)

### `/marketing`
- **Peran:** Exporter
- **Guna:** Menghasilkan intelijen pasar & harga per produk (center pemasaran).
- **Fitur:**
  - Dua tab: **Market Intelligence** & **Pricing**.
  - Pilih produk (dukung deep-link `productId`, cari, filter kategori, paginasi).
  - Menghasilkan/menampilkan **Market Intelligence** (negara rekomendasi, ukuran
    pasar, kompetisi, strategi masuk, forwarder) dan **Product Pricing**
    (EXW/FOB/CIF, insight).
  - Tautan ke deep-link dari halaman lain (mis. dari desa/produk).
- **Terhubung ke:** `$lib/api/marketing.ts` → `getOrCreateMarketIntelligence`,
  `getOrCreateProductPricing` (endpoint AI per produk `/products/{id}/ai/*`).
- **Manfaat:** Keputusan pemasaran & harga berbasis AI + data; mempercepat go-to-market.

---

## Manfaat kelompok Workspace

- **Kolaborasi & tata kelola**: tim, jadwal, komunikasi, audit.
- **Efisiensi**: otomatisasi, template, integrasi.
- **Kapasitas**: edukasi & knowledge base menaikkan kualitas output.
- **Pertumbuhan**: marketing center menemukan pasar & harga optimal.
