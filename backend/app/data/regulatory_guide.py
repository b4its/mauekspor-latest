"""Structured, factual export-import regulation data from the 2026 research guide.

Sumber tunggal: guideline/PANDUAN-REGULASI-EKSPOR-IMPOR-2026.md (snapshot
2026-09-29), disusun dari WCO, WTO, Komisi Eropa, USTR, CBP, JDIH Kemendag,
JDIH Kemenkeu, BPK RI, dan firma hukum internasional.

Modul ini mengubah isi panduan (yang bersifat naratif) menjadi struktur data
mesin-baca agar dapat di-seed ke tabel `regulations`/`knowledge_articles` dan
disajikan via API. Tidak ada angka/nama yang dikarang: setiap entri diambil
apa adanya dari panduan. Bila suatu nilai belum dapat diverifikasi, entri
tersebut TIDAK dimasukkan (bukan ditebak).
"""

from __future__ import annotations

SNAPSHOT_DATE = "2026-09-29"
GUIDE = "guideline/PANDUAN-REGULASI-EKSPOR-IMPOR-2026.md"

DISCLAIMER = (
    "Referensi riset bertanggal 29 September 2026; bukan nasihat hukum/tarif. "
    "Regulasi 2025–2026 sangat dinamis — selalu verifikasi ke sumber resmi "
    "sebelum bertransaksi."
)

# ── 4. Incoterms® 2020 (ICC) ─────────────────────────────────────────────────
INCOTERMS_2020 = (
    ("EXW", "Ex Works", "Di tempat penjual", "Semua"),
    ("FCA", "Free Carrier", "Saat diserahkan ke pengangkut", "Semua"),
    ("CPT", "Carriage Paid To", "Saat diserahkan ke pengangkut pertama", "Semua"),
    ("CIP", "Carriage & Insurance Paid To", "Idem (asuransi minimal ICC A)", "Semua"),
    ("DAP", "Delivered at Place", "Di tempat tujuan, belum dibongkar", "Semua"),
    ("DPU", "Delivered at Place Unloaded", "Di tempat tujuan, sudah dibongkar", "Semua"),
    ("DDP", "Delivered Duty Paid", "Di tujuan, bea & pajak impor dibayar penjual", "Semua"),
    ("FAS", "Free Alongside Ship", "Di samping kapal", "Laut"),
    ("FOB", "Free On Board", "Di atas kapal", "Laut"),
    ("CFR", "Cost and Freight", "Di atas kapal (ongkos angkut dibayar penjual)", "Laut"),
    ("CIF", "Cost, Insurance & Freight", "Di atas kapal (asuransi minimal ICC C)", "Laut"),
)

INCOTERMS_NOTES = (
    "Untuk kontainer, ICC menyarankan FCA/CPT/CIP — bukan FOB/CFR/CIF.",
    "DDP ke AS/UE kini berisiko tinggi karena tarif sering berubah; penjual menanggung seluruh bea tambahan.",
    "Nilai pabean Indonesia berbasis CIF. Nilai pabean AS berbasis nilai transaksi (FOB-like).",
)

# ── 2. Sistem HS ─────────────────────────────────────────────────────────────
# Panjang digit nomenklatur per negara/kawasan.
HS_DIGIT_LENGTHS = (
    ("Indonesia & ASEAN", "BTKI / AHTN", 8),
    ("Amerika Serikat", "HTSUS", 10),
    ("Uni Eropa", "CN / TARIC", 10),
    ("Inggris", "UK Global Tariff", 10),
    ("Tiongkok", "China Customs Tariff", 10),
    ("Jepang", "Japan Tariff Schedule", 9),
    ("India", "ITC-HS", 8),
    ("Korea Selatan", "HSK", 10),
    ("Australia", "Working Tariff", 8),
    ("Kanada", "Customs Tariff", 10),
    ("Negara Teluk (GCC)", "GCC Unified Tariff", 12),
    ("Mercosur (Brasil, dll.)", "NCM", 8),
    ("Rusia/EAEU", "TN VED", 10),
)

# Struktur HS 2022 (berlaku saat ini).
HS_2022_STRUCTURE = {
    "sections": 21,
    "chapters": 97,
    "reserved_chapter": 77,
    "headings": 1228,
    "subheadings": 5609,
}

# Ketentuan Umum Menginterpretasi HS (KUMHS) 1–6.
KUMHS_RULES = (
    ("KUMHS 1", "Klasifikasi ditentukan berdasarkan uraian pos dan Catatan Bagian/Bab. Judul bagian/bab hanya untuk referensi."),
    ("KUMHS 2(a)", "Barang belum lengkap/belum rampung, atau dalam keadaan terbongkar (CKD/SKD), diklasifikasikan sebagai barang lengkap jika sudah memiliki karakter esensialnya."),
    ("KUMHS 2(b)", "Campuran atau gabungan bahan diklasifikasikan menurut KUMHS 3."),
    ("KUMHS 3(a)", "Uraian yang paling spesifik didahulukan."),
    ("KUMHS 3(b)", "Berdasarkan bahan/komponen yang memberi karakter esensial."),
    ("KUMHS 3(c)", "Jika belum juga bisa ditentukan, pilih pos dengan urutan nomor terakhir."),
    ("KUMHS 4", "Barang yang paling mirip (akin)."),
    ("KUMHS 5", "Kemasan/wadah khusus (misalnya kotak kamera) diklasifikasikan bersama barangnya."),
    ("KUMHS 6", "Klasifikasi pada tingkat subpos mengikuti prinsip yang sama."),
)

HS_CLASSIFICATION_TIPS = (
    "Identifikasi bahan, fungsi, tingkat pengolahan, dan penggunaan barang.",
    "Baca Catatan Bagian & Bab terlebih dahulu — pengecualian sering tercantum di sana.",
    "Rujuk Explanatory Notes WCO dan Classification Opinions.",
    "Periksa putusan klasifikasi (US CBP CROSS rulings, EU EBTI/BTI).",
    "Di Indonesia, ajukan Penetapan Klasifikasi Barang Sebelum Impor (Advance Ruling) ke DJBC.",
    "Salah klasifikasi dapat berujung pada kekurangan bayar, denda, penahanan barang, dan hilangnya preferensi FTA.",
)

# ── 3. HS 2028 ───────────────────────────────────────────────────────────────
HS_2028 = {
    "effective": "2028-01-01",
    "edition": 8,
    "review_cycle": "Siklus Review ke-7 WCO (Jul 2019–Jun 2025)",
    "amendment_sets": 299,
    "headings_total": 1229,
    "subheadings_total": 5852,
    "headings_new": 6,
    "headings_deleted": 5,
    "subheadings_new": 428,
    "subheadings_deleted": 172,
    "changes": (
        "Vaksin dipindah dari pos 30.02 ke pos baru 30.07 (vaksin manusia, dirinci per penyakit) "
        "dan 30.08 (vaksin lain, termasuk vaksin hewan).",
        "Suplemen makanan: pos baru 21.07 beserta Catatan hukum baru (menyelesaikan sengketa pangan vs farmasi).",
        "Limbah plastik: restrukturisasi pos 39.15, selaras kategori Konvensi Basel (berbahaya, PIC-controlled, lainnya).",
        "Plastik sekali pakai: Catatan 3 Bab 39 memperkenalkan konsep 'single-use' (sedotan, kemasan, peralatan makan, sarung tangan, cotton bud, balon, alat tangkap ikan).",
        "Kesehatan darurat: subpos baru untuk ambulans, APD, ventilator, serta alat diagnostik dan pemantauan.",
        "Pembaruan lain terkait barang yang diatur konvensi internasional, produk lingkungan, peralatan daur ulang, dan teknologi.",
    ),
    "preparation": (
        "WCO menyusun tabel korelasi HS 2022 → HS 2028.",
        "Indonesia/ASEAN diperkirakan menerbitkan AHTN 2028 dan BTKI baru sebelum 2028.",
        "Mulai audit master data HS perusahaan sejak 2027.",
    ),
}

# ── 1. Kerangka hukum & prinsip WTO ──────────────────────────────────────────
INSTITUTIONS = (
    ("WTO", "World Trade Organization", "Aturan perdagangan multilateral: GATT, MFN, National Treatment, SPS, TBT, Trade Facilitation Agreement", "https://www.wto.org/"),
    ("WCO", "World Customs Organization", "Pengelola HS Code, Revised Kyoto Convention, SAFE Framework, AEO, aturan nilai pabean", "https://www.wcoomd.org/"),
    ("ICC", "International Chamber of Commerce", "Incoterms®, UCP 600 (L/C), URC 522", "https://iccwbo.org/"),
    ("UNCTAD/ITC", "UNCTAD / International Trade Centre", "Data & analisis perdagangan (Trade Map, Market Access Map)", "https://www.intracen.org/"),
)

WTO_PRINCIPLES = (
    ("MFN (Most-Favoured-Nation)", "Tarif yang sama untuk semua anggota WTO, kecuali ada FTA atau skema preferensi (GSP)."),
    ("National Treatment", "Barang impor tidak boleh didiskriminasi dibanding produk lokal setelah masuk pasar."),
    ("Trade Remedies", "Anti-dumping (BMAD), Countervailing/Imbalan (BMI), dan Safeguard (BMTP)."),
    ("SPS & TBT", "Standar kesehatan, karantina, dan teknis harus dinotifikasi. Pantau via ePing (epingalert.org)."),
)

WTO_UPDATES = (
    ("2026-03-30", "MC14 di Yaoundé, Kamerun (Maret 2026): moratorium bea masuk atas transmisi elektronik (e-commerce) berakhir karena tidak tercapai konsensus perpanjangan."),
)

# ── 5. Regulasi Indonesia ────────────────────────────────────────────────────
ID_LEGAL_BASIS = (
    ("UU 10/1995 jo. UU 17/2006", "Kepabeanan"),
    ("UU 7/2014 (diubah UU Cipta Kerja)", "Perdagangan"),
    ("PP 29/2021", "Penyelenggaraan Bidang Perdagangan"),
    ("UU 21/2019", "Karantina Hewan, Ikan, dan Tumbuhan (dilaksanakan Badan Karantina Indonesia)"),
    ("PMK 26/PMK.010/2022", "Penetapan Sistem Klasifikasi Barang & Pembebanan BM (BTKI 2022)"),
    ("Permendag 16/2025", "Kebijakan & Pengaturan Impor (regulasi induk, berlaku 30 Agustus 2025)"),
    ("Permendag 17/2025", "Impor Tekstil & Produk Tekstil"),
    ("Permendag 18/2025", "Impor Barang Pertanian & Peternakan"),
    ("Permendag 19/2025", "Impor Garam, Komoditas Perikanan, dll."),
    ("Permendag 23/2023 jo. Permendag 5/2026", "Kebijakan & Pengaturan Ekspor (perubahan ke-4, berlaku 1 April 2026)"),
    ("Permendag 22/2023 jo. Permendag 6/2026", "Barang yang Dilarang untuk Diekspor (perubahan ke-4, berlaku 1 April 2026)"),
    ("PMK 96/2023 jo. PMK 4/2025", "Barang Kiriman (e-commerce/kurir), berlaku 5 Maret 2025"),
    ("PP 36/2023 & perubahannya (terakhir PP 21/2026)", "Devisa Hasil Ekspor SDA"),
)

ID_BTKI = {
    "effective": "2022-04-01",
    "basis": "HS 2022 dan AHTN 2022",
    "lines": 11414,
    "lines_previous": 10813,
    "access": "beacukai.go.id/btki-dan-tarif dan insw.go.id",
}

ID_IMPORT_DEREG_2025 = (
    "Menggantikan Permendag 36/2023 beserta seluruh perubahannya (termasuk Permendag 8/2024).",
    "Struktur baru berbentuk klaster: 1 regulasi induk + regulasi sektoral (TPT, pertanian/peternakan, garam/perikanan). Total 9 Permendag.",
    "Perizinan impor terintegrasi dengan OSS berbasis risiko dan SINSW.",
    "Latar belakang: penumpukan kontainer di pelabuhan 2024 dan perlindungan UMKM.",
)

ID_EXPORT_DEREG_2026 = (
    "Permendag 5/2026 dan Permendag 6/2026 diundangkan 26 Maret 2026 dan berlaku 1 April 2026.",
    "Menghapus sejumlah kewajiban dan sanksi serta mengurangi dokumen lartas ekspor.",
    "Sebelumnya, Permendag 9/2025 membuka jalur manual layanan ekspor (Pasal 51B–51C).",
)

ID_LICENSES = (
    ("NIB (via OSS)", "Berlaku sekaligus sebagai Angka Pengenal Importir (API-U/API-P) dan akses kepabeanan"),
    ("Persetujuan Impor (PI)", "Untuk barang lartas tertentu, bisa berbasis Neraca Komoditas"),
    ("Persetujuan Ekspor (PE)", "Untuk barang ekspor terbatas"),
    ("Laporan Surveyor (LS)", "Verifikasi teknis oleh surveyor yang ditunjuk (komoditas tertentu)"),
    ("SNI Wajib", "Produk wajib SPPT-SNI (Kemenperin)"),
    ("Izin BPOM", "Pangan olahan, obat, kosmetik, suplemen"),
    ("Sertifikat Karantina", "Hewan, ikan, tumbuhan beserta produknya"),
    ("Sertifikat Halal", "Wajib bertahap berdasarkan UU 33/2014 jo. UU Cipta Kerja"),
)

ID_SYSTEMS = (
    ("SINSW / INSW", "Single window nasional untuk perizinan dan lartas. https://insw.go.id/"),
    ("CEISA 4.0 (DJBC)", "Pengajuan PIB (BC 2.0), PEB (BC 3.0), dan dokumen TPB/KB."),
    ("Jalur pemeriksaan", "Merah (fisik + dokumen), Kuning (dokumen), Hijau (tanpa pemeriksaan fisik), MITA/AEO (prioritas)."),
)

ID_IMPORT_LEVIES = (
    ("Bea Masuk (BM)", "Sesuai BTKI (MFN) atau tarif preferensi FTA jika memenuhi SKA"),
    ("PPN Impor", "Tarif 12%, dengan DPP nilai lain 11/12 untuk barang non-mewah, sehingga efektif ±11%"),
    ("PPnBM", "Untuk barang mewah tertentu"),
    ("PPh Pasal 22 Impor", "Umumnya 2,5% (dengan API), 7,5% (tanpa API), hingga 10% untuk barang konsumsi tertentu"),
    ("Cukai", "Untuk BKC (etil alkohol, MMEA, hasil tembakau, dll.)"),
    ("BMAD / BMI / BMTP", "Trade remedies atas produk dan negara tertentu"),
)

ID_IMPORT_EXAMPLE = {
    "cif_usd": 10000,
    "fx_ndpbm": 16000,
    "nilai_pabean_idr": 160000000,
    "bm_10pct_idr": 16000000,
    "nilai_impor_idr": 176000000,
    "ppn_efektif_11pct_idr": 19360000,
    "pph22_2_5pct_idr": 4400000,
    "total_pungutan_idr": 39760000,
    "note": "Ilustrasi. Selalu cek tarif aktual di BTKI/INSW dan kurs NDPBM mingguan.",
}

ID_PARCEL_RULES = (
    "Nilai pabean ≤ USD 3: BM dibebaskan, pajak tetap dipungut sesuai ketentuan.",
    "Nilai > USD 3 s.d. USD 1.500: tarif BM flat (umumnya 7,5%), kecuali komoditas tertentu (tas, sepatu, tekstil, buku).",
    "> USD 1.500: mengikuti ketentuan impor umum.",
    "PMK 4/2025 menyempurnakan layanan, termasuk fasilitas ekspor barang kiriman.",
)

ID_DHE_SDA = {
    "regulation": "PP 21/2026 (perubahan terbaru atas PP 36/2023)",
    "effective": "2026-06-01",
    "repatriation": "100%",
    "nonmigas_placement": "100% di rekening khusus dalam negeri, minimal 12 bulan",
    "migas_placement": "minimal 30%, holding period minimal 3 bulan",
    "bank": "bank Himbara; konversi ke Rupiah maksimal 50%",
    "flexibility": "maksimal 30% di bank non-Himbara, paling lama 3 bulan, untuk eksportir tertentu (terkait perjanjian bilateral/FTA)",
    "tax_incentive": "Insentif PPh dari penempatan DHE bisa sampai 0%, bertingkat sesuai lama penempatan",
    "sectors": "pertambangan, perkebunan, kehutanan, perikanan",
}

ID_HILIRISASI = (
    "Larangan ekspor bijih nikel (sejak 2020), bijih bauksit (sejak Juni 2023), dan konsentrat tembaga. Menteri ESDM menegaskan kembali larangan bauksit & konsentrat tembaga pada Agustus 2026.",
    "Bea Keluar diatur antara lain dalam PMK 68/2025 untuk komoditas tertentu (sawit/CPO dan turunannya, produk mineral olahan, kayu, kulit, biji kakao).",
    "Bea keluar batu bara dan emas: pemerintah merencanakan pengenaannya sejak 2026 dengan skema tarif bertingkat — cek PMK terbaru di jdih.kemenkeu.go.id.",
    "Pungutan Ekspor Sawit dikelola BPDP (d/h BPDPKS), dengan tarif mengacu harga referensi Kemendag.",
)

ID_COO = {
    "portal": "e-SKA Kemendag (e-ska.kemendag.go.id)",
    "forms": ("Form D (ATIGA, kini bisa self-certification)", "Form E (ACFTA)", "Form RCEP",
              "Form IJEPA", "Form AK (Korea)", "Form AANZ", "Form AI (India)",
              "Form CEPA bilateral: IA-CEPA, IK-CEPA, IEFTA, IUAE-CEPA, IC-CEPA"),
    "eu_gsp": "UE (GSP) memakai sistem REX (Registered Exporter), bukan lagi Form A.",
}

# ── 6. Amerika Serikat ───────────────────────────────────────────────────────
US_TIMELINE = (
    ("Feb–Apr 2025", "Tarif IEEPA ('fentanyl' untuk Kanada/Meksiko/Tiongkok, lalu 'reciprocal' untuk hampir semua negara)"),
    ("2025-08-29", "De minimis USD 800 ditangguhkan untuk semua negara"),
    ("2026-02-19", "Agreement on Reciprocal Trade (ART) AS–Indonesia ditandatangani: tarif resiprokal 19%, produk tertentu 0% (Schedule 2B)"),
    ("2026-02-20", "Mahkamah Agung AS (6-3) dalam Learning Resources v. Trump dan V.O.S. Selections v. Trump: IEEPA tidak memberi wewenang Presiden mengenakan tarif. Semua tarif IEEPA dibatalkan"),
    ("2026-02-24", "Tarif IEEPA dihentikan. Digantikan surcharge Section 122 (maksimal 15%, berlaku maksimal 150 hari)"),
    ("2026-04-20", "Proses refund bea IEEPA (CAPE) melalui ACE Portal dimulai"),
    ("Mei 2026", "CIT menyatakan surcharge Section 122 tidak sah, tetapi keringanan terbatas pada penggugat"),
    ("2026-06-24", "CBP menerbitkan Interim Final Rules: penangguhan de minimis tanpa batas waktu"),
    ("Juli 2026", "Review bersama USMCA: AS tidak memperpanjang perjanjian, masuk rezim review tahunan"),
    ("2026-07-24", "Section 122 berakhir otomatis. Diganti tarif Section 301 'Forced Labor' atas 60 ekonomi"),
    ("2026-09-30", "Sidang CIT atas gugatan tarif Section 301 forced labor (termasuk gugatan 25 Jaksa Agung negara bagian)"),
    ("2026-10-06", "Fase 3 CAPE: refund IEEPA untuk entri yang sudah likuidasi lebih dari 80 hari"),
)

US_SECTION_301_FORCED_LABOR = {
    "effective": "2026-07-24",
    "standard_10pct": ("Argentina", "Bangladesh", "Kamboja", "Kanada", "Ekuador", "El Salvador",
                        "Guatemala", "Honduras", "India", "Indonesia", "Yordania", "Malaysia",
                        "Meksiko", "Pakistan", "Sri Lanka", "Trinidad & Tobago", "Inggris"),
    "standard_12_5pct": ("Australia", "Brasil", "Chili", "Tiongkok", "Hong Kong", "Israel",
                          "Selandia Baru", "Filipina", "Singapura", "Afrika Selatan", "Thailand",
                          "Türkiye", "Arab Saudi", "UEA", "Vietnam"),
    "mfn_capped": {"10%": ("Uni Eropa", "Taiwan"), "12.5%": ("Jepang", "Korea Selatan", "Swiss")},
    "exemptions": ("produk pertanian tropis tertentu", "pesawat sipil beserta suku cadangnya",
                    "farmasi tertentu", "barang yang sudah terkena Section 232",
                    "barang USMCA/DR-CAFTA yang bebas bea", "daftar HTS khusus per negara ART (termasuk Indonesia)"),
    "trq_textile": ("Bangladesh", "Kamboja", "Indonesia", "Malaysia"),
    "ftz": "Barang harus masuk dengan status privileged foreign.",
}

US_SECTION_232 = (
    ("Baja & aluminium (Annex I-A)", "50% atas nilai penuh barang sejak 6 Apr 2026 (Inggris 25%, Rusia 200% untuk aluminium)"),
    ("Turunan baja/aluminium/tembaga (Annex I-B)", "25%"),
    ("Tembaga", "50% (I-A) / 25% (I-B)"),
    ("Alat pertanian/industri tertentu", "15% (8 Jun 2026 s.d. 31 Des 2027)"),
    ("Barang modal dengan ≥85% baja/aluminium asal AS", "10%"),
    ("Mobil & suku cadang", "25% (UE/Jepang/Korea/Taiwan: batas 15% termasuk MFN)"),
    ("Kayu gergajian lunak", "10%"),
    ("Furnitur berlapis kain (upholstered)", "25% → 30% mulai 1 Jan 2027"),
    ("Kabinet dapur & vanity", "25% → 50% mulai 1 Jan 2027"),
    ("Semikonduktor (chip logika tertentu)", "25% (sejak 15 Jan 2026, dengan banyak pengecualian)"),
    ("Farmasi paten", "Hingga 100% (sejak 31 Jul 2026). Generik dikecualikan. UE/Jepang/Korea/Swiss dibatasi 15%"),
    ("Polysilicon & turunannya (sel/modul surya)", "Harga impor minimum + tarif 15% (mulai 4 Des 2026)"),
    ("Investigasi berjalan", "Mineral kritis, robotik & mesin industri, alat medis/APD, pesawat, drone"),
)

US_CHINA = (
    "Tarif Section 301 lama (daftar 1–4A, 7,5%–100%) tetap berlaku.",
    "Gencatan dagang berlaku hingga 10 November 2026. Pada September 2026 dilaporkan ada rencana perpanjangan sekitar 2 bulan — cek status terbaru.",
    "178 pengecualian Section 301 diperpanjang hingga 10 November 2026.",
    "Tarif 100% atas crane STS dan chassis asal Tiongkok ditunda hingga 10 November 2026.",
)

US_IMPORT_COMPLIANCE = (
    "ISF '10+2' untuk kargo laut (paling lambat 24 jam sebelum muat).",
    "FDA: Prior Notice (pangan), registrasi fasilitas, FSMA/FSVP.",
    "UFLPA: praduga kerja paksa untuk barang terkait Xinjiang.",
    "Country of origin marking (19 CFR 134).",
    "Anti-dumping/countervailing (AD/CVD): cek di ACCESS (Dept. of Commerce).",
)

# ── 7. Uni Eropa ─────────────────────────────────────────────────────────────
EU_CBAM = {
    "regulation": "Regulation (EU) 2023/956",
    "definitive_start": "2026-01-01",
    "sectors": ("besi & baja", "aluminium", "semen", "pupuk", "hidrogen", "listrik"),
    "de_minimis": "50 ton per importir per tahun (hasil paket penyederhanaan 2025)",
    "declarant": "Importir wajib berstatus Authorised CBAM Declarant.",
    "certificate_sale": "2027-02-01",
    "first_declaration": "2027-09-30",
    "code_from": "2026-01-01",
    "indonesia_impact": "Baja, stainless steel/NPI berbasis nikel, aluminium, dan pupuk harus menyiapkan data emisi tertanam (embedded emissions) yang terverifikasi.",
}

EU_EUDR = {
    "regulation": "Regulation (EU) 2023/1115",
    "commodities": ("sapi", "kakao", "kopi", "kelapa sawit", "karet", "kedelai", "kayu"),
    "large_operators": "2026-12-30",
    "micro_small": "2027-06-30",
    "delegated_act": "2026-07-13",
    "removed_scope": ("kulit sapi", "kulit mentah", "kulit samak", "ban vulkanisir",
                       "kedelai benih", "barang karet vulkanisir", "sabuk konveyor",
                       "jok pesawat dan kendaraan"),
    "added_scope": ("kopi instan", "turunan sawit tertentu", "lidah sapi beku"),
    "added_effective": "2027-12-30",
    "exemptions": ("sampel/produk uji", "limbah", "barang bekas", "material kemasan", "bahan baku obat"),
    "obligations": ("geolokasi lahan", "bebas deforestasi setelah 31 Desember 2020",
                     "legalitas produksi", "Due Diligence Statement (DDS) via Information System UE"),
    "indonesia_relevance": "Sangat relevan untuk Indonesia (sawit, kopi, kakao, karet, kayu).",
}

EU_CUSTOMS_REFORM = (
    "Mulai 1 Juli 2026: bea masuk tetap €3 per jenis barang (per kode tarif) untuk kiriman bernilai rendah (≤ €150). Bersifat sementara hingga 1 Juli 2028. Pembebasan bea €150 berakhir.",
    "EU Customs Reform: pembentukan EU Customs Authority (EUCA) dan EU Customs Data Hub, diterapkan bertahap.",
    "ICS2: pengajuan ENS pra-kedatangan untuk semua moda.",
    "Aturan lain: REACH (kimia), CE marking, GPSR (keamanan produk umum), EU Batteries Regulation, PPWR (kemasan), Forced Labour Regulation (berlaku 2027), CSDDD.",
)

EU_TARIFF = (
    "TARIC (10 digit) memuat tarif MFN, preferensi, kuota, anti-dumping, dan larangan.",
    "GSP UE: Indonesia memperoleh GSP standar untuk sebagian produk (bukan GSP+).",
)

# ── 8. Negara & kawasan utama lainnya ────────────────────────────────────────
OTHER_COUNTRIES = (
    ("Tiongkok", "GACC, MOFCOM", "Registrasi produsen pangan luar negeri (GACC Decree 248 & revisinya); tarif nol untuk 53 negara Afrika mulai 1 Mei 2026; kontrol ekspor tanah jarang (paket Okt 2025 ditangguhkan hingga 10 Nov 2026, paket Apr 2025 tetap berlaku); Export Control Law"),
    ("Inggris", "HMRC", "UK Global Tariff; UK CBAM mulai 1 Jan 2027 (aluminium, semen, pupuk, hidrogen, besi & baja); relief bea £135 untuk barang bernilai rendah dihapus paling lambat 2029"),
    ("Jepang", "Japan Customs, MAFF, MHLW", "NACCS; Food Sanitation Act; IJEPA (Indonesia)"),
    ("India", "CBIC, DGFT", "Wajib IEC; ICEGATE; BIS Quality Control Orders (QCO) yang luas; FTA India–UE selesai dirundingkan 27 Jan 2026"),
    ("Korea Selatan", "KCS, MFDS", "UNI-PASS; IK-CEPA (Indonesia)"),
    ("Australia", "ABF, DAFF", "BICON (biosekuriti ketat); IA-CEPA (Indonesia, sebagian besar tarif 0%)"),
    ("Kanada", "CBSA", "CARM; IC-CEPA (UU implementasi disahkan 6 Mei 2026; berlaku setelah pertukaran nota diplomatik)"),
    ("Meksiko", "SAT/ANAM", "Tarif 5–50% atas 1.463 pos tarif dari negara non-FTA (termasuk Tiongkok dan Indonesia) sejak 1 Jan 2026"),
    ("Arab Saudi", "ZATCA, SFDA, SASO", "Platform SABER (sertifikasi produk); tarif GCC 12 digit; sertifikat halal"),
    ("UEA", "Federal Customs", "IUAE-CEPA dengan Indonesia"),
    ("Rusia/EAEU", "FCS", "Sanksi Barat berlaku; FTA Indonesia–EAEU (ditandatangani Des 2025, proses ratifikasi berjalan)"),
    ("Brasil/Mercosur", "Receita Federal", "NCM 8 digit; EU–Mercosur Interim Trade Agreement diterapkan sementara sejak 1 Mei 2026"),
    ("ASEAN", "ASEAN Secretariat", "AHTN; ASEAN Single Window (ASW) dengan e-Form D; ATIGA upgrade"),
)

# ── 9. Perjanjian perdagangan (FTA/CEPA) ─────────────────────────────────────
ID_FTAS = (
    ("ATIGA (ASEAN)", "in_force", "Upgraded ATIGA (Protokol Kedua) ditandatangani Okt/Des 2025."),
    ("ACFTA (ASEAN–Tiongkok)", "in_force", "ACFTA 3.0 ditandatangani Okt 2025."),
    ("AKFTA, AJCEP, AANZFTA, AIFTA, AHKFTA", "in_force", "Berlaku."),
    ("RCEP", "in_force", "Berlaku untuk Indonesia sejak 2 Januari 2023."),
    ("IJEPA (Jepang)", "in_force", "Berlaku (protokol amandemen)."),
    ("IA-CEPA (Australia)", "in_force", "Berlaku sejak 2020."),
    ("IK-CEPA (Korea)", "in_force", "Berlaku sejak 2023."),
    ("IEFTA CEPA (Swiss, Norwegia, Islandia, Liechtenstein)", "in_force", "Berlaku sejak 1 Nov 2021."),
    ("IUAE-CEPA", "in_force", "Berlaku."),
    ("IC-CEPA (Chili), PTA Pakistan, PTA Mozambik", "in_force", "Berlaku."),
    ("ICA-CEPA (Kanada)", "signed_ratifying", "Ditandatangani 24 Sep 2025. UU Kanada disahkan 6 Mei 2026. Target berlaku akhir 2026."),
    ("IEU-CEPA (Uni Eropa)", "concluded", "Perundingan selesai 23 Sep 2025. Target penandatanganan Oktober 2026, implementasi awal 2027."),
    ("Indonesia–EAEU FTA", "signed_ratifying", "Ditandatangani Des 2025, ratifikasi berjalan."),
    ("ART Indonesia–AS", "in_force", "Ditandatangani 19 Feb 2026. Dasar pengecualian HTS dari tarif Section 301."),
)

GLOBAL_FTAS = (
    ("CPTPP", "Inggris bergabung (Des 2024). Perundingan aksesi Kosta Rika selesai secara substansial (Mei 2026). Indonesia sudah mengajukan aksesi."),
    ("UE–Mercosur", "Penerapan sementara sejak 1 Mei 2026."),
    ("UE–India", "Perundingan selesai 27 Januari 2026, menunggu penandatanganan dan ratifikasi."),
    ("USMCA", "Tidak diperpanjang pada review Juli 2026, masuk review tahunan."),
    ("AfCFTA", "Implementasi bertahap di Afrika."),
)

RULES_OF_ORIGIN = (
    ("WO (Wholly Obtained)", "Diperoleh seluruhnya di satu negara."),
    ("RVC (Regional Value Content)", "Umumnya ≥ 35–40%."),
    ("CTC (Change in Tariff Classification)", "Perubahan CC (bab), CTH (pos), atau CTSH (subpos)."),
    ("Specific Process Rule", "Misalnya untuk tekstil."),
    ("Kumulasi, de minimis, direct consignment", "Syarat penting dalam banyak FTA."),
)

# ── 10. Dokumen ekspor-impor standar ─────────────────────────────────────────
STANDARD_DOCUMENTS = (
    ("Sales Contract / Proforma Invoice", "Kesepakatan dagang"),
    ("Commercial Invoice", "Dasar nilai pabean"),
    ("Packing List", "Rincian kemasan, berat, dan volume"),
    ("Bill of Lading (B/L) / Air Waybill (AWB)", "Bukti pengangkutan (B/L juga dokumen kepemilikan)"),
    ("Certificate of Origin (COO/SKA)", "Asal barang dan preferensi tarif"),
    ("Insurance Policy/Certificate", "Untuk CIF/CIP"),
    ("Phytosanitary/Health/Veterinary Certificate", "Produk pertanian, hewan, pangan"),
    ("Fumigation Certificate / ISPM-15", "Kemasan kayu"),
    ("Certificate of Analysis (COA)", "Mutu dan spesifikasi"),
    ("Halal Certificate", "Pasar Muslim"),
    ("PEB (BC 3.0) / PIB (BC 2.0)", "Pemberitahuan pabean Indonesia"),
    ("Letter of Credit (UCP 600)", "Instrumen pembayaran"),
    ("Safety Data Sheet (SDS)", "Bahan kimia/berbahaya (IMDG/IATA DGR)"),
)

PAYMENT_METHODS = "Open Account → Documentary Collection (D/A, D/P) → L/C → Cash in Advance (dari paling berisiko bagi eksportir)."

# ── 11. Pengendalian ekspor & sanksi ─────────────────────────────────────────
EXPORT_CONTROLS = (
    ("Multilateral", "Wassenaar Arrangement (dual-use/senjata konvensional), Nuclear Suppliers Group, Australia Group (kimia/biologi), MTCR (rudal)."),
    ("Amerika Serikat", "EAR/Commerce Control List (BIS), ITAR, OFAC SDN List, Entity List. Aturan de minimis dan Foreign Direct Product Rule berlaku lintas batas."),
    ("Uni Eropa", "Dual-Use Regulation (EU) 2021/821. Paket sanksi terhadap Rusia/Belarus."),
    ("Tiongkok", "Export Control Law, daftar mineral kritis (galium, germanium, antimon, grafit, tanah jarang)."),
    ("PBB", "Sanksi Dewan Keamanan (Korea Utara, Iran, dll.)."),
    ("Indonesia", "CITES untuk satwa/tumbuhan, Konvensi Basel untuk limbah B3, larangan ekspor tertentu (Permendag 22/2023 jo. 6/2026)."),
    ("Praktik terbaik", "Lakukan screening mitra dagang (denied-party screening) di setiap transaksi."),
)

# ── 12. Portal resmi ─────────────────────────────────────────────────────────
OFFICIAL_PORTALS = (
    ("Indonesia", ("insw.go.id", "beacukai.go.id", "jdih.kemendag.go.id", "jdih.kemenkeu.go.id",
                    "e-ska.kemendag.go.id", "oss.go.id", "peraturan.bpk.go.id")),
    ("Amerika Serikat", ("hts.usitc.gov", "cbp.gov (CSMS)", "ustr.gov", "federalregister.gov", "bis.gov")),
    ("Uni Eropa", ("trade.ec.europa.eu/access-to-markets", "TARIC", "taxation-customs.ec.europa.eu")),
    ("Inggris", ("trade-tariff.service.gov.uk", "gov.uk")),
    ("Tiongkok", ("customs.gov.cn (GACC)", "mofcom.gov.cn")),
    ("Jepang", ("customs.go.jp",)),
    ("India", ("icegate.gov.in", "dgft.gov.in", "cbic.gov.in")),
    ("Australia", ("abf.gov.au", "bicon.agriculture.gov.au")),
    ("Kanada", ("cbsa-asfc.gc.ca", "international.gc.ca")),
    ("ASEAN", ("asean.org", "atr.asean.org (ASEAN Trade Repository)")),
)

GLOBAL_PORTALS = (
    ("HS Code & HS 2028", "wcoomd.org"),
    ("Tarif semua negara", "macmap.org, ttd.wto.org, WTO World Tariff Profiles 2026"),
    ("Statistik perdagangan", "trademap.org, UN Comtrade, WITS (World Bank)"),
    ("Notifikasi SPS/TBT", "epingalert.org"),
    ("Global Trade Helpdesk", "globaltradehelpdesk.org"),
)

# ── 13. Checklist kepatuhan ──────────────────────────────────────────────────
COMPLIANCE_CHECKLIST = (
    ("Sebelum Transaksi", (
        "Klasifikasi HS benar hingga digit nasional negara tujuan (pertimbangkan Advance Ruling).",
        "Cek tarif MFN, preferensi FTA, dan tarif tambahan (Section 301/232 AS, anti-dumping, safeguard).",
        "Cek lartas di negara asal dan negara tujuan (izin, SNI, BPOM, karantina, halal, SABER, dll.).",
        "Screening sanksi dan kontrol ekspor untuk pembeli, bank, dan pengguna akhir.",
        "Tentukan Incoterms (hindari DDP ke pasar dengan tarif volatil).",
        "Periksa pemenuhan aturan asal barang untuk memperoleh SKA preferensi.",
    )),
    ("Kepatuhan Keberlanjutan (Pasar UE/Inggris)", (
        "CBAM: data emisi tertanam (baja, aluminium, pupuk, semen, hidrogen).",
        "EUDR: geolokasi, legalitas, dan DDS (sawit, kopi, kakao, karet, kayu, kedelai, sapi).",
        "Uji tuntas kerja paksa (UFLPA AS, Forced Labour Regulation UE).",
    )),
    ("Operasional", (
        "Dokumen lengkap dan konsisten (invoice, packing list, B/L, COO).",
        "Pengajuan PEB/PIB via CEISA/SINSW.",
        "DHE SDA: penempatan di rekening khusus bank Himbara sesuai PP terbaru.",
        "Arsip dokumen minimal 10 tahun (ketentuan kepabeanan Indonesia).",
    )),
    ("Monitoring Rutin", (
        "Pembaruan tarif AS (CBP CSMS, Federal Register), mingguan.",
        "Hasil sidang CIT atas tarif Section 301 forced labor (sidang 30 Sep 2026).",
        "Status gencatan dagang AS–Tiongkok (batas 10 Nov 2026).",
        "Penandatanganan IEU-CEPA (target Okt 2026) dan berlakunya ICA-CEPA.",
        "Transisi ke HS 2028 (1 Jan 2028) dan BTKI baru.",
    )),
)

# ── Ringkasan timeline penting ───────────────────────────────────────────────
KEY_TIMELINE = (
    ("2026-01-01", "CBAM UE fase definitif; tarif Meksiko untuk negara non-FTA"),
    ("2026-02-20", "Mahkamah Agung AS membatalkan tarif IEEPA"),
    ("2026-03-30", "Moratorium bea e-commerce WTO berakhir"),
    ("2026-04-01", "Permendag 5/2026 & 6/2026 (deregulasi ekspor) berlaku"),
    ("2026-05-01", "EU–Mercosur diterapkan sementara; tarif nol Tiongkok untuk 53 negara Afrika"),
    ("2026-06-01", "PP 21/2026 tentang DHE SDA berlaku"),
    ("2026-07-01", "Bea €3 per jenis barang untuk kiriman nilai rendah ke UE"),
    ("2026-07-24", "Tarif Section 301 forced labor AS berlaku"),
    ("2026-11-10", "Batas gencatan dagang AS–Tiongkok & penangguhan kontrol tanah jarang Tiongkok"),
    ("2026-12-04", "Tarif Section 232 polysilicon AS berlaku"),
    ("2026-12-30", "EUDR berlaku (operator besar/menengah)"),
    ("2027-01-01", "UK CBAM berlaku; kenaikan tarif AS untuk furnitur dan kabinet"),
    ("2027-02-01", "Penjualan sertifikat CBAM UE dimulai"),
    ("2027-06-30", "EUDR berlaku untuk operator mikro/kecil"),
    ("2027-09-30", "Deklarasi CBAM tahunan pertama"),
    ("2028-01-01", "HS 2028 berlaku secara global"),
    ("2028-07-01", "Akhir masa bea sementara €3 UE (digantikan EU Customs Data Hub)"),
)

# ── Sumber rujukan utama ─────────────────────────────────────────────────────
PRIMARY_SOURCES = (
    "WCO: HS Nomenclature 2028 Edition — Amendments effective from 1 January 2028",
    "WTO: Post-MC14 Briefing Note (E-commerce); World Tariff Profiles 2026",
    "Komisi Eropa: CBAM, EUDR (Delegated Act 13 Juli 2026), €3 low-value parcels, EU–Mercosur, EU–India, EU–Indonesia",
    "USTR, White House, CBP (CAPE/IEEPA refunds, de minimis), Congressional Research Service",
    "Canada Gazette Part II, SI/2026-30 (ICA-CEPA)",
    "JDIH Kemendag: Permendag 16/2025, 5/2026, 6/2026; JDIH Kemenkeu: PMK 26/2022, PMK 4/2025, PMK 68/2025",
    "BPK RI (peraturan.bpk.go.id), DJBC (beacukai.go.id), LNSW (insw.go.id)",
    "Analisis firma hukum: Baker Donelson, Thompson Hine, Skadden, Holland & Knight, KSP Law, Hukumonline",
)
