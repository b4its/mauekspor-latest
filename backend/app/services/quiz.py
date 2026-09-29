"""Bank soal kuis edukasi yang menyesuaikan topik & materi tiap modul.

Setiap modul pembelajaran (educational module) mendapat kuis dengan soal yang
relevan dengan topiknya — dibaca dari judul, ringkasan, dan judul/isi pelajaran
modul tersebut. Modul dikelompokkan ke *topic* (kesiapan ekspor, kepatuhan,
costing, pengemasan, bea cukai, dokumen, pembeli, pengiriman, dll.) lalu setiap
topic menyumbang sekumpulan soal pilihan ganda beserta penjelasan jawaban.

Modul yang topiknya tidak terdeteksi tetap mendapat kuis "umum" yang mengacu
pada istilah inti ekspor, sehingga **setiap** modul selalu punya kuis.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

# Topic → daftar soal. Format tiap soal:
#   {"question": str, "options": [4 opsi], "answer": int (indeks opsi benar),
#    "explanation": str}
# Indeks jawaban selalu 0 di sumber ini; fungsi `_rotate` akan mengacaknya
# secara deterministik per modul agar posisi jawaban tidak selalu "A".
_TOPIC_BANK: dict[str, list[dict[str, Any]]] = {
    "readiness": [
        {
            "question": "Apa langkah paling awal sebelum mengajukan penawaran ekspor?",
            "options": [
                "Memastikan data produk (spesifikasi, berat, dimensi) lengkap dan terstruktur",
                "Langsung mengirim barang tanpa dokumen",
                "Menetapkan harga jual tanpa menghitung biaya",
                "Menunggu pembeli menghubungi terlebih dahulu",
            ],
            "explanation": "Kesiapan ekspor dimulai dari data produk yang lengkap dan konsisten; semua alur berikutnya bergantung pada data ini.",
        },
        {
            "question": "Mengapa berat bersih (net) dan berat kotor (gross) harus dicatat terpisah?",
            "options": [
                "Karena keduanya dipakai untuk dokumen, ongkos kirim, dan klasifikasi",
                "Karena hanya berat kotor yang diperbolehkan",
                "Karena berat bersih tidak pernah dipakai di ekspor",
                "Karena keduanya selalu bernilai sama",
            ],
            "explanation": "Berat net (isi produk) dan gross (termasuk kemasan) dipakai pada packing list, perhitungan freight, dan kepabeanan.",
        },
        {
            "question": "Apa yang dimaksud dengan produk 'export-ready'?",
            "options": [
                "Produk dengan data, kemasan, dan sertifikat yang memenuhi syarat pasar tujuan",
                "Produk yang sudah pernah dikirim tanpa dokumen",
                "Produk dengan harga termurah di pasar",
                "Produk yang belum punya spesifikasi apa pun",
            ],
            "explanation": "Export-ready berarti kelengkapan data, kemasan, dan dokumen sudah sesuai persyaratan pasar tujuan.",
        },
        {
            "question": "Kapan sebaiknya sertifikat dilampirkan pada data produk?",
            "options": [
                "Sebelum meminta analisis pasar dan menyusun penawaran",
                "Setelah barang tiba di negara tujuan",
                "Setelah pembeli komplain",
                "Tidak perlu dilampirkan sama sekali",
            ],
            "explanation": "Sertifikat yang dilampirkan lebih awal mencegah penundaan penawaran dan analisis pasar.",
        },
    ],
    "compliance": [
        {
            "question": "Berapa digit kode HS pada tingkat global (Harmonized System)?",
            "options": [
                "6 digit, lalu diperluas oleh otoritas pabean masing-masing negara",
                "2 digit saja",
                "10 digit di semua negara",
                "Tidak ada standar digit",
            ],
            "explanation": "HS global terdiri dari 6 digit; tiap negara memperluasnya (mis. 8–10 digit) untuk tarif lokal.",
        },
        {
            "question": "Apa yang harus dilakukan terhadap kode HS yang disarankan AI sebelum dipakai?",
            "options": [
                "Dikonfirmasi oleh manusia karena berpengaruh pada perhitungan bea",
                "Langsung dipakai tanpa perlu dikonfirmasi",
                "Diabaikan karena selalu salah",
                "Diganti dengan kode dari kompetitor",
            ],
            "explanation": "Saran HS dari AI bersifat indikatif; kesalahan klasifikasi berisiko denda/perhitungan bea yang salah, jadi perlu konfirmasi.",
        },
        {
            "question": "Bagaimana hubungan antara persyaratan kepatuhan dan bukti (evidence)?",
            "options": [
                "Satu persyaratan idealnya dipetakan ke satu artefak bukti yang jelas",
                "Satu bukti cukup untuk semua persyaratan di semua pasar",
                "Bukti tidak diperlukan bila pemilik barang yakin",
                "Bukti hanya formalitas tanpa dampak",
            ],
            "explanation": "Bukti yang jelas dan spesifik per persyaratan menjaga kepercayaan dan skor kepatuhan.",
        },
        {
            "question": "Apa syarat agar tarif preferensial (mis. FTA/EPA) dapat digunakan?",
            "options": [
                "Harus ada bukti asal barang (rules of origin) yang sah dan sesuai format perjanjian",
                "Cukup mengisi harga barang yang lebih rendah",
                "Cukup mengirim barang dari negara mana saja",
                "Tidak ada syarat dokumen",
            ],
            "explanation": "Tarif preferensial hanya berlaku bila bukti asal barang memenuhi aturan asal perjanjian dagang terkait.",
        },
    ],
    "costing": [
        {
            "question": "Apa perbedaan inti antara Incoterms EXW dan DAP?",
            "options": [
                "EXW menyerahkan hampir seluruh biaya/risiko ke pembeli, DAP ke penjual",
                "Keduanya sama saja",
                "EXW mewajibkan penjual menanggung ongkos kirim sampai tujuan",
                "DAP berarti barang diambil di gudang penjual",
            ],
            "explanation": "EXW: pembeli menanggung hampir semua biaya/risiko. DAP: penjual menanggung pengiriman hingga lokasi tujuan.",
        },
        {
            "question": "Komponen apa saja yang termasuk dalam landed cost?",
            "options": [
                "Harga produk, penanganan asal, freight, asuransi, bea, dan biaya tujuan",
                "Hanya harga produk saja",
                "Hanya biaya freight",
                "Hanya harga produk dan diskon pembeli",
            ],
            "explanation": "Landed cost menggabungkan seluruh biaya sampai barang tiba di tujuan, dihitung per unit.",
        },
        {
            "question": "Mengapa perlu buffer nilai tukar (FX) dalam penawaran?",
            "options": [
                "Karena pergerakan kurs antara penawaran dan pembayaran dapat menggerus margin",
                "Karena kurs selalu tetap sepanjang tahun",
                "Karena pembeli menanggung seluruh selisih kurs",
                "Karena FX tidak berpengaruh pada margin",
            ],
            "explanation": "Perubahan kurs selama jeda penawaran-pembayaran memengaruhi margin aktual, sehingga buffer FX melindungi profit.",
        },
        {
            "question": "Saat meninjau margin penawaran, harga sebaiknya dibandingkan terhadap apa?",
            "options": [
                "Landed cost, bukan hanya harga pokok produk",
                "Harga pesaing saja",
                "Harga produk saja",
                "Keinginan pembeli saja",
            ],
            "explanation": "Membandingkan dengan landed cost mencegah penawaran yang tampak untung tetapi sebenarnya tipis.",
        },
    ],
    "packaging": [
        {
            "question": "Apa fungsi utama standar pengemasan ekspor?",
            "options": [
                "Melindungi produk selama pengiriman internasional dan memenuhi syarat pasar",
                "Hanya memperindah tampilan produk",
                "Menambah berat tanpa manfaat",
                "Menghindari penggunaan label",
            ],
            "explanation": "Kemasan ekspor melindungi produk dari risiko perjalanan panjang sekaligus memenuhi regulasi pelabelan.",
        },
        {
            "question": "Mengapa informasi kemasan perlu dicatat pada data produk?",
            "options": [
                "Karena berpengaruh pada berat, volume, dan perhitungan biaya kirim",
                "Karena kemasan tidak pernah dihitung",
                "Karena kemasan hanya urusan pembeli",
                "Karena kemasan tidak memengaruhi dokumen",
            ],
            "explanation": "Dimensi dan material kemasan memengaruhi berat, volume, dan biaya logistik serta pengisian dokumen.",
        },
    ],
    "customs": [
        {
            "question": "Apa peran utama customs clearance (pengurusan kepabeanan)?",
            "options": [
                "Memastikan barang memenuhi syarat masuk/keluar negara dan kewajiban bea terpenuhi",
                "Mengemas ulang barang di pelabuhan",
                "Menentukan harga jual pembeli",
                "Menghapus kebutuhan dokumen",
            ],
            "explanation": "Customs clearance memastikan barang legal melintasi perbatasan dan kewajiban bea/pajak dipenuhi.",
        },
        {
            "question": "Dokumen apa yang biasanya menjadi tulang punggung pengurusan kepabeanan?",
            "options": [
                "Commercial invoice, packing list, dan dokumen asal barang",
                "Hanya kartu nama penjual",
                "Hanya foto produk",
                "Tanpa dokumen apa pun",
            ],
            "explanation": "Invoice, packing list, dan sertifikat asal adalah dokumen inti yang harus konsisten satu sama lain.",
        },
    ],
    "documents": [
        {
            "question": "Mengapa kuantitas pada invoice harus cocok dengan packing list?",
            "options": [
                "Ketidaksesuaian adalah penyebab umum dokumen ditolak saat kepabeanan",
                "Karena invoice tidak pernah diperiksa",
                "Karena packing list bersifat opsional",
                "Karena keduanya tidak berhubungan",
            ],
            "explanation": "Invoice dan packing list harus rekonsiliasi; selisih kuantitas memicu penolakan atau pemeriksaan tambahan.",
        },
        {
            "question": "Kode HS pada invoice sebaiknya mengacu ke apa?",
            "options": [
                "Hasil analisis ekspor / klasifikasi resmi yang telah dikonfirmasi",
                "Tebakan acak tanpa dasar",
                "Kode milik produk lain yang mirip",
                "Kode dari negara yang tidak berhubungan",
            ],
            "explanation": "Kode HS pada invoice harus konsisten dengan analisis ekspor agar tidak terjadi selisih dengan kepabeanan.",
        },
    ],
    "buyers": [
        {
            "question": "Kapan sebaiknya kualifikasi pembeli dilakukan?",
            "options": [
                "Sebelum menginvestasikan waktu pada penawaran lengkap",
                "Setelah barang dikirim",
                "Setelah kontrak dibatalkan",
                "Kualifikasi tidak diperlukan",
            ],
            "explanation": "Kualifikasi lebih awal menghemat waktu dan sumber daya dari prospek yang tidak serius.",
        },
        {
            "question": "Apa fungsi tahapan pembeli (Lead, Qualified, Active, Churned)?",
            "options": [
                "Memprioritaskan pipeline penjualan dan tindak lanjut",
                "Mengganti dokumen ekspor",
                "Menentukan kurs mata uang",
                "Menghitung bea masuk",
            ],
            "explanation": "Tahapan membantu memprioritaskan prospek dan mengukur kesehatan pipeline penjualan.",
        },
    ],
    "shipping": [
        {
            "question": "Faktor apa yang penting diperhatikan saat memilih forwarder?",
            "options": [
                "Cakupan jalur (lane), tingkat on-time, dan kecepatan penawaran",
                "Warna logo perusahaan",
                "Jumlah karyawan saja",
                "Harga termurah tanpa mempertimbangkan layanan",
            ],
            "explanation": "Lane coverage, on-time rate, dan kecepatan quoting menentukan keandalan pengiriman.",
        },
        {
            "question": "Mengapa tarif freight perlu di-quote ulang bila masa berlaku habis?",
            "options": [
                "Karena tarif freight fluktuatif mengikuti musim dan ketersediaan",
                "Karena tarif freight selalu tetap",
                "Karena forwarder tidak pernah berubah harga",
                "Karena asuransi menanggung selisihnya",
            ],
            "explanation": "Tarif freight berubah mengikuti musim dan kapasitas; kutipan kedaluwarsa bisa membuat estimasi biaya meleset.",
        },
    ],
    "quarantine": [
        {
            "question": "Sertifikat apa yang wajib untuk ekspor hasil panen segar (tumbuhan)?",
            "options": [
                "Sertifikat Kesehatan Tumbuhan (Phytosanitary) dari Badan Karantina Pertanian",
                "Kartu anggota koperasi",
                "Surat izin mengemudi",
                "Bukti pembayaran listrik",
            ],
            "explanation": "Hasil panen segar wajib disertai Phytosanitary/ Sertifikat Kesehatan Tumbuhan dari karantina pertanian.",
        },
        {
            "question": "Kapan pemeriksaan karantina sebaiknya dilakukan?",
            "options": [
                "Di tempat penimbunan sebelum kontainer ditutup",
                "Setelah barang tiba di negara tujuan",
                "Setelah pembeli menerima barang",
                "Tidak perlu diperiksa",
            ],
            "explanation": "Pemeriksaan karantina dilakukan sebelum kontainer ditutup agar sertifikat dapat diterbitkan.",
        },
        {
            "question": "Data apa yang perlu disiapkan saat mengajukan pengurusan karantina?",
            "options": [
                "Nama latin komoditas, volume, kemasan, dan negara tujuan",
                "Hanya nomor telepon sopir",
                "Hanya warna kemasan",
                "Tidak ada data yang diperlukan",
            ],
            "explanation": "Pengajuan karantina membutuhkan data komoditas, volume, kemasan, dan negara tujuan secara lengkap.",
        },
    ],
    "halal": [
        {
            "question": "Apa yang dinilai dalam sertifikasi halal suatu produk?",
            "options": [
                "Bahan, pemasok, dan proses produksi yang sesuai ketentuan halal",
                "Warna kemasan saja",
                "Harga jual produk",
                "Jumlah karyawan",
            ],
            "explanation": "Sertifikasi halal menilai keseluruhan rantai bahan dan proses produksi (sistem jaminan halal).",
        },
        {
            "question": "Mengapa requirement negara tujuan penting dalam sertifikasi halal?",
            "options": [
                "Karena tiap negara punya standar/label halal yang diakui berbeda",
                "Karena semua negara punya aturan halal yang sama persis",
                "Karena sertifikat halal tidak diakui di luar negeri",
                "Karena halal hanya urusan lokal",
            ],
            "explanation": "Negara tujuan seperti di Timur Tengah memiliki skema pengakuan (mis. GAC/SMAS) yang perlu dipenuhi.",
        },
    ],
    "licensing": [
        {
            "question": "Apa fungsi NIB (Nomor Induk Berusaha) bagi pelaku usaha?",
            "options": [
                "Identitas pelaku usaha di OSS-RBA dan pintu masuk perizinan lainnya",
                "Nomor telepon resmi perusahaan",
                "Kode kelas barang",
                "Nomor rekening bank",
            ],
            "explanation": "NIB adalah identitas usaha di OSS-RBA yang menjadi dasar pengurusan perizinan lainnya.",
        },
        {
            "question": "Apa peran IUMK bagi usaha mikro dan kecil?",
            "options": [
                "Menegaskan skala usaha agar memenuhi syarat fasilitas ekspor (mis. pembebasan tertentu)",
                "Menggantikan fungsi NIB",
                "Menggantikan NPWP",
                "Menentukan kurs mata uang",
            ],
            "explanation": "IUMK menegaskan skala usaha mikro/kecil sehingga dapat mengakses fasilitas kepabeanan bagi UMK.",
        },
        {
            "question": "Apa yang perlu disiapkan sebelum registrasi OSS-RBA?",
            "options": [
                "Akta badan usaha/koperasi dan NPWP",
                "Hanya foto produk",
                "Hanya nomor HP",
                "Tidak ada dokumen",
            ],
            "explanation": "Registrasi OSS-RBA membutuhkan akta badan usaha dan NPWP sebagai data dasar.",
        },
    ],
    "cites": [
        {
            "question": "Apa yang perlu dipastikan terkait CITES saat mengekspor kriya bahan alam?",
            "options": [
                "Bahan bukan berasal dari spesies dilindungi (cek appendix CITES)",
                "Semua bahan alam otomatis bebas CITES",
                "CITES hanya berlaku untuk produk makanan",
                "CITES tidak perlu diperiksa",
            ],
            "explanation": "Kriya dari kayu/rotan/bahan alam harus dipastikan bukan spesies dilindungi CITES (periksa appendix).",
        },
        {
            "question": "Dokumen apa yang mendukung legalitas bahan baku kayu/rotan?",
            "options": [
                "Dokumen legalitas kayu (mis. SVLK) dan asal-usul bahan",
                "Hanya faktur pembelian tanpa legalitas",
                "Hanya foto produk",
                "Tidak ada dokumen",
            ],
            "explanation": "Legalitas bahan baku (SVLK) dan dokumen asal-usul menjadi bukti keabsahan bahan ekspor.",
        },
    ],
}

# Topic umum — dipakai bila topik modul tidak terdeteksi.
_GENERAL_BANK: list[dict[str, Any]] = [
    {
        "question": "Apa kode yang dipakai untuk mengklasifikasikan barang dalam perdagangan internasional?",
        "options": [
            "Kode HS (Harmonized System)",
            "Kode pos",
            "Kode area telepon",
            "Kode warna kemasan",
        ],
        "explanation": "Kode HS (Harmonized System) adalah standar klasifikasi barang untuk kepabeanan dan tarif.",
    },
    {
        "question": "Apa manfaat menyusun costing sebelum menawarkan harga ke pembeli?",
        "options": [
            "Harga yang ditawarkan mencerminkan seluruh biaya dan margin yang wajar",
            "Agar bisa menebak harga pesaing",
            "Agar tidak perlu memikirkan dokumen",
            "Agar barang cepat laku tanpa memperhitungkan biaya",
        ],
        "explanation": "Costing memastikan harga menutup semua biaya (produk, freight, bea) dan margin yang diinginkan.",
    },
    {
        "question": "Mengapa kepatuhan (compliance) penting dalam ekspor?",
        "options": [
            "Karena pelanggaran aturan pasar tujuan dapat menyebabkan barang ditahan atau ditolak",
            "Karena hanya formalitas administratif",
            "Karena tidak memengaruhi kelancaran pengiriman",
            "Karena hanya berlaku untuk eksportir besar",
        ],
        "explanation": "Ketidakpatuhan dapat menyebabkan penahanan, penolakan, atau denda di negara tujuan.",
    },
    {
        "question": "Dokumen apa yang umum mendampingi pengiriman ekspor?",
        "options": [
            "Commercial invoice, packing list, dan sertifikat asal barang",
            "Kartu nama dan brosur saja",
            "Hanya foto produk",
            "Tidak perlu dokumen",
        ],
        "explanation": "Invoice, packing list, dan sertifikat asal adalah dokumen dasar yang selalu dibutuhkan.",
    },
]


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


# Kata kunci per topic → memetakan konten modul ke topic di bank soal.
_TOPIC_KEYWORDS: dict[str, set[str]] = {
    "readiness": {"readiness", "ready", "foundation", "fundamentals", "persiapan", "kesiapan", "pemula"},
    "compliance": {"compliance", "kepatuhan", "regulasi", "regulation", "hs", "origin", "evidence"},
    "costing": {"costing", "cost", "biaya", "incoterms", "incoterm", "landed", "harga", "price", "pricing", "margin", "freight"},
    "packaging": {"packaging", "kemasan", "packing", "kriya", "kontainer", "rotan", "kayu"},
    "customs": {"customs", "clearance", "pabean", "bea", "cukai", "kepabeanan", "impor"},
    "documents": {"document", "documentation", "dokumen", "invoice", "packing", "bill", "lading", "coo", "sertifikat"},
    "buyers": {"buyer", "pembeli", "lead", "crm", "inquiry", "rfq", "quotation"},
    "shipping": {"shipping", "logistics", "logistik", "pengiriman", "forwarder", "shipment"},
    "quarantine": {"karantina", "phytosanitary", "panen", "pertanian", "tumbuhan", "hama", "skt", "kesehatan"},
    "halal": {"halal", "sihalal", "timur", "tengah", "smac", "pph", "syariah"},
    "licensing": {"nib", "iumk", "oss", "rbk", "osr", "kbli", "legalitas", "perizinan", "badan", "usaha", "bumdes"},
    "cites": {"cites", "spesies", "dilindungi", "appendix", "svlk", "bahan", "baku", "alam", "kehutanan"},
}


def _detect_topics(text: str) -> list[str]:
    """Kembalikan daftar topic (terurut dampak) yang cocok dengan teks modul."""
    tokens = _tokenize(text)
    scores: list[tuple[int, str]] = []
    for topic, keywords in _TOPIC_KEYWORDS.items():
        hits = len(tokens & keywords)
        if hits:
            scores.append((hits, topic))
    # Urutkan menurun berdasar jumlah kecocokan, lalu alfabetis agar deterministik.
    scores.sort(key=lambda s: (-s[0], s[1]))
    return [t for _, t in scores]


def _rotate(items: list[Any], offset: int) -> list[Any]:
    if not items:
        return items
    offset %= len(items)
    return items[offset:] + items[:offset]


def build_quiz(module: dict[str, Any], lessons: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Susun daftar soal kuis untuk sebuah modul.

    Soal diambil dari topic yang terdeteksi (judul + ringkasan + pelajaran),
    lalu dilengkapi dari bank umum bila topic belum memenuhi jumlah minimal.
    Posisi jawaban dirotasi deterministik berdasar id modul sehingga tidak
    selalu berada di indeks yang sama.
    """
    lessons = lessons or []
    haystack_parts = [
        str(module.get("title", "")),
        str(module.get("summary", "")),
        str(module.get("description", "")),
        str(module.get("level", "")),
    ]
    for lesson in lessons:
        haystack_parts.append(str(lesson.get("title", "")))
        haystack_parts.append(str(lesson.get("content", "")))
    haystack = " ".join(haystack_parts)

    topics = _detect_topics(haystack)

    questions: list[dict[str, Any]] = []
    for topic in topics:
        questions.extend(_TOPIC_BANK.get(topic, []))
    # Lengkapi dengan bank umum bila belum cukup 4 soal.
    if len(questions) < 4:
        questions.extend(_GENERAL_BANK)

    # Ambil maksimal 5 soal, tanpa duplikat pertanyaan.
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for q in questions:
        key = q["question"]
        if key in seen:
            continue
        seen.add(key)
        unique.append(q)
        if len(unique) >= 5:
            break

    # Rotasi opsi jawaban secara deterministik per modul (hash stabil, bukan
    # hash() bawaan yang diacak PYTHONHASHSEED sehingga berubah tiap restart).
    digest = hashlib.sha256(str(module.get("id", "")).encode("utf-8")).hexdigest()
    seed = int(digest[:8], 16) % 4
    out: list[dict[str, Any]] = []
    for i, q in enumerate(unique):
        offset = (seed + i) % len(q["options"])
        options = _rotate(list(q["options"]), offset)
        # Indeks benar semula 0; setelah rotasi maju `offset` posisi.
        answer = (0 - offset) % len(q["options"])
        out.append(
            {
                "id": f"{module.get('id', 'Q')}-Q{i + 1}",
                "question": q["question"],
                "options": options,
                "answer": answer,
                "explanation": q["explanation"],
            }
        )
    return out


def public_quiz(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Versi soal tanpa kunci jawaban, untuk dikirim ke klien."""
    return [
        {"id": q["id"], "question": q["question"], "options": q["options"]}
        for q in questions
    ]


def grade_quiz(questions: list[dict[str, Any]], answers: dict[str, int]) -> dict[str, Any]:
    """Nilai jawaban klien (map id→indeks opsi) terhadap kunci.

    Mengembalikan skor, jumlah benar/salah, kelulusan (≥70%), dan rincian
    per soal termasuk kunci + penjelasan untuk umpan balik.
    """
    details: list[dict[str, Any]] = []
    correct_count = 0
    for q in questions:
        chosen = answers.get(q["id"])
        is_correct = chosen == q["answer"]
        if is_correct:
            correct_count += 1
        details.append(
            {
                "id": q["id"],
                "question": q["question"],
                "options": q["options"],
                "chosen": chosen,
                "answer": q["answer"],
                "correct": is_correct,
                "explanation": q["explanation"],
            }
        )
    total = len(questions) or 1
    score = round((correct_count / total) * 100)
    return {
        "score": score,
        "correctCount": correct_count,
        "total": len(questions),
        "passed": score >= 70,
        "details": details,
    }
