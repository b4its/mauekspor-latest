"""Seeder komoditas desa MauEkspor.

Fokus demo pada komoditas desa Indonesia (bukan seluruh 6.941 kode HS):
- Chapter HS 01-24 : produk pertanian, peternakan, perikanan, perkebunan
- Chapter HS 46    : kerajinan anyaman (rotan/bambu)
- Chapter HS 68-70 : kerajinan tangan/kriya (batu semen/gips, keramik, kaca)

Mengisi database dengan kurasi komoditas desa: kopi, kakao, rempah,
vanili, manggis, kerajinan rotan, dan hasil hutan non-kayu (HHNK),
lengkap dengan penanda `is_village_priority` + `commodity_group`,
data desa fiktif (relasi produk -> desa), dan konten edukasi desa.
"""
from app import db
from app.core.security import hash_password

# Chapter HS yang relevan untuk komoditas desa:
# - 01-24 : pertanian, peternakan, perikanan, perkebunan
# - 46    : kerajinan anyaman (rotan/bambu) — kode resmi kerajinan rotan
# - 68-70 : kerajinan tangan/kriya (batu semen/gips, keramik, kaca)
VILLAGE_HS_CHAPTERS = set(range(1, 25)) | {46} | {68, 69, 70}


def commodity_group_for_chapter(chapter: int | str | None) -> str:
    """Petakan chapter HS ke kelompok komoditas (pertanian/perikanan/kerajinan)."""
    try:
        chapter = int(chapter)
    except (TypeError, ValueError):
        return "pertanian"
    if chapter == 3:
        return "perikanan"
    if chapter in {46, 68, 69, 70}:
        return "kerajinan"
    return "pertanian"


def chapter_of(hs_code: str) -> int | None:
    digits = "".join(ch for ch in str(hs_code or "") if ch.isdigit())
    if len(digits) < 2:
        return None
    return int(digits[:2])


def is_village_hs_code(hs_code: str) -> bool:
    """True jika kode HS termasuk chapter komoditas desa."""
    chapter = chapter_of(hs_code)
    return chapter is not None and chapter in VILLAGE_HS_CHAPTERS


def filter_village_hs_codes(codes: list[dict]) -> list[dict]:
    """Saring daftar record kode HS agar hanya chapter komoditas desa."""
    return [c for c in codes if is_village_hs_code(c.get("hs_code", ""))]


def village_flags(hs_code: str) -> dict:
    """Penanda master data: kolom pembeda data desa."""
    return {
        "is_village_priority": True,
        "commodity_group": commodity_group_for_chapter(chapter_of(hs_code)),
    }


# ---------------------------------------------------------------------------
# Data desa fiktif (demo) — direlasikan ke produk melalui `villageId`.
# Status kesiapan: >= 80 = "Siap Ekspor", sisanya "Butuh Pendampingan".
# ---------------------------------------------------------------------------
VILLAGE_DESA = [
    {"id": "DES-GAYO", "name": "Desa Kopi Gayo", "region": "Lut Tawar, Aceh Tengah", "province": "Aceh",
     "flagshipCommodity": "Kopi Arabika", "commodityGroup": "pertanian", "production": "8 ton green beans / bulan",
     "organization": "BUMDes Kopi Gayo Sejahtera", "readiness": 86},
    {"id": "DES-VANILI-BALI", "name": "Desa Vanili Bali", "region": "Tabanan", "province": "Bali",
     "flagshipCommodity": "Vanili Planifolia", "commodityGroup": "pertanian", "production": "50 kg curing / bulan",
     "organization": "Koperasi Vanili Bali Sejahtera", "readiness": 77},
    {"id": "DES-SITUBONDO", "name": "Desa Manggis Situbondo", "region": "Banyuputih, Situbondo", "province": "Jawa Timur",
     "flagshipCommodity": "Manggis Premium", "commodityGroup": "pertanian", "production": "600 kg / musim panen",
     "organization": "Gapoktan Manggis Lestari", "readiness": 68},
    {"id": "DES-TORAJA", "name": "Desa Kakao Toraja", "region": "Rantepao, Toraja Utara", "province": "Sulawesi Selatan",
     "flagshipCommodity": "Kakao Fermentasi", "commodityGroup": "pertanian", "production": "3 ton / bulan",
     "organization": "Koperasi Desa Kakao Toraja", "readiness": 81},
    {"id": "DES-KAHAYAN", "name": "Desa Rotan Kahayan", "region": "Pulang Pisau", "province": "Kalimantan Tengah",
     "flagshipCommodity": "Kerajinan Rotan", "commodityGroup": "kerajinan", "production": "200 pcs / bulan",
     "organization": "BUMDes Kriya Kahayan", "readiness": 72},
    {"id": "DES-SUMBAWA", "name": "Desa Madu Sumbawa", "region": "Dompu", "province": "Nusa Tenggara Barat",
     "flagshipCommodity": "Madu Hutan", "commodityGroup": "pertanian", "production": "480 jar / bulan",
     "organization": "Kelompok Panen Madu Hutan Sumbawa", "readiness": 84},
    {"id": "DES-TERNATE", "name": "Desa Cengkeh Ternate", "region": "Ternate", "province": "Maluku Utara",
     "flagshipCommodity": "Cengkeh Grade A", "commodityGroup": "pertanian", "production": "2 ton / musim",
     "organization": "Koperasi Cengkeh Ternate Makmur", "readiness": 75},
    {"id": "DES-MUNTOK", "name": "Desa Lada Putih Muntok", "region": "Bangka Barat", "province": "Kepulauan Bangka Belitung",
     "flagshipCommodity": "Lada Putih Muntok", "commodityGroup": "pertanian", "production": "1,5 ton / bulan",
     "organization": "BUMDes Lada Muntok Jaya", "readiness": 70},
    {"id": "DES-KERINCI", "name": "Desa Kayu Manis Kerinci", "region": "Kerinci", "province": "Jambi",
     "flagshipCommodity": "Kayu Manis (Kassia)", "commodityGroup": "pertanian", "production": "1 ton bale / bulan",
     "organization": "Koperasi Kayu Manis Kerinci", "readiness": 74},
]


def _desa_status(readiness: int) -> str:
    return "Siap Ekspor" if readiness >= 80 else "Butuh Pendampingan"


# ---------------------------------------------------------------------------
# Kurasi produk komoditas unggulan desa.
# Setiap produk wajib punya berat (kg) & dimensi (cm) + relasi desa.
# ---------------------------------------------------------------------------
VILLAGE_PRODUCTS = [
    {
        "id": "PRD-DES-KOPI-001", "name": "Kopi Arabika Gayo Green Beans", "category": "Perkebunan",
        "status": "Enriched", "hs": "09011100", "origin": "Desa Kopi Gayo, Aceh Tengah",
        "packaging": "Grain pro liner 30 kg atau kantong 1 kg", "netWeightKg": 1, "grossWeightKg": 1.05,
        "dimensionsCm": "30x20x10", "moq": "500 kg", "leadTime": "21 days",
        "certificates": ["Halal", "Origin declaration", "Lab report required"],
        "villageId": "DES-GAYO", "readiness": 88, "updatedAt": "2026-08-06",
    },
    {
        "id": "PRD-DES-KOPI-002", "name": "Kopi Bubuk Arabika Roasted Premium", "category": "Perkebunan",
        "status": "Enriched", "hs": "09012100", "origin": "Desa Kopi Gayo, Aceh Tengah",
        "packaging": "Kemasan valve bag 500 g, 24 pcs per karton", "netWeightKg": 0.5, "grossWeightKg": 0.55,
        "dimensionsCm": "25x15x8", "moq": "1.000 pack", "leadTime": "14 days",
        "certificates": ["Halal", "Roasting profile sheet"],
        "villageId": "DES-GAYO", "readiness": 82, "updatedAt": "2026-08-06",
    },
    {
        "id": "PRD-DES-KAKAO-003", "name": "Kakao Fermentasi Sulawesi", "category": "Perkebunan",
        "status": "Enriched", "hs": "18010000", "origin": "Desa Kakao Toraja, Sulawesi Selatan",
        "packaging": "Karung jute 60 kg atau kemasan vakum 1 kg", "netWeightKg": 1, "grossWeightKg": 1.1,
        "dimensionsCm": "30x20x15", "moq": "500 kg", "leadTime": "18 days",
        "certificates": ["Halal", "Fermentation log", "Lab report required"],
        "villageId": "DES-TORAJA", "readiness": 81, "updatedAt": "2026-08-06",
    },
    {
        "id": "PRD-DES-VANILI-004", "name": "Vanili Planifolia Grade A", "category": "Perkebunan",
        "status": "Enriched", "hs": "09061100", "origin": "Desa Vanili Bali, Tabanan, Bali",
        "packaging": "Vacuum pack 250 g dalam tin, 20 tin per karton", "netWeightKg": 0.25, "grossWeightKg": 0.3,
        "dimensionsCm": "20x15x6", "moq": "50 kg", "leadTime": "25 days",
        "certificates": ["Organic in progress", "Curing certificate", "Phytosanitary"],
        "villageId": "DES-VANILI-BALI", "readiness": 77, "updatedAt": "2026-08-05",
    },
    {
        "id": "PRD-DES-MANGGIS-005", "name": "Manggis Segar Premium", "category": "Hortikultura",
        "status": "Needs HS Review", "hs": "08109060", "origin": "Desa Manggis Situbondo, Jawa Timur",
        "packaging": "Kardus ventilasi 3 kg, cold chain 13°C", "netWeightKg": 3, "grossWeightKg": 3.4,
        "dimensionsCm": "40x30x20", "moq": "600 kg per shipment", "leadTime": "10 days",
        "certificates": ["Phytosanitary", "GlobalGAP in progress", "Cold chain"],
        "villageId": "DES-SITUBONDO", "readiness": 68, "updatedAt": "2026-08-04",
    },
    {
        "id": "PRD-DES-ROTAN-006", "name": "Keranjang Rotan Anyaman Set Isi 6", "category": "Kriya Rotan",
        "status": "Needs HS Review", "hs": "46021200", "origin": "Desa Rotan Kahayan, Kalimantan Tengah",
        "packaging": "1 set per kardus tebal + bubble wrap", "netWeightKg": 20, "grossWeightKg": 22,
        "dimensionsCm": "50x50x50", "moq": "100 set", "leadTime": "30 days",
        "certificates": ["SVLK evidence required", "Fumigation"],
        "villageId": "DES-KAHAYAN", "readiness": 70, "updatedAt": "2026-08-03",
    },
    {
        "id": "PRD-DES-ROTAN-007", "name": "Tas Rotan Fashion Anyaman", "category": "Kriya Rotan",
        "status": "Needs HS Review", "hs": "46021200", "origin": "Desa Rotan Kahayan, Kalimantan Tengah",
        "packaging": "1 pcs bubble wrap + kardus tebal, 24 pcs per karton", "netWeightKg": 0.8, "grossWeightKg": 0.9,
        "dimensionsCm": "35x30x12", "moq": "240 pcs", "leadTime": "28 days",
        "certificates": ["SVLK evidence required", "Fumigation"],
        "villageId": "DES-KAHAYAN", "readiness": 76, "updatedAt": "2026-08-03",
    },
    {
        "id": "PRD-DES-HHNK-008", "name": "Madu Hutan Murni Sumbawa", "category": "Hasil Hutan Non-Kayu",
        "status": "Ready", "hs": "04090000", "origin": "Desa Madu Sumbawa, NTB",
        "packaging": "Toples kaca 250 ml, 24 toples per karton", "netWeightKg": 0.375, "grossWeightKg": 0.6,
        "dimensionsCm": "30x30x25", "moq": "480 jars (20 karton)", "leadTime": "14 days",
        "certificates": ["Halal", "Water content test", "Traceability forest honey"],
        "villageId": "DES-SUMBAWA", "readiness": 84, "updatedAt": "2026-08-02",
    },
    {
        "id": "PRD-DES-CENGKEH-009", "name": "Cengkeh Utuh Grade A", "category": "Perkebunan",
        "status": "Ready", "hs": "09041100", "origin": "Desa Cengkeh Ternate, Maluku Utara",
        "packaging": "Karung gunny baru 25 kg, inner liner", "netWeightKg": 25, "grossWeightKg": 25.3,
        "dimensionsCm": "60x40x20", "moq": "1 ton", "leadTime": "20 days",
        "certificates": ["Phytosanitary", "Moisture test max 12%"],
        "villageId": "DES-TERNATE", "readiness": 75, "updatedAt": "2026-08-02",
    },
    {
        "id": "PRD-DES-LADA-010", "name": "Lada Putih Muntok Karung", "category": "Perkebunan",
        "status": "Ready", "hs": "09041200", "origin": "Desa Lada Putih Muntok, Bangka Belitung",
        "packaging": "Karung PP 25 kg dengan inner PE", "netWeightKg": 25, "grossWeightKg": 25.4,
        "dimensionsCm": "60x40x20", "moq": "1 ton", "leadTime": "18 days",
        "certificates": ["Phytosanitary", "Density test (IG Muntok)"],
        "villageId": "DES-MUNTOK", "readiness": 70, "updatedAt": "2026-08-01",
    },
    {
        "id": "PRD-DES-KAYUMANIS-011", "name": "Kulit Kayu Manis Kerinci Bale", "category": "Perkebunan",
        "status": "Needs HS Review", "hs": "09061900", "origin": "Desa Kayu Manis Kerinci, Jambi",
        "packaging": "Bale press 20 kg dibungkus karung goni", "netWeightKg": 20, "grossWeightKg": 20.5,
        "dimensionsCm": "80x50x30", "moq": "500 kg", "leadTime": "22 days",
        "certificates": ["Phytosanitary", "Coumarin content report"],
        "villageId": "DES-KERINCI", "readiness": 74, "updatedAt": "2026-08-01",
    },
    {
        "id": "PRD-DES-MANGGIS-012", "name": "Selai Manggis Olahan Desa", "category": "Olahan Pertanian",
        "status": "Needs HS Review", "hs": "20079900", "origin": "Desa Manggis Situbondo, Jawa Timur",
        "packaging": "Jar 220 g, 24 jar per karton", "netWeightKg": 0.22, "grossWeightKg": 0.35,
        "dimensionsCm": "30x30x20", "moq": "1.000 jar", "leadTime": "16 days",
        "certificates": ["Halal", "PIRT", "Nutrition facts ready"],
        "villageId": "DES-SITUBONDO", "readiness": 66, "updatedAt": "2026-07-31",
    },
]

VILLAGE_PROFILES = [
    {
        "id": "BIZ-DES-TORAJA", "companyName": "Koperasi Desa Kakao Toraja", "address": "Desa Kakao Toraja, Sulawesi Selatan",
        "productionCapacity": "3 ton kakao fermentasi / bulan", "yearEstablished": 2019,
        "certifications": ["Halal", "Fermentation log"], "status": "Complete",
        "owner": "Yohanis Tangka", "readiness": 88, "updatedAt": "2026-08-05",
    },
    {
        "id": "BIZ-DES-GAYO", "companyName": "BUMDes Kopi Gayo Sejahtera", "address": "Desa Kopi Gayo, Aceh Tengah",
        "productionCapacity": "8.000 retail bag / bulan", "yearEstablished": 2017,
        "certifications": ["Halal", "Origin declaration"], "status": "Needs Review",
        "owner": "Rizal Fahmi", "readiness": 82, "updatedAt": "2026-08-05",
    },
]

VILLAGE_ENRICHMENTS = [
    {
        "id": "ENR-DES-KAKAO", "productId": "PRD-DES-KAKAO-003",
        "hsCodeRecommendation": "18010000", "skuGenerated": "KAK-SUL-001",
        "nameEnglishB2b": "Sulawesi Fermented Cacao Beans",
        "descriptionEnglishB2b": "Well-fermented fine-flavor cacao from smallholder village plots in Toraja, sun dried on raised beds.",
        "marketingHighlights": ["Fine flavor cacao", "Village cooperative sourced", "Sun dried"],
        "lastUpdatedAi": "2026-08-06 09:30",
    },
    {
        "id": "ENR-DES-VANILI", "productId": "PRD-DES-VANILI-004",
        "hsCodeRecommendation": "09061100", "skuGenerated": "VAN-BAL-001",
        "nameEnglishB2b": "Grade A Vanilla Planifolia Beans",
        "descriptionEnglishB2b": "Hand-pollinated vanilla beans from Bali village farms, slow cured for rich aroma.",
        "marketingHighlights": ["Grade A 16cm+", "Hand pollinated", "Slow cured"],
        "lastUpdatedAi": "2026-08-05 14:00",
    },
    {
        "id": "ENR-DES-MANGGIS", "productId": "PRD-DES-MANGGIS-005",
        "hsCodeRecommendation": "08109060", "skuGenerated": "MGS-SIT-001",
        "nameEnglishB2b": "Premium Fresh Mangosteen",
        "descriptionEnglishB2b": "Sweet-sour premium mangosteen from Situbondo village orchards, field heat removed within 4 hours.",
        "marketingHighlights": ["Deep purple ripe fruit", "Cold chain ready", "Village orchard"],
        "lastUpdatedAi": "2026-08-04 10:15",
    },
    {
        "id": "ENR-DES-ROTAN", "productId": "PRD-DES-ROTAN-006",
        "hsCodeRecommendation": "46021200", "skuGenerated": "ROT-KAL-001",
        "nameEnglishB2b": "Handwoven Rattan Basket Set of 6",
        "descriptionEnglishB2b": "Artisan handwoven rattan baskets woven by village craftswomen along the Kahayan river.",
        "marketingHighlights": ["Handwoven", "Natural rattan", "Fair trade village craft"],
        "lastUpdatedAi": "2026-08-03 13:45",
    },
    {
        "id": "ENR-DES-HHNK", "productId": "PRD-DES-HHNK-008",
        "hsCodeRecommendation": "04090000", "skuGenerated": "MDU-SUM-001",
        "nameEnglishB2b": "Wild Forest Honey Sumbawa",
        "descriptionEnglishB2b": "Pure wild honey harvested sustainably from Sumbawa forest by village honey collectors.",
        "marketingHighlights": ["Wild harvest", "Sustainably sourced", "No added sugar"],
        "lastUpdatedAi": "2026-08-02 11:20",
    },
    {
        "id": "ENR-DES-KOPI", "productId": "PRD-DES-KOPI-001",
        "hsCodeRecommendation": "09011100", "skuGenerated": "COF-GAY-GRN",
        "nameEnglishB2b": "Gayo Arabica Green Beans - Single Origin Village Lot",
        "descriptionEnglishB2b": "Fully washed Gayo highland arabica from a BUMDes-managed village lot, screen 16+.",
        "marketingHighlights": ["Single-origin Aceh", "BUMDes managed lot", "Screen 16+"],
        "lastUpdatedAi": "2026-08-06 08:50",
    },
    {
        "id": "ENR-DES-CENGKEH", "productId": "PRD-DES-CENGKEH-009",
        "hsCodeRecommendation": "09041100", "skuGenerated": "CGK-TER-A01",
        "nameEnglishB2b": "Grade A Whole Cloves",
        "descriptionEnglishB2b": "Headless whole cloves from volcanic Ternate island soil, oil content above 15%.",
        "marketingHighlights": ["High volatile oil", "Headless grade A", "Volcanic soil origin"],
        "lastUpdatedAi": "2026-08-02 09:10",
    },
]


# ---------------------------------------------------------------------------
# Konten edukasi spesifik desa (menggantikan modul generik).
# ---------------------------------------------------------------------------
VILLAGE_EDU_MODULES = [
    {
        "id": "EDU-DES-PANEN-01", "title": "Cara Ekspor Hasil Panen Segar (Sertifikat Kesehatan Tumbuhan)",
        "level": "Pemula", "status": "Published", "lessons": 6, "completion": 0,
        "summary": "Langkah demi langkah mengurus Sertifikat Kesehatan Tumbuhan (Phytosanitary) dari karantina pertanian sebelum hasil panen berangkat.",
        "steps": ["Kenali jenis komoditas & hama karantina", "Ajukan permohonan ke Badan Karantina Pertanian", "Siapkan sampel & pemeriksaan lapangan", "Terbitkan sertifikat & lampirkan ke dokumen ekspor"],
    },
    {
        "id": "EDU-DES-HALAL-02", "title": "Panduan Sertifikasi Halal untuk Tembus Pasar Timur Tengah",
        "level": "Pemula", "status": "Published", "lessons": 5, "completion": 0,
        "summary": "Proses sertifikasi halal untuk produk olahan desa: bahan, proses produksi, hingga label halal yang diterima pasar Timur Tengah.",
        "steps": ["Kumpulkan daftar bahan & pemasok", "Amankan proses produksi (PPH)", "Ajukan via SIHALAL", "Pahami requirement negara tujuan (GAC/SMAS)"],
    },
    {
        "id": "EDU-DES-KEMAS-03", "title": "Tips Pengemasan Kriya agar Tahan Banting saat di Kontainer",
        "level": "Menengah", "status": "Published", "lessons": 4, "completion": 0,
        "summary": "Teknik packing kriya rotan, kayu, dan tekstun agar selamat menempuh perjalanan laut 30+ hari tanpa retak atau jamur.",
        "steps": ["Hitung dimensi karton & container loading", "Gunakan silica gel & wrapping moisture barrier", "Susun dunnage & stacking limit", "Foto kondisi packing sebagai bukti klaim asuransi"],
    },
    {
        "id": "EDU-DES-NIB-04", "title": "Tata Cara Pengurusan NIB dan IUMK untuk BUMDes",
        "level": "Pemula", "status": "Published", "lessons": 5, "completion": 0,
        "summary": "Panduan legalitas dasar: mengurus Nomor Induk Berusaha (NIB) dan Izin Usaha Mikro Kecil (IUMK) untuk badan usaha desa lewat OSS-RBA.",
        "steps": ["Siapkan akta desa/koperasi & NPWP", "Registrasi akun OSS-RBA", "Isi KBLI 5 digit sesuai komoditas", "Unduh NIB & IUMK", "Manfaatkan fasilitas bea cukai bagi UMK"],
    },
    {
        "id": "EDU-DES-DOC-05", "title": "Daftar Dokumen Wajib Ekspor ke Singapura dan Jepang (Khusus Pertanian)",
        "level": "Menengah", "status": "Published", "lessons": 7, "completion": 0,
        "summary": "Checklist dokumen per negara: invoice, packing list, COO Form AI/ASEAN-JEPA, phytosanitary, health certificate, hingga label Jepang.",
        "steps": ["Dokumen dasar semua negara", "Khusus Singapura: COO Form D & SFA", "Khusus Jepang: label Bahasa Jepang & JEPA", "Simpan arsip 5 tahun untuk audit"],
    },
    {
        "id": "EDU-DES-KARANTINA-06", "title": "PP 28/2024: Karantina Pertanian untuk Petani & Pelaku Usaha Desa",
        "level": "Pemula", "status": "Published", "lessons": 4, "completion": 0,
        "summary": "Memahami Peraturan Pemerintah No. 28 Tahun 2024 tentang karantina hewan, ikan, dan tumbuhan — apa artinya bagi pengiriman hasil kebun Anda.",
        "steps": ["Penggolongan media pembawa (MKH/MKH/TIK)", "Wilayah karantina & negara tujuan", "Tindakan karantina: P4/PK/PKHP", "Biaya & layanan cepat karantina"],
    },
    {
        "id": "EDU-DES-CITES-07", "title": "CITES & Dokumen Asal Bahan Baku untuk Krija Berbahan Alam",
        "level": "Lanjutan", "status": "Published", "lessons": 5, "completion": 0,
        "summary": "Untuk krija dari kayu, rotan, dan bahan alam lainnya: pastikan bahan bukan spesies dilindungi CITES dan siapkan dokumen asal bahan baku.",
        "steps": ["Cek appendix CITES untuk bahan Anda", "Legalitas bahan baku (SVLK/legalitas kayu)", "Dokumen asal-usul dari penyuluh kehutanan", "Alternatif baman aman saat bahan terlarang"],
    },
]

VILLAGE_EDU_ARTICLES = [
    {
        "id": "ART-DES-HST-01", "title": "Sertifikat Kesehatan Tumbuhan: Syarat Minimal & Cara Mengurus",
        "status": "Published", "level": "Pemula", "readMinutes": 5,
        "tags": ["Karantina", "Pertanian", "PP 28/2024"],
        "summary": "Syarat dokumen minimal dan alur pengurusan Sertifikat Kesehatan Tumbuhan untuk hasil kebun desa.",
        "body": "Sertifikat Kesehatan Tumbuhan (SKT/Phytosanitary) diterbitkan Badan Karantina Pertanian berdasarkan PP 28/2024. Siapkan: surat permohonan, data komoditas (nama latin, volume, kemasan), negara tujuan, dan jadwal pemeriksaan. Pemeriksaan dilakukan di tempat penimbunan sebelum kontainer ditutup.",
    },
    {
        "id": "ART-DES-NIB-02", "title": "NIB vs IUMK: Mana yang Wajib untuk BUMDes Anda?",
        "status": "Published", "level": "Pemula", "readMinutes": 4,
        "tags": ["NIB", "IUMK", "BUMDes"],
        "summary": "Bedanya NIB dan IUMK, urutan pengurusannya, dan kenapa keduanya pintu masuk fasilitas ekspor UMK.",
        "body": "NIB menjadi identitas pelaku usaha di OSS-RBA dan syarat awal semua perizinan. IUMK menegaskan skala usaha mikro/kecil agar memenuhi syarat fasilitas: pembebasan Bea Masuk Impon (API UM), layanan ekspor masuk (exim), hingga kemudahan kepabeanan Permendag 16/2025.",
    },
    {
        "id": "ART-DES-KEMAS-03", "title": "5 Kesalahan Pengemasan Kriya yang Bikin Klaim Asuransi Ditolak",
        "status": "Published", "level": "Menengah", "readMinutes": 6,
        "tags": ["Kriya", "Pengemasan", "Asuransi"],
        "summary": "Kesalahan umum packing krija rotan & kayu dan cara mendokumentasikannya dengan benar.",
        "body": "Karton tipis tanpa corner protector, tidak ada silica gel, pallet tidak di-fumigasi, tidak ada foto pre-loading, dan deskripsi kemasan di B/L tidak cocok dengan packing list. Dokumentasikan setiap step agar klaim mudah dibayar.",
    },
]

# User contoh peran KepalaDesa (RBAC sederhana).
KEPALA_DESA_USER = {
    "id": "U-DES-001", "email": "kepala@desagayo.example", "fullName": "Rustam Efendi",
    "role": "KepalaDesa", "organization": "BUMDes Kopi Gayo Sejahtera",
    "password_plain": "desa12345", "status": "Active", "createdAt": "2026-08-01", "lastLogin": "2026-08-06 08:00",
}


def seed_village_hs_codes() -> int:
    """Muat kode HS dari CSV hanya untuk chapter komoditas desa (01-24, 46, 68-70).

    Setiap record ditandai `is_village_priority=True` + `commodity_group`.
    Mengembalikan jumlah record yang dimuat (0 jika dataset penuh sudah ada).
    """
    if db.loaded_records("hs_codes") >= 1000:
        return 0  # dataset penuh sudah pernah dimuat
    from app.data import hs_loader

    loader = hs_loader.get_hs_loader()
    village_codes = filter_village_hs_codes(loader.codes)
    for i, code in enumerate(village_codes, 1):
        hs_code = code.get("hs_code", "")
        db.insert("hs_codes", {
            "id": f"HS-{i:04d}",
            "hs_code": hs_code,
            "description": code.get("description", ""),
            "section": code.get("section", ""),
            "level": code.get("level", len(hs_code)),
            "parent": code.get("parent", ""),
            **village_flags(hs_code),
            "createdAt": "now",
        })
    return len(village_codes)


def seed_villages() -> int:
    """Isi tabel desa fiktif untuk demo peta potensi desa."""
    existing = {str(v.get("id")) for v in db.all("villages")}
    inserted = 0
    for village in VILLAGE_DESA:
        if village["id"] not in existing:
            db.insert("villages", {
                **village,
                "status": _desa_status(village["readiness"]),
                "createdAt": "2026-08-01",
            })
            inserted += 1
    return inserted


def seed_village_products() -> None:
    """Isi kurasi produk komoditas unggulan desa + relasi ke desa."""
    existing_products = {str(p.get("id")) for p in db.all("products")}
    for product in VILLAGE_PRODUCTS:
        if product["id"] not in existing_products:
            db.insert("products", {
                "netWeight": f'{product["netWeightKg"]} kg',
                "grossWeight": f'{product["grossWeightKg"]} kg',
                **product,
                **village_flags(product["hs"]),
            })

    existing_profiles = {str(p.get("id")) for p in db.all("business_profiles")}
    for profile in VILLAGE_PROFILES:
        if profile["id"] not in existing_profiles:
            db.insert("business_profiles", dict(profile))

    existing_enrichments = {str(e.get("productId")) for e in db.all("product_enrichments")}
    for enrichment in VILLAGE_ENRICHMENTS:
        if enrichment["productId"] not in existing_enrichments:
            db.insert("product_enrichments", dict(enrichment))


def seed_village_education() -> None:
    """Ganti konten edukasi generik dengan materi spesifik desa (5-7 modul)."""
    for record in list(db.all("educational_modules")):
        db.delete("educational_modules", record.get("id"))
    for record in list(db.all("educational_articles")):
        db.delete("educational_articles", record.get("id"))

    for module in VILLAGE_EDU_MODULES:
        db.insert("educational_modules", dict(module))
    for article in VILLAGE_EDU_ARTICLES:
        db.insert("educational_articles", dict(article))


def seed_kepala_desa_user() -> None:
    """User demo peran KepalaDesa untuk menu sederhana (RBAC)."""
    email = KEPALA_DESA_USER["email"]
    if not db.get_by("users", email=email):
        payload = dict(KEPALA_DESA_USER)
        password = payload.pop("password_plain")
        db.insert("users", {**payload, "password": hash_password(password)})


def seed_village_commodities() -> None:
    """Isi database dengan kurasi komoditas desa untuk demo.

    Aman dipanggil berulang: hanya mengisi data yang belum ada.
    """
    seed_villages()
    seed_village_products()
    seed_village_education()
    seed_kepala_desa_user()
