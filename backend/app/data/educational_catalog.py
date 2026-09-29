"""Katalog Data Resmi Modul Edukasi Ekspor, Materi Pembelajaran, dan Kuis Interaktif.

Status data: per 29 September 2026.
Disusun dari acuan kredibel: WCO (HS 2022/2028), WTO, Komisi Eropa (EUDR, CBAM),
USTR & US CBP, PP 21/2026 (DHE SDA), PP 28/2024 (Karantina Pertanian), Permendag 16/2025.
Setiap modul WAJIB memiliki materi pembelajaran berbobot dan kuis evaluasi pemahaman.
"""

from typing import Any

FULL_EDUCATIONAL_MODULES: list[dict[str, Any]] = [
    {
        "id": "EDU-START",
        "title": "Dasar Kesiapan Ekspor & Verifikasi Spesifikasi Produk",
        "level": "Beginner",
        "status": "Published",
        "lessons": 4,
        "completion": 75,
        "summary": "Fondasi kesiapan ekspor: struktur data teknis produk, kualifikasi buyer global, rekonsiliasi dokumen kepabeanan, dan uji kuis kesiapan.",
        "orderIndex": 1,
    },
    {
        "id": "EDU-COMPLIANCE",
        "title": "Regulasi Global 2026: EUDR, CBAM, PPWR & Amandemen HS 2028",
        "level": "Intermediate",
        "status": "Published",
        "lessons": 4,
        "completion": 50,
        "summary": "Kuasai regulasi bebas deforestasi EUDR (cut-off 2020), deklarasi emisi CBAM Uni Eropa, serta peta transisi amandemen WCO HS 2028.",
        "orderIndex": 2,
    },
    {
        "id": "EDU-COSTING",
        "title": "Incoterms® 2020 & Landed Costing Ekspor Realistis",
        "level": "Advanced",
        "status": "Published",
        "lessons": 4,
        "completion": 30,
        "summary": "Pemodelan biaya EXW, FOB, CIF, DAP, margin bersih per unit, mitigasi fluktuasi kurs valas (FX buffer), dan asuransi kargo laut.",
        "orderIndex": 3,
    },
    {
        "id": "EDU-TARIFFS-2026",
        "title": "Rezim Tarif AS, Bilateral ART & Devisa DHE SDA (PP 21/2026)",
        "level": "Advanced",
        "status": "Published",
        "lessons": 4,
        "completion": 25,
        "summary": "Strategi pembebasan tarif Section 301/232 AS via ART Schedule 2B dan kepatuhan retensi 100% 12 bulan DHE SDA di bank devisa Himbara.",
        "orderIndex": 4,
    },
    {
        "id": "EDU-DES-PANEN-01",
        "title": "Ekspor Hasil Panen Segar & Karantina Pertanian (PP 28/2024)",
        "level": "Beginner",
        "status": "Published",
        "lessons": 4,
        "completion": 0,
        "summary": "Prosedur penerbitan Sertifikat Kesehatan Tumbuhan (Phytosanitary Certificate) Barantin, uji bebas Organisme Pengganggu Tumbuhan Karantina (OPTK).",
        "orderIndex": 5,
    },
    {
        "id": "EDU-DES-HALAL-02",
        "title": "Panduan Sertifikasi Halal BPJPH & Akses Pasar Timur Tengah",
        "level": "Beginner",
        "status": "Published",
        "lessons": 4,
        "completion": 0,
        "summary": "Langkah pendaftaran SIHALAL, Sistem Jaminan Produk Halal (SJPH), pengakuan standar GSO/SASO, dan penandaan label halal ekspor.",
        "orderIndex": 6,
    },
    {
        "id": "EDU-DES-KEMAS-03",
        "title": "Pengemasan Kriya Rotan & Kayu Tahan Lembap Kontainer Laut",
        "level": "Intermediate",
        "status": "Published",
        "lessons": 4,
        "completion": 0,
        "summary": "Standar fumigasi ISPM 15, moisture barrier wrapping, silica gel kalkulasi kontainer, serta dokumentasi pre-loading anti klaim asuransi.",
        "orderIndex": 7,
    },
    {
        "id": "EDU-DES-NIB-04",
        "title": "Legalitas BUMDes, NIB OSS-RBA, & Fasilitas Kepabeanan UMK",
        "level": "Beginner",
        "status": "Published",
        "lessons": 5,
        "completion": 0,
        "summary": "Transformasi kelembagaan BUMDes berbadan hukum, pemetaan KBLI 5 digit di OSS-RBA, akses pembiayaan LPEI, dan fasilitas Permendag 16/2025.",
        "orderIndex": 8,
    },
    {
        "id": "EDU-DES-DOC-05",
        "title": "Daftar Dokumen Wajib Ekspor ke Singapura dan Jepang (Khusus Pertanian)",
        "level": "Intermediate",
        "status": "Published",
        "lessons": 4,
        "completion": 0,
        "summary": "Standar pemenuhan dokumen pangan segar SFA Singapura & MAFF Jepang: Phytosanitary Certificate, Health Certificate, Certificate of Analysis (CoA) residu pestisida, dan e-Form D/IJEPA.",
        "orderIndex": 9,
    },
    {
        "id": "EDU-DES-KARANTINA-06",
        "title": "PP 28/2024: Karantina Pertanian untuk Petani & Pelaku Usaha Desa",
        "level": "Beginner",
        "status": "Published",
        "lessons": 4,
        "completion": 0,
        "summary": "Implementasi Peraturan Pemerintah No. 28 Tahun 2024: integrasi layanan satu pintu Badan Karantina Indonesia (Barantin), pemeriksaan pre-border di kebun sentra produksi desa, perlakuan fumigasi, dan sertifikasi digital e-Phyto.",
        "orderIndex": 10,
    },
    {
        "id": "EDU-DES-CITES-07",
        "title": "CITES & Dokumen Asal Bahan Baku untuk Kriya Berbahan Alam",
        "level": "Intermediate",
        "status": "Published",
        "lessons": 4,
        "completion": 0,
        "summary": "Panduan legalitas ekspor kerajinan berbahan flora/fauna liar: pengurusan izin SATS-LN CITES (Appendix II & III), verifikasi Sistem Verifikasi Kelestarian Kayu (SVLK), dan Deklarasi Kesesuaian Pemasok (DKP).",
        "orderIndex": 11,
    },
]

FULL_EDUCATIONAL_LESSONS: list[dict[str, Any]] = [
    # ── EDU-START ─────────────────────────────────────────────────────────────
    {
        "id": "LSN-START-01",
        "moduleId": "EDU-START",
        "title": "Standar Data Produk Ekspor & Spesifikasi Teknis",
        "duration": "5 min",
        "kind": "Reading",
        "completed": True,
        "content": "Kesiapan ekspor menuntut pemisahan deskripsi bebas menjadi data terstruktur: nama latin/botanis, bobot bersih (net weight), bobot kotor (gross weight), dimensi kemasan (PxLxT), standar mutu (grade, moisture content, defect rate), dan dokumen sertifikasi. Data yang rapi memastikan penentuan HS Code otomatis akurat dan mempercepat respons terhadap RFQ pembeli internasional.",
        "keyPoints": [
            "Pisahkan spesifikasi teknis dari deskripsi pemasaran",
            "Catat berat bersih dan berat kotor secara terpisah per kemasan",
            "Sertakan toleransi mutu (kadar air, ukuran biji/screen size, sertifikat)"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-START-02",
        "moduleId": "EDU-START",
        "title": "Kualifikasi Buyer Internasional & Validasi RFQ",
        "duration": "6 min",
        "kind": "Video",
        "videoUrl": "https://www.youtube.com/watch?v=C7VLuiVPIQM",
        "completed": True,
        "content": "Sebelum memberikan penawaran harga resmi (Quotation), eksportir wajib memvalidasi profil calon pembeli: keabsahan perusahaan (nomor registrasi bisnis, situs resmi, referensi perdagangan), riwayat pembayaran, estimasi volume tahunan, serta Incoterm yang diminta. Hindari memberikan harga DDP ke negara yang mengenakan bea masuk dinamis tanpa klausul penyesuaian tarif.",
        "keyPoints": [
            "Validasi legalitas dan rekam jejak buyer sebelum menyusun quotation",
            "Pastikan kuantitas minimum order (MOQ) dan lead time produksi realistis",
            "Tentukan masa berlaku penawaran harga (quotation validity) maksimal 14–30 hari"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-START-03",
        "moduleId": "EDU-START",
        "title": "Validasi Dokumen Ekspor & Rekonsiliasi Faktur",
        "duration": "6 min",
        "kind": "Reading",
        "completed": True,
        "content": "Tiga pilar dokumen pengapalan ekspor: Commercial Invoice, Packing List, dan Bill of Lading (B/L) atau Air Waybill (AWB). Seluruh angka kuantitas, nilai satuan, deskripsi barang, dan nomor pos tarif HS wajib 100% konsisten. Inkonsistensi berat antara packing list dan manifest pelabuhan dapat memicu pemeriksaan fisik jalur merah oleh Bea Cukai.",
        "keyPoints": [
            "Jumlah koli dan berat kotor pada Packing List wajib persis sama dengan B/L",
            "Cantumkan nomor HS Code 8 digit (AHTN/BTKI) pada Commercial Invoice",
            "Simpan arsip pemberitahuan ekspor barang (PEB) minimal 10 tahun untuk audit kepabeanan"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-START-04",
        "moduleId": "EDU-START",
        "title": "Kuis Evaluasi: Dasar Kesiapan Ekspor",
        "duration": "4 min",
        "kind": "Quiz",
        "completed": False,
        "content": "Uji pemahaman Anda mengenai standardisasi data produk ekspor, kualifikasi calon buyer, dan rekonsiliasi dokumen kepabeanan.",
        "keyPoints": [
            "Kuis 3 pertanyaan pilihan ganda",
            "Skor kelulusan minimal 70% untuk sertifikasi modul",
            "Penjelasan kunci jawaban disertakan langsung setelah pengiriman kuis"
        ],
        "quizQuestions": [
            {
                "id": "QZ-START-1",
                "question": "Mengapa berat bersih (net weight) dan berat kotor (gross weight) wajib dicantumkan terpisah pada dokumen ekspor?",
                "options": [
                    "Hanya untuk memenuhi estetika faktur komersial",
                    "Untuk perhitungan bea masuk dan kalkulasi payload kontainer/freight muatan kapal",
                    "Agar buyer bisa membedakan warna kemasan produk",
                    "Tidak wajib jika pengiriman menggunakan pesawat udara"
                ],
                "correctIndex": 1,
                "explanation": "Customs dan shipping line memerlukan gross weight untuk keselamatan pemuatan kontainer (VGM/SOLAS), sedangkan net weight digunakan untuk dasar perhitungan nilai pabean dan sertifikasi mutu."
            },
            {
                "id": "QZ-START-2",
                "question": "Berapa lama masa berlaku wajar untuk surat penawaran harga ekspor (Quotation)?",
                "options": [
                    "Tanpa batas waktu (berlaku selamanya)",
                    "Maksimal 12 bulan tanpa penyesuaian",
                    "Umumnya 14 hingga 30 hari karena risiko fluktuasi freight dan kurs valas",
                    "Hanya 24 jam di semua industri"
                ],
                "correctIndex": 2,
                "explanation": "Freight pelayaran laut dan nilai tukar valas berfluktuasi secara berkala, sehingga masa berlaku penawaran 14–30 hari melindungi eksportir dari kerugian margin."
            },
            {
                "id": "QZ-START-3",
                "question": "Apa dampak utama jika terjadi ketidakcocokan jumlah koli antara Commercial Invoice dan Packing List?",
                "options": [
                    "Barang langsung dilelang oleh otoritas pelabuhan",
                    "Penetapan jalur merah kepabeanan, denda administrasi, dan penahanan kontainer di pelabuhan tujuan",
                    "Pembeli mendapatkan diskon 50%",
                    "Tidak ada konsekuensi apapun"
                ],
                "correctIndex": 1,
                "explanation": "Inkonsistensi data dokumen pengapalan merupakan pemicu utama pemeriksaan fisik (jalur merah) oleh otoritas pabean dan potensi denda demurrage akibat penahanan kontainer."
            }
        ],
    },

    # ── EDU-COMPLIANCE ────────────────────────────────────────────────────────
    {
        "id": "LSN-CMP-01",
        "moduleId": "EDU-COMPLIANCE",
        "title": "Kepatuhan EUDR: Geolokasi Titik/Poligon Lahan Kebun & Due Diligence",
        "duration": "7 min",
        "kind": "Reading",
        "completed": True,
        "content": "Regulasi Bebas Deforestasi Uni Eropa (EUDR — Regulation EU 2023/1115) mewajibkan komoditas kopi, kakao, kelapa sawit, karet, kayu, dan kedelai membuktikan bebas deforestasi setelah cut-off date 31 Desember 2020. Eksportir wajib mengumpulkan koordinat GPS (titik untuk kebun <4 hektare, poligon untuk kebun >=4 hektare) dan menerbitkan Due Diligence Statement (DDS) di portal TRACES Komisi Eropa sebelum kapal sandar di pelabuhan UE.",
        "keyPoints": [
            "Cut-off date bebas deforestasi adalah 31 Desember 2020",
            "Kebun >= 4 hektare wajib poligon koordinat lengkap, bukan satu titik",
            "Due Diligence Statement (DDS) wajib diserahkan sebelum impor disetujui"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-CMP-02",
        "moduleId": "EDU-COMPLIANCE",
        "title": "Transisi Fase Definitif CBAM 2026 & Sertifikasi Emisi",
        "duration": "8 min",
        "kind": "Reading",
        "completed": True,
        "content": "Carbon Border Adjustment Mechanism (CBAM) Uni Eropa memasuki fase definitif pada 1 Januari 2026. Produk besi, baja, aluminium, semen, dan pupuk tidak lagi cukup hanya melaporkan emisi triwulanan. Importir wajib membeli sertifikat CBAM berdasarkan emisi tertanam aktual (embedded emissions) yang diverifikasi oleh verifikator terakreditasi ISO 14065.",
        "keyPoints": [
            "Fase definitif aktif 1 Januari 2026: importir wajib menyerahkan sertifikat CBAM",
            "Eksportir wajib menghitung emisi lingkup 1 (langsung) dan lingkup 2 (listrik pabrik)",
            "Data emisi yang tidak lengkap akan dikenai nilai default emisi tertinggi oleh Komisi Eropa"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-CMP-03",
        "moduleId": "EDU-COMPLIANCE",
        "title": "Persiapan Nomenklatur WCO HS 2028 (Edisi ke-8)",
        "duration": "6 min",
        "kind": "Video",
        "videoUrl": "https://www.youtube.com/watch?v=-I2EJ5MUVkY",
        "completed": False,
        "content": "World Customs Organization (WCO) telah mengesahkan 299 set amandemen HS 2028 yang berlaku per 1 Januari 2028. Perubahan vital meliputi: pemindahan vaksin ke pos 30.07 & 30.08, pos baru 21.07 untuk suplemen makanan dan nutraseutikal, serta restrukturisasi pos 39.15 untuk limbah dan barang plastik sekali pakai (single-use plastics). Eksportir disarankan mengaudit master data HS pada tahun 2027.",
        "keyPoints": [
            "HS 2028 memuat 1.229 pos dan 5.852 subpos internasional",
            "Suplemen makanan dipisahkan tegas ke pos 21.07 untuk mengakhiri sengketa klasifikasi",
            "Plastik sekali pakai mendapatkan Catatan Bab 39 baru dan subpos khusus"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-CMP-04",
        "moduleId": "EDU-COMPLIANCE",
        "title": "Kuis Evaluasi: Kepatuhan Regulasi Ekspor 2026",
        "duration": "4 min",
        "kind": "Quiz",
        "completed": False,
        "content": "Uji pengetahuan Anda mengenai kepatuhan regulasi lingkungan global, EUDR, CBAM fase definitif, dan transisi klasifikasi HS 2028.",
        "keyPoints": [
            "Kuis 3 pertanyaan pilihan ganda",
            "Mencakup aturan cut-off date EUDR, verifikasi CBAM, dan pos suplemen HS 2028",
            "Pembahasan komprehensif diberikan setelah kuis selesai"
        ],
        "quizQuestions": [
            {
                "id": "QZ-CMP-1",
                "question": "Berapakah tanggal cut-off deforestasi yang ditetapkan oleh regulasi EUDR (Regulation EU 2023/1115)?",
                "options": [
                    "31 Desember 2015",
                    "31 Desember 2020",
                    "1 Januari 2024",
                    "30 Desember 2026"
                ],
                "correctIndex": 1,
                "explanation": "Berdasarkan Pasal 2 regulasi EUDR, lahan budidaya komoditas tidak boleh mengalami deforestasi atau degradasi hutan setelah tanggal 31 Desember 2020."
            },
            {
                "id": "QZ-CMP-2",
                "question": "Apa kewajiban baru importir Uni Eropa saat CBAM memasuki fase definitif sejak 1 Januari 2026?",
                "options": [
                    "Hanya mengisi formulir deklarasi sederhana tanpa perhitungan emisi",
                    "Wajib membeli dan menyerahkan sertifikat CBAM berdasarkan emisi aktual yang terverifikasi",
                    "Mendapatkan pembebasan pajak penuh untuk komoditas logam",
                    "Menutup pabrik lokal di seluruh kawasan Eropa"
                ],
                "correctIndex": 1,
                "explanation": "Mulai fase definitif 2026, importir UE wajib membeli sertifikat CBAM seharga kuota ETS dan menyerahkannya setiap tahun berdasarkan emisi karbon tertanam pada produk impor."
            },
            {
                "id": "QZ-CMP-3",
                "question": "Pada edisi Harmonized System 2028 (HS 2028), suplemen makanan dialokasikan ke pos baru nomor berapa?",
                "options": [
                    "Pos 09.01",
                    "Pos 21.07",
                    "Pos 30.02",
                    "Pos 85.04"
                ],
                "correctIndex": 1,
                "explanation": "WCO menetapkan pos baru 21.07 pada HS 2028 beserta Catatan Bab baru untuk menyelesaikan sengketa klasifikasi suplemen pangan antara bab makanan olahan (21) dan farmasi (30)."
            }
        ],
    },

    # ── EDU-COSTING ───────────────────────────────────────────────────────────
    {
        "id": "LSN-CST-01",
        "moduleId": "EDU-COSTING",
        "title": "Perbedaan Risiko & Tanggung Jawab: EXW, FOB, CIF, dan DAP",
        "duration": "8 min",
        "kind": "Reading",
        "completed": True,
        "content": "Incoterms® 2020 ICC mengatur titik peralihan risiko (risk transfer) dan pembagian ongkos logistik antara penjual dan pembeli. Pada EXW, seluruh risiko dan biaya berada di tempat penjual. Pada FOB, risiko beralih saat barang melintasi geladak kapal di pelabuhan muat. Pada CIF, penjual membayar ongkos angkut dan asuransi laut minimal Klausul C hingga pelabuhan tujuan, namun risiko beralih sejak barang dimuat di kapal asal. Untuk kontainer, ICC menganjurkan FCA/CPT/CIP.",
        "keyPoints": [
            "FOB dan CIF hanya berlaku untuk moda transportasi laut dan perairan pedalaman",
            "Untuk muatan peti kemas (kontainer), ICC merekomendasikan penggunaan FCA/CPT/CIP",
            "Nilai pabean impor Indonesia dihitung berbasis CIF, sedangkan AS berbasis nilai transaksi FOB-like"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-CST-02",
        "moduleId": "EDU-COSTING",
        "title": "Kalkulasi Landed Cost per Unit & Buffer Risiko Fluktuasi Kurs",
        "duration": "9 min",
        "kind": "Reading",
        "completed": False,
        "content": "Landed Cost adalah akumulasi seluruh pengeluaran riil hingga barang tiba di gudang tujuan: HPP produk, handling asal, biaya karantina/sertifikasi, ocean freight, asuransi, bea masuk negara tujuan, handling pelabuhan bongkar (THC/demurrage reserve), dan margin laba bersih. Eksportir wajib memasukkan buffer fluktuasi nilai tukar valas (mis. 2–3% FX buffer) untuk melindungi margin kontrak pembayaran berjangka 60–90 hari.",
        "keyPoints": [
            "Hitung biaya kepatuhan dan sertifikasi ke dalam landed cost per unit",
            "Sertakan bantalan deviasi kurs (FX buffer) pada skema pembayaran tempo",
            "Simulasikan skenario kontainer FCL (20ft / 40ft) vs konsolidasi LCL"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-CST-03",
        "moduleId": "EDU-COSTING",
        "title": "Memilih Forwarder, Perhitungan Muatan Kontainer & Asuransi Kargo",
        "duration": "7 min",
        "kind": "Video",
        "videoUrl": "https://www.youtube.com/watch?v=7g7IC4IzjDM",
        "completed": False,
        "content": "Evaluasi forwarder tidak boleh hanya berpatokan pada harga termurah. Parameter penting: ketepatan jadwal sandar (on-time reliability), alokasi ruang kapal (space guarantee) saat peak season, kejelasan biaya lokal (local charges origin & destination), dan responsivitas saat timbul kendala transit. Asuransi kargo Institute Cargo Clauses (ICC A) wajib dipilih untuk barang berharga tinggi atau mudah rusak.",
        "keyPoints": [
            "Bandingkan on-time performance dan lane coverage sebelum booking",
            "Minta konfirmasi total breakdown local charges di pelabuhan bongkar tujuan",
            "Pilih asuransi ICC A (All Risks) untuk barang bernilai tinggi"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-CST-04",
        "moduleId": "EDU-COSTING",
        "title": "Kuis Evaluasi: Incoterms & Strategi Harga Ekspor",
        "duration": "4 min",
        "kind": "Quiz",
        "completed": False,
        "content": "Uji pemahaman Anda mengenai ketentuan Incoterms® 2020, pembagian biaya dan risiko, serta kalkulasi harga landed cost ekspor.",
        "keyPoints": [
            "Kuis 3 pertanyaan pilihan ganda",
            "Evaluasi peralihan risiko FOB/CIF dan rekomendasi peti kemas",
            "Skor dan evaluasi instan setelah pengiriman"
        ],
        "quizQuestions": [
            {
                "id": "QZ-CST-1",
                "question": "Pada kontrak pengapalan dengan syarat CIF (Cost, Insurance & Freight), kapan titik peralihan risiko terjadi dari penjual ke pembeli?",
                "options": [
                    "Saat barang tiba di gudang pembeli di negara tujuan",
                    "Saat barang sudah dimuat di atas kapal di pelabuhan muat asal",
                    "Saat pembeli melunasi pembayaran L/C di bank",
                    "Saat kapal membongkar muatan di pelabuhan tujuan"
                ],
                "correctIndex": 1,
                "explanation": "Meskipun penjual menanggung biaya tambang laut dan polis asuransi sampai pelabuhan tujuan, risiko kerusakan/kehilangan barang beralih ke pembeli segera setelah barang dimuat di atas kapal di pelabuhan asal."
            },
            {
                "id": "QZ-CST-2",
                "question": "Manakah Incoterm yang paling direkomendasikan oleh ICC untuk pengiriman barang dalam peti kemas (kontainer)?",
                "options": [
                    "EXW (Ex Works)",
                    "FOB (Free On Board)",
                    "FCA / CPT / CIP",
                    "DDP (Delivered Duty Paid)"
                ],
                "correctIndex": 2,
                "explanation": "ICC secara eksplisit merekomendasikan FCA/CPT/CIP untuk kontainer karena penyerahan peti kemas dilakukan di terminal darat (CY/CFS) sebelum barang dinaikkan ke kapal."
            },
            {
                "id": "QZ-CST-3",
                "question": "Mengapa eksportir perlu memasukkan 'FX buffer' (bantalan kurs) ke dalam pemodelan harga ekspor?",
                "options": [
                    "Untuk menghindari pembayaran pajak penghasilan",
                    "Melindungi margin laba bersih dari pelemahan kurs valas selama masa kredit pembayaran",
                    "Sebagai komisi wajib bagi forwarder pelayaran",
                    "Untuk membayar denda kelebihan muatan kontainer"
                ],
                "correctIndex": 1,
                "explanation": "Pada transaksi dengan termin pembayaran tempo (Net 30/60/90), fluktuasi nilai tukar valas dapat menggerus marjin laba bila tidak diantisipasi dengan bantalan kurs wajar."
            }
        ],
    },

    # ── EDU-TARIFFS-2026 ──────────────────────────────────────────────────────
    {
        "id": "LSN-TRF-01",
        "moduleId": "EDU-TARIFFS-2026",
        "title": "Mitigasi Tarif Section 301/232 AS via Perjanjian Bilateral ART Schedule 2B",
        "duration": "8 min",
        "kind": "Reading",
        "completed": True,
        "content": "Pemerintah Amerika Serikat memberlakukan rezim tarif dinamis sepanjang 2025–2026: tarif Section 301, Section 232 (baja 25%, aluminium 10%), serta kenaikan tarif barang strategis. Indonesia dan AS menyepakati Agreement on Reciprocal Trade (ART) pada 19 Februari 2026, di mana komoditas kopi, kakao, dan rempah Indonesia yang memenuhi kriteria Schedule 2B dibebaskan dari tarif tambahan 10%. Eksportir wajib mencantumkan deklarasi ART pada dokumen pabean AS CBP 7501.",
        "keyPoints": [
            "Periksa apakah produk Anda tercantum dalam Schedule 2B Agreement on Reciprocal Trade",
            "Lampirkan bukti sertifikasi asal ART Schedule 2B untuk pembuktian pembebasan tarif 10%",
            "Pantau de minimis threshold AS ($800) yang mengalami pengetatan pengawasan pada produk tekstil/garment"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-TRF-02",
        "moduleId": "EDU-TARIFFS-2026",
        "title": "Kewajiban Devisa Hasil Ekspor (DHE SDA) PP 21/2026: Retensi 100% 12 Bulan",
        "duration": "7 min",
        "kind": "Reading",
        "completed": False,
        "content": "Pemerintah RI menerbitkan PP No. 21 Tahun 2026 (berlaku mulai 1 Juni 2026) sebagai pengetatan aturan devisa hasil ekspor sumber daya alam. Ketentuan kunci: setiap ekspor sektor SDA (pertambangan, perkebunan, kehutanan, perikanan) dengan nilai FOB pada PEB minimal USD 250.000 wajib memasukkan 100% devisanya ke dalam Rekening Khusus DHE SDA di bank devisa dalam negeri (Himbara) dan dipertahankan minimal selama 12 bulan (untuk non-migas). Sanksi pelanggaran adalah penolakan layanan ekspor dan pemblokiran sistem CEISA/INSW Bea Cukai.",
        "keyPoints": [
            "Threshold ekspor SDA: nilai FOB pada dokumen PEB minimal USD 250.000",
            "Retensi 100% selama minimal 12 bulan di bank devisa domestik (Himbara)",
            "Pemerintah memberikan insentif PPh final bunga deposito DHE hingga 0%"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-TRF-03",
        "moduleId": "EDU-TARIFFS-2026",
        "title": "Tata Cara Pembukaan Rekening Khusus DHE & Insentif Pajak Bunga Deposito",
        "duration": "6 min",
        "kind": "Video",
        "videoUrl": "https://www.youtube.com/watch?v=S0T09u1T8kY",
        "completed": False,
        "content": "Langkah kepatuhan DHE SDA: 1) Buka Rekening Khusus (Reksus) DHE SDA di bank Himbara (Mandiri, BRI, BNI, BTN) sebelum pengapalan; 2) Pastikan buyer mentransfer dana devisa ke Reksus tersebut; 3) Manfaatkan instrumen penempatan term deposit valas Bank Indonesia dengan tarif PPh final bunga deposito 0% untuk tenor di atas 6 bulan; 4) Sistem CEISA dan Bank Indonesia melakukan rekonsiliasi data PEB secara otomatis.",
        "keyPoints": [
            "Buka rekening khusus berlabel DHE SDA sebelum mengajukan PEB",
            "Gunakan instrumen Term Deposit Valas BI untuk insentif pembebasan PPh bunga",
            "Data devisa masuk direkonsiliasi otomatis oleh Bank Indonesia dan DJBC"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-TRF-04",
        "moduleId": "EDU-TARIFFS-2026",
        "title": "Kuis Evaluasi: Kebijakan Tarif & Kepatuhan Devisa DHE SDA",
        "duration": "4 min",
        "kind": "Quiz",
        "completed": False,
        "content": "Uji penguasaan Anda mengenai mitigasi tarif ekspor AS dan kepatuhan hukum Devisa Hasil Ekspor SDA PP 21/2026.",
        "keyPoints": [
            "Kuis 3 pertanyaan pilihan ganda",
            "Mencakup batas minimal PEB DHE SDA, durasi retensi, dan mitigasi tarif ART",
            "Penjelasan yuridis lengkap setelah pengiriman"
        ],
        "quizQuestions": [
            {
                "id": "QZ-TRF-1",
                "question": "Berapa ambang batas nilai ekspor (FOB pada PEB) yang mewajibkan penempatan DHE SDA menurut PP No. 21 Tahun 2026?",
                "options": [
                    "Minimal USD 50,000",
                    "Minimal USD 100,000",
                    "Minimal USD 250,000",
                    "Minimal USD 1,000,000"
                ],
                "correctIndex": 2,
                "explanation": "Berdasarkan ketentuan PP No. 21 Tahun 2026, kewajiban penempatan DHE SDA berlaku bagi eksportir dengan nilai ekspor pada dokumen PEB sebesar minimal USD 250,000 atau ekuivalennya."
            },
            {
                "id": "QZ-TRF-2",
                "question": "Berapa persentase dan durasi minimal penempatan DHE SDA non-migas di bank devisa domestik berdasarkan PP 21/2026?",
                "options": [
                    "30% selama minimal 3 bulan",
                    "50% selama minimal 6 bulan",
                    "100% selama minimal 12 bulan",
                    "100% tanpa batas waktu penempatan"
                ],
                "correctIndex": 2,
                "explanation": "PP 21/2026 memperketat kewajiban DHE SDA non-migas menjadi penempatan 100% selama jangka waktu paling singkat 12 bulan di rekening khusus bank devisa dalam negeri."
            },
            {
                "id": "QZ-TRF-3",
                "question": "Bagaimana cara eksportir kopi Indonesia membebaskan diri dari tarif tambahan 10% saat mengekspor ke Amerika Serikat?",
                "options": [
                    "Mengubah nama produk menjadi produk lokal AS",
                    "Membuktikan pemenuhan kriteria Schedule 2B pada perjanjian bilateral US-Indonesia ART",
                    "Mengirimkan barang lewat negara transit tanpa dokumen asal",
                    "Membayar uang jaminan tunai ke otoritas pelabuhan AS"
                ],
                "correctIndex": 1,
                "explanation": "Berdasarkan Perjanjian Bilateral US-Indonesia Agreement on Reciprocal Trade (ART) 19 Februari 2026, produk Indonesia yang terdaftar di Schedule 2B dikecualikan dari tarif 10% melalui pembuktian sertifikasi asal pada deklarasi CBP 7501."
            }
        ],
    },

    # ── EDU-DES-PANEN-01 ──────────────────────────────────────────────────────
    {
        "id": "LSN-PAN-01",
        "moduleId": "EDU-DES-PANEN-01",
        "title": "Prosedur Sertifikat Kesehatan Tumbuhan (Phytosanitary) Barantin",
        "duration": "6 min",
        "kind": "Reading",
        "completed": False,
        "content": "Pemerintah melalui Badan Karantina Indonesia (Barantin) berdasarkan UU 21/2019 dan PP 28/2024 mewajibkan setiap komoditas pertanian segar (buah, sayur, rempah basah, bibit) memiliki Sertifikat Kesehatan Tumbuhan (KT-1 / Phytosanitary Certificate). Pengajuan dilakukan melalui portal PPK Online Barantin minimal 3 hari sebelum pemuatan kontainer. Petugas karantina akan mengambil sampel acak untuk uji laboratorium bebas OPTK (Organisme Pengganggu Tumbuhan Karantina).",
        "keyPoints": [
            "Ajukan permohonan pemeriksaan karantina (PPK Online) sebelum barang dimuat ke kontainer",
            "Ketahui daftar OPTK golongan I dan II yang dilarang oleh negara tujuan ekspor",
            "Sertifikat KT-1 wajib menyertai dokumen pengapalan fisik dan pertukaran data e-Phyto"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-PAN-02",
        "moduleId": "EDU-DES-PANEN-01",
        "title": "Standar Mutu Kopi Gayo, Kakao, & Vanila untuk Buyer Jepang dan Uni Eropa",
        "duration": "7 min",
        "kind": "Reading",
        "completed": False,
        "content": "Komoditas perkebunan desa memiliki potensi pasar premium di Jepang dan Uni Eropa bila memenuhi batas ambang residu pestisida (MRL - Maximum Residue Limit) dan standar mikotoksin (Aflatoksin & Ochratoxin A). Untuk biji kopi, kadar air maksimal adalah 12,5%, dengan defect rate maksimal grade 1 (maksimal 11 nilai cacat menurut SCAA). Biji vanila wajib memiliki kadar vanilin minimal 1,8% dengan kadar air 25–30%.",
        "keyPoints": [
            "Uji batas residu pestisida di laboratorium terakreditasi KAN sebelum shipment",
            "Jaga kadar air biji kopi di bawah 12,5% untuk mencegah timbulnya jamur Ochratoxin A",
            "Gunakan kemasan kedap udara (mis. GrainPro liner) di dalam karung goni"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-PAN-03",
        "moduleId": "EDU-DES-PANEN-01",
        "title": "Pengemasan Higienis & Perlakuan Fumigasi Bebas Serangga untuk Hasil Kebun",
        "duration": "6 min",
        "kind": "Video",
        "videoUrl": "https://www.youtube.com/watch?v=JnMtuZTjV6Q",
        "completed": False,
        "content": "Seluruh hasil panen pertanian yang diangkut menggunakan palet kayu wajib memenuhi standar internasional ISPM 15 (perlakuan panas Heat Treatment atau fumigasi). Kemasan primer karung goni wajib dilapisi kantong hermetik (seperti GrainPro) untuk menjaga kadar air dan mematikan serangga hama gudang (seperti kumbang bubuk kopi Hypothenemus hampei) selama pelayaran 30 hari.",
        "keyPoints": [
            "Wajib sertifikat fumigasi atau tanda cap stempel ISPM 15 pada setiap palet kayu",
            "Kemasan hermetik mencegah penyerapan kelembapan udara laut di dalam kontainer",
            "Lakukan pemeriksaan visual menyeluruh sebelum segel pabean kontainer dipasang"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-PAN-04",
        "moduleId": "EDU-DES-PANEN-01",
        "title": "Kuis Evaluasi: Karantina Pertanian & Standar Mutu Panen",
        "duration": "4 min",
        "kind": "Quiz",
        "completed": False,
        "content": "Uji penguasaan Anda mengenai pengurusan sertifikat karantina tumbuhan, standar batas residu, dan kemasan hasil kebun desa.",
        "keyPoints": [
            "Kuis 3 pertanyaan pilihan ganda",
            "Standar karantina Barantin PP 28/2024 dan ambang batas mutu internasional",
            "Penjelasan kunci jawaban instan"
        ],
        "quizQuestions": [
            {
                "id": "QZ-PAN-1",
                "question": "Lembaga resmi pemerintah Indonesia yang menerbitkan Sertifikat Kesehatan Tumbuhan (Phytosanitary Certificate) adalah:",
                "options": [
                    "Kementerian Pariwisata",
                    "Badan Karantina Indonesia (Barantin)",
                    "Dinas Perhubungan Laut",
                    "Kamar Dagang dan Industri (KADIN)"
                ],
                "correctIndex": 1,
                "explanation": "Berdasarkan UU 21/2019 dan penataan kelembagaan PP 28/2024, Badan Karantina Indonesia (Barantin) adalah lembaga tunggal yang berwenang menerbitkan sertifikat karantina hewan, ikan, dan tumbuhan."
            },
            {
                "id": "QZ-PAN-2",
                "question": "Berapakah kadar air maksimal standar ekspor untuk biji kopi arabika agar terhindar dari jamur mikotoksin?",
                "options": [
                    "Maksimal 25%",
                    "Maksimal 18%",
                    "Maksimal 12,5%",
                    "Bebas tanpa batasan"
                ],
                "correctIndex": 2,
                "explanation": "Standar Nasional Indonesia (SNI) dan International Coffee Organization menetapkan kadar air biji kopi ekspor maksimal 12,5% guna mencegah pertumbuhan jamur penghasil mikotoksin berbahaya Ochratoxin A."
            },
            {
                "id": "QZ-PAN-3",
                "question": "Apa fungsi utama penggunaan kantong pelindung hermetik (seperti GrainPro) di dalam karung goni ekspor?",
                "options": [
                    "Menambah berat barang agar harga jual lebih mahal",
                    "Mengunci kadar air konstan dan mematikan serangga hama akibat kondisi atmosfer anaerobik",
                    "Hanya untuk mempercantik tampilan luar karung",
                    "Sebagai pengganti Bill of Lading"
                ],
                "correctIndex": 1,
                "explanation": "Kantong hermetik menahan pertukaran uap air dan oksigen dari luar sehingga kualitas rasa terjaga serta serangga hama gudang mati secara alami selama perjalanan kapal."
            }
        ],
    },

    # ── EDU-DES-HALAL-02 ──────────────────────────────────────────────────────
    {
        "id": "LSN-HAL-01",
        "moduleId": "EDU-DES-HALAL-02",
        "title": "Transformasi Regulasi Halal & Registrasi SIHALAL BPJPH",
        "duration": "6 min",
        "kind": "Reading",
        "completed": False,
        "content": "Berdasarkan UU No. 33 Tahun 2014 jo. Perppu No. 2 Tahun 2022, seluruh produk makanan dan minuman yang beredar dan diekspor wajib bersertifikat halal. Badan Penyelenggara Jaminan Produk Halal (BPJPH) mengelola perizinan terintegrasi via portal SIHALAL (ptsp.halal.go.id). Eksportir desa dapat memanfaatkan jalur Sertifikasi Halal Reguler maupun Fasilitasi Self-Declare bagi pelaku Usaha Mikro dan Kecil (UMK).",
        "keyPoints": [
            "Pendaftaran dilakukan secara daring melalui sistem SIHALAL BPJPH",
            "Tunjuk minimal satu orang Penyelia Halal bersertifikat di internal BUMDes",
            "Dokumentasikan manual Sistem Jaminan Produk Halal (SJPH) secara tertulis"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-HAL-02",
        "moduleId": "EDU-DES-HALAL-02",
        "title": "Kesepakatan Saling Pengakuan (MRA) untuk Pasar Timur Tengah & ASEAN",
        "duration": "7 min",
        "kind": "Reading",
        "completed": False,
        "content": "Untuk menembus pasar Arab Saudi, Uni Emirat Arab, dan kawasan Teluk (GCC), sertifikat halal Indonesia diakui melalui Mutual Recognition Agreement (MRA) antara BPJPH dan lembaga halal akreditasi setempat (seperti SASO dan SFDA di Arab Saudi, serta ESMA/MoIAT di UEA). Pastikan bahan baku kritis (seperti perisa, gelatin, enzim, emulsifier) memiliki sertifikat halal yang diakui secara timbal balik.",
        "keyPoints": [
            "Periksa status akreditasi MRA lembaga pemeriksa halal negara tujuan",
            "Gunakan label halal resmi Indonesia beserta nomor registrasi yang terverifikasi",
            "Produk olahan pangan desa wajib bebas dari kontaminasi silang fasilitas non-halal"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-HAL-03",
        "moduleId": "EDU-DES-HALAL-02",
        "title": "Audit Lapangan Lembaga Pemeriksa Halal (LPH) & Penerbitan Sertifikat",
        "duration": "6 min",
        "kind": "Video",
        "videoUrl": "https://www.youtube.com/watch?v=UaPPWKAYj7E",
        "completed": False,
        "content": "Tahapan sertifikasi halal reguler: 1) Pemilihan Lembaga Pemeriksa Halal (LPH seperti LPPOM MUI, Sucofindo, Surveyor Indonesia); 2) Verifikasi dokumen bahan baku dan diagram alir proses produksi; 3) Audit lapangan oleh auditor halal di tempat pengolahan produk desa; 4) Sidang Fatwa Halal Komite Fatwa MUI; 5) Penerbitan Ketetapan Halal dan Sertifikat Halal BPJPH berjangka waktu 4 tahun.",
        "keyPoints": [
            "Siapkan logbook harian penerimaan bahan baku dan catatan produksi halal",
            "Auditor memeriksa kebersihan lini produksi, wadah simpan, dan kemasan",
            "Sertifikat halal kini berlaku seumur hidup selama tidak ada perubahan komposisi bahan"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-HAL-04",
        "moduleId": "EDU-DES-HALAL-02",
        "title": "Kuis Evaluasi: Sertifikasi Halal Ekspor",
        "duration": "4 min",
        "kind": "Quiz",
        "completed": False,
        "content": "Uji pengetahuan Anda mengenai regulasi jaminan produk halal, proses pendaftaran SIHALAL, dan pengakuan standar halal di pasar internasional.",
        "keyPoints": [
            "Kuis 3 pertanyaan pilihan ganda",
            "Mencakup peran BPJPH, MRA sertifikasi, dan persyaratan penyelia halal",
            "Pembahasan detail untuk setiap jawaban"
        ],
        "quizQuestions": [
            {
                "id": "QZ-HAL-1",
                "question": "Lembaga pemerintah yang berwenang menerbitkan Sertifikat Halal resmi di Indonesia adalah:",
                "options": [
                    "Kementerian Luar Negeri",
                    "Badan Penyelenggara Jaminan Produk Halal (BPJPH) Kemenag",
                    "Kementerian BUMN",
                    "Badan Koordinasi Penanaman Modal (BKPM)"
                ],
                "correctIndex": 1,
                "explanation": "Berdasarkan amanat UU No. 33 Tahun 2014, BPJPH adalah badan pemerintah di bawah Kemenag yang berwenang menerbitkan sertifikat halal, bekerja sama dengan LPH dan Komisi Fatwa."
            },
            {
                "id": "QZ-HAL-2",
                "question": "Apa fungsi dari Mutual Recognition Agreement (MRA) dalam sertifikasi halal antarnegara?",
                "options": [
                    "Untuk mengenakan tarif bea masuk ganda",
                    "Saling mengakui kesetaraan standar sertifikat halal sehingga produk tidak perlu sertifikasi ulang di negara tujuan",
                    "Membatalkan seluruh sertifikat lokal di negara pengimpor",
                    "Menghapus kewajiban pemeriksaan pabean"
                ],
                "correctIndex": 1,
                "explanation": "MRA halal memungkinkan sertifikat halal yang diterbitkan BPJPH diakui secara sah oleh otoritas pangan negara tujuan (misal SFDA Arab Saudi), mempercepat proses izin edar impor."
            },
            {
                "id": "QZ-HAL-3",
                "question": "Siapakah personil kunci yang wajib ditunjuk oleh pelaku usaha di internal perusahaan untuk mengawal proses sertifikasi halal?",
                "options": [
                    "Pialang bea cukai eksternal",
                    "Penyelia Halal yang beragama Islam dan memahami syariat jaminan produk halal",
                    "Supir truk ekspedisi",
                    "Kepala kantor imigrasi pelabuhan"
                ],
                "correctIndex": 1,
                "explanation": "UU JPH mewajibkan setiap pelaku usaha memiliki minimal seorang Penyelia Halal internal yang bertugas memimpin dan mengawasi implementasi Sistem Jaminan Produk Halal."
            }
        ],
    },

    # ── EDU-DES-KEMAS-03 ──────────────────────────────────────────────────────
    {
        "id": "LSN-KMS-01",
        "moduleId": "EDU-DES-KEMAS-03",
        "title": "Teknik Moisture Barrier & Kalkulasi Silica Gel Kontainer",
        "duration": "6 min",
        "kind": "Reading",
        "completed": False,
        "content": "Pengiriman laut melintasi zona tropis menuju negara 4 musim menghasilkan fenomena 'hujan kontainer' (container rain) akibat kondensasi udara dingin pada langit-langit peti kemas. Untuk produk kerajinan rotan, kayu, dan anyaman serat alam, eksportir wajib menggunakan desiccant pole kalsium klorida (bukan silica gel kecil biasa) dengan rasio minimal 1 unit (1 kg) per 5 meter kubik volume kontainer, serta membungkus barang dengan plastik barrier kedap uap air.",
        "keyPoints": [
            "Gunakan container desiccant kalsium klorida berkemampuan serap 200–300% berat kering",
            "Bungkus kriya dengan kertas krep dan plastik pelindung kelembapan (moisture barrier)",
            "Hindari memasukkan kardus karton yang basah atau lembap saat stuffing kontainer"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-KMS-02",
        "moduleId": "EDU-DES-KEMAS-03",
        "title": "Perlindungan Sudut (Corner Protectors) & Fumigasi Palet ISPM 15",
        "duration": "6 min",
        "kind": "Video",
        "videoUrl": "https://www.youtube.com/watch?v=tK-V0wXk-V0",
        "completed": False,
        "content": "Kerusakan fisik terbesar pada kriya furnitur rotan dan kayu terjadi akibat guncangan gelombang laut (pitching & rolling). Pasang edge corner protectors karton tebal pada seluruh sudut kemasan luar. Seluruh palet kayu penopang wajib memiliki cap logo gandum resmi ISPM 15 (menandakan perlakuan Heat Treatment HT atau Methyl Bromide MB) dari perusahaan fumigasi teregistrasi Barantin.",
        "keyPoints": [
            "Corner protector melindungi sudut karton dari tindihan strapping band",
            "Palet tanpa cap ISPM 15 akan ditolak masuk dan diperintahkan re-ekspor oleh customs tujuan",
            "Beri bantalan dunnage air bag di sela-sela palet agar muatan tidak bergeser saat kapal berlayar"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-KMS-03",
        "moduleId": "EDU-DES-KEMAS-03",
        "title": "SOP Dokumentasi Pre-Loading Foto untuk Validasi Klaim Asuransi",
        "duration": "6 min",
        "kind": "Reading",
        "completed": False,
        "content": "Lebih dari 60% klaim asuransi kargo ditolak perusahaan penjamin karena eksportir tidak memiliki bukti kondisi awal muatan sebelum berangkat. Terapkan SOP foto wajib: 1) Foto kondisi lantai dan dinding kontainer kosong (pastikan bersih, kering, tidak bocor cahaya); 2) Foto lapisan pertama pemuatan barang; 3) Foto desiccant pole terpasang; 4) Foto saat kontainer terisi 100%; 5) Foto penutupan pintu sebelah kanan kontainer beserta nomor segel (seal number).",
        "keyPoints": [
            "Pemeriksaan 'light check' kontainer kosong: masuk dan tutup pintu, pastikan tiada lubang cahaya",
            "Dokumentasikan nomor seri segel kontainer (bolt seal) secara berdampingan dengan B/L",
            "Bukti foto pre-loading adalah syarat mutlak persetujuan klaim surveyor asuransi maritim"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-KMS-04",
        "moduleId": "EDU-DES-KEMAS-03",
        "title": "Kuis Evaluasi: Pengemasan Kriya & Proteksi Kontainer",
        "duration": "4 min",
        "kind": "Quiz",
        "completed": False,
        "content": "Uji pemahaman Anda mengenai mitigasi risiko kelembapan laut, standar palet ISPM 15, dan dokumentasi klaim asuransi kriya.",
        "keyPoints": [
            "Kuis 3 pertanyaan pilihan ganda",
            "Standar pengemasan kriya rotan/kayu dan regulasi ISPM 15",
            "Penjelasan kunci jawaban praktis"
        ],
        "quizQuestions": [
            {
                "id": "QZ-KMS-1",
                "question": "Apakah penyebab utama fenomena 'container rain' (hujan kontainer) yang sering merusak produk kerajinan alam?",
                "options": [
                    "Air laut yang merembes melalui celah pintu kontainer",
                    "Kondensasi udara lembap di dalam kontainer akibat perbedaan suhu ekstrem siang dan malam",
                    "Pencucian kontainer yang tidak dikeringkan",
                    "Kesalahan awak kapal menyiram atap kapal"
                ],
                "correctIndex": 1,
                "explanation": "Udara hangat dan lembap di dalam kontainer mengalami pengembunan saat dinding luar kontainer mendingin drastis di perairan dingin, menjatuhkan tetesan air ke muatan kriya."
            },
            {
                "id": "QZ-KMS-2",
                "question": "Tanda standar internasional apakah yang wajib tercantum pada palet kayu penopang ekspor menurut aturan karantina dunia?",
                "options": [
                    "Label SNI",
                    "Cap Logo Gandum ISPM 15",
                    "Tanda barcode toko ritel",
                    "Stempel tanda lunas bea cukai"
                ],
                "correctIndex": 1,
                "explanation": "Standar ISPM 15 (International Standards for Phytosanitary Measures) mewajibkan palet kayu diberi cap logo gandum bertuliskan kode negara dan jenis perlakuan (HT/MB) untuk mencegah penyebaran hama kayu lintas benua."
            },
            {
                "id": "QZ-KMS-3",
                "question": "Mengapa foto nomor segel kontainer (bolt seal) pada pintu peti kemas wajib diambil sebelum kontainer diberangkatkan?",
                "options": [
                    "Hanya untuk koleksi dokumentasi media sosial eksportir",
                    "Sebagai bukti hukum bahwa kontainer tertutup rapat dan belum pernah dibuka sejak pemuatan awal, krusial bagi klaim asuransi jika terjadi pencurian/kerusakan",
                    "Syarat untuk mendapatkan diskon tol laut",
                    "Sebagai pengganti nota pajak pertambahan nilai"
                ],
                "correctIndex": 1,
                "explanation": "Foto segel utuh membuktikan muatan berada dalam kondisi aman saat diserahkan ke pengangkut, menjadi dasar klaim asuransi bila segel tiba di tujuan dalam kondisi rusak atau berganti nomor."
            }
        ],
    },

    # ── EDU-DES-NIB-04 ────────────────────────────────────────────────────────
    {
        "id": "LSN-NIB-01",
        "moduleId": "EDU-DES-NIB-04",
        "title": "Transformasi BUMDes Berbadan Hukum & Pengurusan NIB di OSS-RBA",
        "duration": "6 min",
        "kind": "Reading",
        "completed": False,
        "content": "UU Cipta Kerja dan PP No. 11 Tahun 2021 menetapkan BUMDes (Badan Usaha Milik Desa) dan BUMDes Bersama resmi berstatus sebagai badan hukum. Pendaftaran dilakukan ke Kementerian Desa, dilanjutkan dengan pendaftaran Nomor Induk Berusaha (NIB) secara daring melalui sistem Online Single Submission Risk-Based Approach (OSS-RBA). NIB kini berlaku sebagai identitas legal tunggal, Tanda Daftar Perusahaan (TDP), dan Angka Pengenal Impor/Ekspor (API).",
        "keyPoints": [
            "BUMDes memiliki legalitas badan hukum setara perseroan terbatas setelah terdaftar di Kemendes",
            "NIB di OSS-RBA secara otomatis berfungsi sebagai identitas kepabeanan ekspor-impor",
            "Pilih Klasifikasi Baku Lapangan Usaha Indonesia (KBLI) 5 digit yang tepat untuk kegiatan perdagangan ekspor"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-NIB-02",
        "moduleId": "EDU-DES-NIB-04",
        "title": "Pendaftaran KBLI Perdagangan Ekspor & Fasilitas Pembebasan Bea Masuk UMK",
        "duration": "7 min",
        "kind": "Reading",
        "completed": False,
        "content": "Pelaku usaha desa wajib memilih KBLI perdagangan besar atau ekspor sesuai komoditasnya (contoh: KBLI 46201 untuk perdagangan besar hasil pertanian, 46311 untuk kopi/teh/kakao). Berdasarkan Permendag 16/2025 dan kebijakan Kementerian Keuangan, pelaku UMK desa berhak mendapatkan fasilitas Kemudahan Impor Tujuan Ekspor (KITE IKM), pembebasan bea masuk bahan baku penolong, serta asistensi klinik ekspor Bea Cukai.",
        "keyPoints": [
            "KBLI 5 digit menentukan izin teknis dan rekomendasi kementerian terkait",
            "Fasilitas KITE IKM memberikan pembebasan bea masuk dan PPN tidak dipungut untuk bahan baku olahan ekspor",
            "Manfaatkan fasilitas pembiayaan modal kerja ekspor berbunga rendah dari LPEI (Indonesia Eximbank)"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-NIB-03",
        "moduleId": "EDU-DES-NIB-04",
        "title": "Tata Kelola Keuangan Ekspor & Pembayaran L/C untuk Koperasi Desa",
        "duration": "6 min",
        "kind": "Video",
        "videoUrl": "https://www.youtube.com/watch?v=3-1hUZ6EZn0",
        "completed": False,
        "content": "Manajemen keuangan ekspor bagi BUMDes dan koperasi tani: 1) Pemilihan metode pembayaran aman: Irrevocable Letter of Credit (L/C) at Sight untuk buyer baru, atau Telegraphic Transfer (T/T) dengan uang muka minimal 30–50%; 2) Hindari skema Open Account untuk pembeli perdana tanpa penjaminan asuransi ekspor (seperti Asuransi Pembayaran Askrindo/LPEI); 3) Pisahkan rekening kas operasional BUMDes dengan rekening transaksi ekspor valas.",
        "keyPoints": [
            "Letter of Credit (L/C) at sight menjamin pembayaran dari bank pembeli setelah dokumen pengapalan valid",
            "Mitigasi risiko gagal bayar pembeli luar negeri dengan asuransi piutang dagang ekspor LPEI",
            "Tertib pembukuan keuangan desa memperkuat kelayakan kredit perbankan nasional"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-NIB-04",
        "moduleId": "EDU-DES-NIB-04",
        "title": "Kuis Evaluasi: Legalitas Usaha & Fasilitas Ekspor Desa",
        "duration": "4 min",
        "kind": "Quiz",
        "completed": False,
        "content": "Uji penguasaan Anda mengenai status badan hukum BUMDes, fungsi NIB OSS-RBA, dan tata kelola pembayaran ekspor internasional.",
        "keyPoints": [
            "Kuis 3 pertanyaan pilihan ganda",
            "Mencakup kedudukan hukum BUMDes, sistem OSS-RBA, dan instrumen pembayaran L/C",
            "Evaluasi skor dan ulasan jawaban benar"
        ],
        "quizQuestions": [
            {
                "id": "QZ-NIB-1",
                "question": "Berdasarkan regulasi terkini di Indonesia, apakah kedudukan hukum resmi Badan Usaha Milik Desa (BUMDes)?",
                "options": [
                    "Bukan badan hukum, hanya unit informal desa",
                    "Resmi berkedudukan sebagai Badan Hukum mandiri setelah mendapatkan sertifikat dari kementerian terkait",
                    "Hanya bagian dari kepanitiaan pemilihan kepala desa",
                    "Organisasi sosial kemasyarakatan tanpa hak berbisnis"
                ],
                "correctIndex": 1,
                "explanation": "UU Cipta Kerja dan PP 11/2021 menegaskan bahwa BUMDes dan BUMDes Bersama adalah badan hukum mandiri yang berhak mengadakan kontrak bisnis internasional dan membuka rekening perbankan ekspor."
            },
            {
                "id": "QZ-NIB-2",
                "question": "Apakah fungsi utama Nomor Induk Berusaha (NIB) yang diterbitkan melalui portal OSS-RBA bagi eksportir pemula?",
                "options": [
                    "Hanya tanda bukti bayar pajak kendaraan bermotor",
                    "Berfungsi sebagai identitas berusaha tunggal sekaligus hak akses kepabeanan ekspor (Angka Pengenal Impor/Ekspor)",
                    "Sebagai tiket masuk pelabuhan bongkar muat",
                    "Kartu identitas pegawai BUMDes"
                ],
                "correctIndex": 1,
                "explanation": "Sistem OSS-RBA mengintegrasikan berbagai perizinan, di mana satu nomor NIB otomatis berlaku sebagai identitas legalitas, TDP, dan identitas kepabeanan untuk aktivitas ekspor-impor."
            },
            {
                "id": "QZ-NIB-3",
                "question": "Metode pembayaran perdagangan internasional manakah yang memberikan kepastian jaminan bayar tertinggi dari bank pembeli bagi eksportir desa?",
                "options": [
                    "Open Account (bayar belakangan setelah barang laku)",
                    "Konsinyasi titip jual",
                    "Irrevocable Letter of Credit (L/C) at Sight",
                    "Cek tunai lewat pos surat"
                ],
                "correctIndex": 2,
                "explanation": "Irrevocable L/C at sight memberikan komitmen tanpa syarat dari bank penerbit (issuing bank) untuk membayar eksportir segera setelah dokumen pengapalan yang sah dan sesuai syarat L/C diserahkan."
            }
        ],
    },
    # --- Alias Lessons untuk kompatibilitas seeder desa ---
    {
        "id": "LSN-DES-PANEN-01",
        "moduleId": "EDU-DES-PANEN-01",
        "title": "Kenali komoditas & hama karantina",
        "duration": "5 min",
        "kind": "Video",
        "videoUrl": "https://www.youtube.com/watch?v=JnMtuZTjV6Q",
        "video_url": "https://www.youtube.com/watch?v=JnMtuZTjV6Q",
        "completed": False,
        "content": "Hasil panen segar wajib melewati karantina pertanian. Kenali media pembawa, hama penyakit, dan syarat phytosanitary negara tujuan.",
        "keyPoints": [
            "Identifikasi jenis komoditas & hama",
            "Karantina pertanian menerbitkan phytosanitary",
            "Sampel & pemeriksaan lapangan"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-DES-HALAL-01",
        "moduleId": "EDU-DES-HALAL-02",
        "title": "Bahan & proses produksi halal",
        "duration": "5 min",
        "kind": "Video",
        "videoUrl": "https://www.youtube.com/watch?v=UaPPWKAYj7E",
        "video_url": "https://www.youtube.com/watch?v=UaPPWKAYj7E",
        "completed": False,
        "content": "Sertifikasi halal menilai bahan, pemasok, dan proses produksi (PPH). Pahami requirement negara tujuan seperti GAC/SMAS di Timur Tengah.",
        "keyPoints": [
            "Kumpulkan daftar bahan & pemasok",
            "Amankan proses produksi halal",
            "Cek requirement negara tujuan"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-DES-NIB-01",
        "moduleId": "EDU-DES-NIB-04",
        "title": "Registrasi OSS-RBA & KBLI",
        "duration": "5 min",
        "kind": "Video",
        "videoUrl": "https://www.youtube.com/watch?v=3-1hUZ6EZn0",
        "video_url": "https://www.youtube.com/watch?v=3-1hUZ6EZn0",
        "completed": False,
        "content": "Urusan legalitas dasar: Nomor Induk Berusaha (NIB) dan IUMK lewat OSS-RBA, isi KBLI sesuai komoditas, dan fasilitas kepabeanan bagi UMK.",
        "keyPoints": [
            "Siapkan akta & NPWP",
            "Isi KBLI 5 digit",
            "Unduh NIB & IUMK"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-DES-KARANTINA-01",
        "moduleId": "EDU-DES-KARANTINA-06",
        "title": "PP 28/2024 & tindakan karantina",
        "duration": "5 min",
        "kind": "Video",
        "videoUrl": "https://www.youtube.com/watch?v=JnMtuZTjV6Q",
        "video_url": "https://www.youtube.com/watch?v=JnMtuZTjV6Q",
        "completed": False,
        "content": "Memahami PP 28/2024 tentang karantina hewan, ikan, dan tumbuhan: penggolongan media pembawa, wilayah karantina, dan tindakan P4/PK/PKHP.",
        "keyPoints": [
            "Golongan MHK/MKH/TIK",
            "Tindakan karantina P4/PK/PKHP",
            "Biaya & layanan cepat karantina"
        ],
        "quizQuestions": [],
    },

    # ── EDU-DES-DOC-05 ────────────────────────────────────────────────────────
    {
        "id": "LSN-DOC-01",
        "moduleId": "EDU-DES-DOC-05",
        "title": "Spesifikasi Dokumen Wajib Ekspor Pangan ke SFA Singapura & MAFF Jepang",
        "duration": "6 min",
        "kind": "Reading",
        "completed": False,
        "content": "Regulasi impor pangan segar di Singapura diawasi oleh Singapore Food Agency (SFA) berdasarkan Sale of Food Act, sedangkan di Jepang diatur oleh Ministry of Agriculture, Forestry and Fisheries (MAFF) dan MHLW. Dokumen inti meliputi: Phytosanitary Certificate Barantin, Health Certificate, Certificate of Origin (Form D / Form IJEPA), Certificate of Analysis (CoA) residu pestisida laboratorium terakreditasi ISO/IEC 17025, serta Commercial Invoice & Packing List bilingual.",
        "keyPoints": [
            "SFA Singapura mewajibkan registrasi establishment dan CoA batas residu pestisida",
            "Jepang menerapkan Positive List System untuk 800+ jenis bahan kimia pertanian",
            "Sertifikat Fitosanitari Barantin wajib diterbitkan maksimal 14 hari sebelum waktu muat kapal"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-DOC-02",
        "moduleId": "EDU-DES-DOC-05",
        "title": "Prosedur Pengurusan SKA Elektronik (e-Form D/IJEPA) & Health Certificate",
        "duration": "6 min",
        "kind": "Video",
        "videoUrl": "https://www.youtube.com/watch?v=C7VLuiVPIQM",
        "video_url": "https://www.youtube.com/watch?v=C7VLuiVPIQM",
        "completed": False,
        "content": "Pelajari alur pendaftaran dan penerbitan Surat Keterangan Asal (SKA) secara elektronik melalui sistem e-SKA Kementerian Perdagangan RI guna mengamankan tarif bea masuk preferensi 0% ke negara mitra dagang.",
        "keyPoints": [
            "Pendaftaran akun e-SKA menggunakan NIB berbasis risiko",
            "Kalkulasi Regional Value Content (RVC) minimal 40% untuk preferensi tarif ASEAN",
            "Pengiriman dokumen e-Form D terintegrasi melalui ASEAN Single Window (ASW)"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-DOC-03",
        "moduleId": "EDU-DES-DOC-05",
        "title": "Standar Uji Residu Laboratorium (CoA) & Traceability Lot Panen",
        "duration": "5 min",
        "kind": "Reading",
        "completed": False,
        "content": "Hasil uji Certificate of Analysis (CoA) wajib dikeluarkan oleh laboratorium uji pangan yang diakui Komite Akreditasi Nasional (KAN) berstandar ISO/IEC 17025. Data nomor lot panen, tanggal panen, nama kebun, dan jenis pestisida yang digunakan wajib identik dengan penandaan fisik pada tiap kemasan box ekspor.",
        "keyPoints": [
            "Laboratorium penguji wajib mengantongi akreditasi KAN ISO/IEC 17025",
            "Patuhi Maximum Residue Limit (MRL) spesifik negara tujuan",
            "Nomor batch pada CoA wajib tertelusur (traceable) ke catatan kebun petani"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-DOC-04",
        "moduleId": "EDU-DES-DOC-05",
        "title": "Kuis Evaluasi: Dokumen Ekspor Pertanian Singapura & Jepang",
        "duration": "4 min",
        "kind": "Quiz",
        "completed": False,
        "content": "Uji kompetensi Anda mengenai standardisasi dokumen pangan segar, pengurusan SKA elektronik, dan uji laboratorium residu pestisida.",
        "keyPoints": [
            "Kuis 3 pertanyaan pilihan ganda",
            "Mencakup otoritas SFA, batas RVC pada e-Form D, dan fungsi Certificate of Analysis",
            "Evaluasi skor dan kunci jawaban pembuktian dokumen"
        ],
        "quizQuestions": [
            {
                "id": "QZ-DOC-1",
                "question": "Otoritas manakah di Singapura yang bertindak sebagai pengawas gerbang impor produk pangan segar?",
                "options": [
                    "Maritime and Port Authority (MPA)",
                    "Singapore Food Agency (SFA)",
                    "Singapore Police Force",
                    "Civil Aviation Authority of Singapore"
                ],
                "correctIndex": 1,
                "explanation": "Singapore Food Agency (SFA) adalah otoritas tunggal di bawah Kementerian Keberlanjutan dan Lingkungan Hidup Singapura yang mengawasi keamanan pangan dan inspeksi impor produk pertanian."
            },
            {
                "id": "QZ-DOC-2",
                "question": "Berapakah batas ambang minimal Regional Value Content (RVC) agar komoditas berhak menikmati tarif 0% via skema SKA Form D (ATIGA)?",
                "options": [
                    "Minimal 10%",
                    "Minimal 25%",
                    "Minimal 40%",
                    "Wajib 100% tanpa kompromi"
                ],
                "correctIndex": 2,
                "explanation": "Skema ASEAN Trade in Goods Agreement (ATIGA) menetapkan aturan asal barang standar dengan nilai kandungan lokal ASEAN (Regional Value Content / RVC) minimal 40%."
            },
            {
                "id": "QZ-DOC-3",
                "question": "Mengapa nomor batch atau lot pada Certificate of Analysis (CoA) wajib dicocokkan dengan label kemasan produk?",
                "options": [
                    "Hanya untuk memenuhi warna desain kemasan",
                    "Sebagai syarat mutlak ketertelusuran (traceability) keamanan pangan apabila terjadi penarikan produk (recall)",
                    "Agar pengemudi truk ekspedisi tidak tersesat",
                    "Tidak ada pengaruhnya terhadap kepatuhan pabean"
                ],
                "correctIndex": 1,
                "explanation": "Otoritas karantina dan pangan internasional mewajibkan traceability penuh: nomor lot pada CoA membuktikan bahwa produk fisik yang dikirim adalah spesimen yang sama dengan yang diuji di laboratorium."
            }
        ],
    },

    # ── EDU-DES-KARANTINA-06 (Lanjutan) ───────────────────────────────────────
    {
        "id": "LSN-KARANTINA-02",
        "moduleId": "EDU-DES-KARANTINA-06",
        "title": "8 Tindakan Karantina (8P) & Kategori Media Pembawa OPTK",
        "duration": "6 min",
        "kind": "Reading",
        "completed": False,
        "content": "Peraturan Pemerintah No. 28 Tahun 2024 menyatukan mandat penyelenggaraan karantina hewan, ikan, dan tumbuhan ke dalam 8 Tindakan Karantina (8P): Pemeriksaan, Pengasingan, Pengamatan, Perlakuan, Penahanan, Penolakan, Pemusnahan, dan Pembebasan. Komoditas pertanian desa diklasifikasikan sebagai Media Pembawa Organisme Pengganggu Tumbuhan Karantina (OPTK) yang wajib steril dari tanah, gulma invasif, maupun larva serangga hidup.",
        "keyPoints": [
            "8 Tindakan Karantina (8P) dijalankan secara proporsional sesuai analisis risiko",
            "Larangan mutlak kontaminasi tanah liat/media tanam mentah pada produk segar",
            "Sertifikat Kesehatan Tumbuhan diterbitkan sebagai bukti tindakan pembebasan karantina"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-KARANTINA-03",
        "moduleId": "EDU-DES-KARANTINA-06",
        "title": "Fasilitas Periksa Lapangan di Tempat Produksi (In-Line Inspection)",
        "duration": "5 min",
        "kind": "Reading",
        "completed": False,
        "content": "Badan Karantina Indonesia menyediakan mekanisme pemeriksaan karantina di tempat produksi atau packing house desa (In-Line Inspection). Pejabat karantina meninjau SOP kebersihan, perlakuan pascapanen, dan sanitasi ruang kemas sebelum barang dikirim ke pelabuhan muat, sehingga mengeliminasi risiko penolakan kargo di dermaga ekspor.",
        "keyPoints": [
            "Pengajuan pemeriksaan karantina sebelum barang diberangkatkan dari desa",
            "Pemberian perlakuan teknis seperti pencucian, fumigasi, atau perlakuan panas terkendali",
            "Pengawalan kargo berpendingin berstatus segel karantina menuju pelabuhan laut/udara"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-KARANTINA-04",
        "moduleId": "EDU-DES-KARANTINA-06",
        "title": "Kuis Evaluasi: Regulasi Karantina Pertanian PP 28/2024",
        "duration": "4 min",
        "kind": "Quiz",
        "completed": False,
        "content": "Uji pemahaman Anda mengenai prinsip 8 Tindakan Karantina, mitigasi risiko OPTK, dan fasilitas In-Line Inspection Barantin.",
        "keyPoints": [
            "Kuis 3 pertanyaan pilihan ganda",
            "Membahas integrasi Barantin, tindakan perlakuan karantina, dan keuntungan inspeksi di desa",
            "Skor langsung dan evaluasi pembahasan resmi"
        ],
        "quizQuestions": [
            {
                "id": "QZ-KARANTINA-1",
                "question": "Apa peran strategis pembentukan Badan Karantina Indonesia (Barantin) menurut PP 28/2024?",
                "options": [
                    "Menetapkan tarif pajak penghasilan badan",
                    "Mengintegrasikan seluruh fungsi karantina hewan, ikan, dan tumbuhan ke dalam satu lembaga terpadu",
                    "Mengambil alih fungsi operasional kapal kargo niaga",
                    "Menyediakan bibit tanaman gratis bagi petani"
                ],
                "correctIndex": 1,
                "explanation": "PP 28/2024 menyatukan otoritas karantina pertanian dan perikanan ke bawah Badan Karantina Indonesia (Barantin) sebagai institusi karantina satu pintu nasional."
            },
            {
                "id": "QZ-KARANTINA-2",
                "question": "Manakah tindakan karantina yang diterapkan bila kargo buah ditemukan membawa serangga hidup namun jenisnya masih dapat dibasmi?",
                "options": [
                    "Pemusnahan seketika di tempat",
                    "Tindakan Perlakuan (Treatment), seperti fumigasi atau perlakuan uap panas (Vapour Heat Treatment)",
                    "Dibiarkan lolos tanpa tindakan",
                    "Denda tunai tanpa pembersihan hama"
                ],
                "correctIndex": 1,
                "explanation": "Tindakan Perlakuan (Treatment) dilakukan untuk mengeliminasi hama penyakit target tanpa merusak mutu fisik komoditas, sebelum sertifikat karantina diterbitkan."
            },
            {
                "id": "QZ-KARANTINA-3",
                "question": "Apa manfaat utama skema In-Line Inspection bagi pelaku usaha desa?",
                "options": [
                    "Bebas dari seluruh pemeriksaan bea cukai",
                    "Pemeriksaan dan sertifikasi dilakukan di packing house desa sehingga mencegah risiko penahanan kontainer di pelabuhan",
                    "Ongkos kirim kapal laut digratiskan oleh otoritas pabean",
                    "Komoditas tidak perlu dikemas dengan rapi"
                ],
                "correctIndex": 1,
                "explanation": "In-Line Inspection memastikan komoditas telah memenuhi standar sebelum kargo berangkat, meminimalkan demurrage kontainer dan pembongkaran ulang di pelabuhan."
            }
        ],
    },

    # ── EDU-DES-CITES-07 ──────────────────────────────────────────────────────
    {
        "id": "LSN-CITES-01",
        "moduleId": "EDU-DES-CITES-07",
        "title": "Verifikasi Legalitas Kayu SVLK & Sertifikasi Ekspor Kriya Alam",
        "duration": "5 min",
        "kind": "Video",
        "videoUrl": "https://www.youtube.com/watch?v=tK-V0wXk-V0",
        "video_url": "https://www.youtube.com/watch?v=tK-V0wXk-V0",
        "completed": False,
        "content": "Pelajari tata cara pemenuhan standar Sistem Verifikasi Kelestarian Kayu (SVLK) untuk produk kerajinan berbahan kayu, rotan, dan bambu desa serta rantai pasok lacak balak berkelanjutan.",
        "keyPoints": [
            "Pentingnya dokumen V-Legal untuk menembus pasar Eropa, AS, dan Australia",
            "Audit lacak balak (chain of custody) dari sumber bahan baku ke produk jadi",
            "Standar kemasan kayu palet ISPM 15 anti rayap dan serangga perusak kayu"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-CITES-02",
        "moduleId": "EDU-DES-CITES-07",
        "title": "Ketentuan Appendix CITES untuk Komoditas Kerajinan & Satwa/Tumbuhan",
        "duration": "6 min",
        "kind": "Reading",
        "completed": False,
        "content": "Konvensi Perdagangan Internasional Spesies Terancam Punah (CITES) mengatur lalu lintas flora dan fauna liar. Komoditas seperti kayu gaharu (Aquilaria), sonokeling (Dalbergia latifolia), ramin, serta kulit reptil budidaya masuk dalam Appendix II CITES. Ekspor komersial diperbolehkan namun wajib mengantongi kuota tangkap/panen dan Surat Angkut Tumbuhan dan Satwa Liar Luar Negeri (SATS-LN) dari Ditjen KSDAE Kementerian Lingkungan Hidup dan Kehutanan (KLHK).",
        "keyPoints": [
            "Appendix I mutlak dilarang untuk ekspor komersial",
            "Appendix II mewajibkan izin SATS-LN KLHK dan verifikasi kuota resmi",
            "Cantumkan nama ilmiah botani/zoologi pada invoice dan dokumen pengapalan"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-CITES-03",
        "moduleId": "EDU-DES-CITES-07",
        "title": "Deklarasi Kesesuaian Pemasok (DKP) bagi Pengrajin Kriya Desa",
        "duration": "5 min",
        "kind": "Reading",
        "completed": False,
        "content": "Untuk pengrajin mikro di desa yang mengolah kayu dari kebun rakyat atau hutan hak, pemerintah menyediakan skema Deklarasi Kesesuaian Pemasok (DKP). Pengrajin cukup mengisi formulir DKP yang melampirkan bukti kepemilikan pohon atau nota angkutan desa, yang kemudian dapat digunakan oleh eksportir mitra untuk menerbitkan Dokumen V-Legal tanpa beban biaya audit industri besar.",
        "keyPoints": [
            "DKP memberikan fasilitas kepatuhan legalitas yang ramah biaya bagi UMK desa",
            "Wajib dilengkapi surat kepemilikan pohon/tanah rakyat yang sah",
            "Menjadi dasar penerbitan Dokumen V-Legal kepabeanan oleh Lembaga Verifikasi"
        ],
        "quizQuestions": [],
    },
    {
        "id": "LSN-CITES-04",
        "moduleId": "EDU-DES-CITES-07",
        "title": "Kuis Evaluasi: Regulasi CITES & Legalitas Kayu SVLK",
        "duration": "4 min",
        "kind": "Quiz",
        "completed": False,
        "content": "Uji pengetahuan Anda mengenai klasifikasi Appendix CITES, penerbitan izin SATS-LN KLHK, dan dokumen legalitas kayu SVLK.",
        "keyPoints": [
            "Kuis 3 pertanyaan pilihan ganda",
            "Memvalidasi pemahaman Appendix II, dokumen SATS-LN, dan dokumen V-Legal",
            "Penjelasan kunci jawaban disertakan langsung"
        ],
        "quizQuestions": [
            {
                "id": "QZ-CITES-1",
                "question": "Pada kategori Appendix manakah flora/fauna yang terdaftar CITES boleh diperdagangkan secara komersial dengan izin ekspor khusus?",
                "options": [
                    "Appendix I",
                    "Appendix II",
                    "Appendix Nol",
                    "Tidak ada yang boleh diperdagangkan sama sekali"
                ],
                "correctIndex": 1,
                "explanation": "Spesies yang terdaftar dalam Appendix II CITES dapat diperdagangkan secara komersial selama memiliki kuota tangkap/panen yang berkelanjutan dan izin ekspor resmi (SATS-LN)."
            },
            {
                "id": "QZ-CITES-2",
                "question": "Dokumen apakah yang diterbitkan oleh KLHK sebagai izin resmi ekspor spesimen tumbuhan atau satwa liar yang diatur CITES?",
                "options": [
                    "Surat Izin Mengemudi Kapal (SIM-K)",
                    "Surat Angkut Tumbuhan dan Satwa Liar Luar Negeri (SATS-LN)",
                    "Kartu Tanda Penduduk Pengrajin",
                    "Kwitansi Belanja Pasar Tradisional"
                ],
                "correctIndex": 1,
                "explanation": "SATS-LN (Surat Angkut Tumbuhan dan Satwa Liar Luar Negeri) adalah dokumen izin ekspor resmi yang diterbitkan oleh Management Authority CITES di Indonesia (Ditjen KSDAE KLHK)."
            },
            {
                "id": "QZ-CITES-3",
                "question": "Apakah fungsi utama Dokumen V-Legal pada pengapalan ekspor kerajinan kayu Indonesia?",
                "options": [
                    "Memberikan diskon pajak pertambahan nilai bagi buyer",
                    "Membuktikan bahwa kayu dipanen dan diolah dari sumber legal yang terverifikasi secara sah sesuai standar SVLK",
                    "Sebagai pengganti asuransi kapal laut",
                    "Sebagai tanda lunas pembayaran kontainer"
                ],
                "correctIndex": 1,
                "explanation": "Dokumen V-Legal merupakan lisensi ekspor resmi yang membuktikan seluruh rantai pasok kayu memenuhi standar legalitas dan kelestarian (SVLK), diakui secara internasional seperti di Uni Eropa (FLEGT License)."
            }
        ],
    },
]

FULL_EDUCATIONAL_ARTICLES: list[dict[str, Any]] = [
    {
        "id": "ART-DES-HST-01",
        "moduleId": "EDU-DES-PANEN-01",
        "title": "Sertifikat Kesehatan Tumbuhan: Syarat Minimal & Cara Mengurus di Barantin",
        "status": "Published",
        "level": "Pemula",
        "readMinutes": 5,
        "tags": ["Karantina", "Pertanian", "PP 28/2024", "Barantin"],
        "summary": "Syarat dokumen minimal dan alur pengurusan Sertifikat Kesehatan Tumbuhan (KT-1) untuk hasil kebun desa.",
        "body": "Sertifikat Kesehatan Tumbuhan (KT-1 / Phytosanitary Certificate) diterbitkan oleh Badan Karantina Indonesia berdasarkan UU 21/2019 dan PP 28/2024. Dokumen yang disiapkan: surat permohonan pemeriksaan karantina, invoice, packing list, nama latin tanaman, volume muatan, negara tujuan, serta jadwal inspeksi sebelum kontainer ditutup.",
    },
    {
        "id": "ART-DES-NIB-02",
        "moduleId": "EDU-DES-NIB-04",
        "title": "NIB vs IUMK: Panduan Akses Legalitas dan Fasilitas Ekspor BUMDes",
        "status": "Published",
        "level": "Pemula",
        "readMinutes": 4,
        "tags": ["NIB", "IUMK", "BUMDes", "OSS-RBA"],
        "summary": "Perbedaan NIB dan IUMK, urutan registrasi OSS-RBA, dan fasilitas pembebasan bea masuk bagi UMK desa.",
        "body": "NIB menjadi identitas tunggal pelaku usaha di OSS-RBA dan syarat awal seluruh perizinan kepabeanan. IUMK menegaskan skala usaha mikro/kecil agar berhak mendapatkan fasilitas: pembebasan bea masuk impor mesin olahan (API UM), asistensi ekspor, hingga fasilitas Permendag 16/2025.",
    },
    {
        "id": "ART-DES-KEMAS-03",
        "moduleId": "EDU-DES-KEMAS-03",
        "title": "5 Kesalahan Pengemasan Kriya Rotan yang Menyebabkan Klaim Asuransi Ditolak",
        "status": "Published",
        "level": "Menengah",
        "readMinutes": 6,
        "tags": ["Kriya", "Pengemasan", "Asuransi", "ISPM 15"],
        "summary": "Kesalahan umum packing kriya rotan & kayu dan cara mendokumentasikan foto pre-loading agar klaim asuransi cair.",
        "body": "Kesalahan paling fatal: karton tanpa corner protector, tidak ada container desiccant kalsium klorida, palet kayu belum stempel ISPM 15, tiada foto kontainer kosong sebelum muat, dan deskripsi koli di B/L tidak cocok dengan packing list. Terapkan 5 SOP foto wajib sebelum pintu kontainer disegel.",
    },
    {
        "id": "ART-EUDR-GEO-04",
        "moduleId": "EDU-COMPLIANCE",
        "title": "Panduan Pemetaan Koordinat Poligon Kebun Kopi untuk Kepatuhan EUDR 2026",
        "status": "Published",
        "level": "Menengah",
        "readMinutes": 7,
        "tags": ["EUDR", "Kopi", "Geolokasi", "Uni Eropa"],
        "summary": "Langkah praktis petani desa memetakan batas poligon kebun menggunakan GPS ponsel untuk penerbitan Due Diligence Statement.",
        "body": "Regulasi EUDR menetapkan bahwa pengiriman kopi dan kakao ke 27 negara anggota Uni Eropa wajib menyertakan koordinat GPS poligon untuk kebun seluas 4 hektare ke atas. Petani desa dapat menggunakan aplikasi pemetaan terbuka berstandar WGS84 untuk mencatat titik koordinat batas kebun sebelum menyerahkannya ke koperasi atau eksportir mitra.",
    },
    {
        "id": "ART-DHE-PP21-05",
        "moduleId": "EDU-TARIFFS-2026",
        "title": "Implementasi Praktis DHE SDA PP 21/2026 bagi Eksportir Hasil Tambang & Kebun",
        "status": "Published",
        "level": "Lanjutan",
        "readMinutes": 6,
        "tags": ["DHE SDA", "PP 21/2026", "Bank Himbara", "Keuangan"],
        "summary": "Tata cara teknis penempatan devisa 100% 12 bulan di bank devisa Himbara dan mitigasi risiko blokir sistem CEISA.",
        "body": "Mulai 1 Juni 2026 berdasarkan PP 21/2026, nilai ekspor SDA minimal USD 250.000 wajib masuk ke Rekening Khusus di bank devisa Himbara. Eksportir dapat memilih instrumen Term Deposit Valas Bank Indonesia dengan tarif PPh bunga deposito final 0% untuk tenor di atas 6 bulan, sekaligus menjaga kepatuhan agar nomor identitas kepabeanan (NIB) tidak dibekukan di portal INSW.",
    },
]
