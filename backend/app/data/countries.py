"""Master data: negara tujuan ekspor + regulasi (adapted dari `seed_countries` ExportReadyAI).

Digunakan untuk:
- endpoint `/countries/` (list + detail dengan regulasi per kategori)
- compliance check pada Export Analysis
- dropdown target market di pricing / market intelligence
"""

from __future__ import annotations

COUNTRIES: list[dict] = [
    {"country_code": "JP", "country_name": "Japan", "region": "Asia"},
    {"country_code": "US", "country_name": "United States", "region": "North America"},
    {"country_code": "DE", "country_name": "Germany", "region": "Europe"},
    {"country_code": "SG", "country_name": "Singapore", "region": "Asia"},
    {"country_code": "AU", "country_name": "Australia", "region": "Oceania"},
    {"country_code": "CN", "country_name": "China", "region": "Asia"},
    {"country_code": "KR", "country_name": "South Korea", "region": "Asia"},
    {"country_code": "GB", "country_name": "United Kingdom", "region": "Europe"},
    {"country_code": "NL", "country_name": "Netherlands", "region": "Europe"},
    {"country_code": "AE", "country_name": "United Arab Emirates", "region": "Middle East"},
    {"country_code": "MY", "country_name": "Malaysia", "region": "Asia"},
    {"country_code": "TH", "country_name": "Thailand", "region": "Asia"},
    {"country_code": "SA", "country_name": "Saudi Arabia", "region": "Middle East"},
    {"country_code": "ID", "country_name": "Indonesia", "region": "Asia"},
]

# rule_category: Ingredient | Labeling | Physical
REGULATIONS: list[dict] = [
    # Japan
    {"country_code": "JP", "rule_category": "Ingredient", "forbidden_keywords": "Pewarna Buatan, MSG berlebih, Bahan Non-Halal",
     "required_specs": "", "description_rule": "Japan Food Sanitation Act mengatur aditif makanan secara ketat."},
    {"country_code": "JP", "rule_category": "Labeling", "forbidden_keywords": "",
     "required_specs": "Japanese Language Label, Allergen Info (28 items), Best Before Date",
     "description_rule": "Label wajib dalam Bahasa Jepang dengan deklarasi alergen spesifik."},
    {"country_code": "JP", "rule_category": "Physical", "forbidden_keywords": "",
     "required_specs": "JAS Certification, Presisi 1mm",
     "description_rule": "Japanese Agricultural Standard (JAS) mungkin diperlukan."},
    # United States
    {"country_code": "US", "rule_category": "Ingredient", "forbidden_keywords": "Pewarna K10, Formalin, Boraks, Rhodamine B",
     "required_specs": "", "description_rule": "Regulasi FDA melarang aditif dan pewarna makanan tertentu."},
    {"country_code": "US", "rule_category": "Labeling", "forbidden_keywords": "",
     "required_specs": "Nutrition Facts, Allergen Info, Country of Origin",
     "description_rule": "FDA mewajibkan label nutrisi dan deklarasi alergen."},
    {"country_code": "US", "rule_category": "Physical", "forbidden_keywords": "",
     "required_specs": "ISPM-15 (wood packaging), FDA Registration",
     "description_rule": "Kemasan kayu harus memenuhi standar ISPM-15."},
    # Germany / EU
    {"country_code": "DE", "rule_category": "Ingredient", "forbidden_keywords": "Sawit Non-RSPO, Pewarna Azo, GMO",
     "required_specs": "", "description_rule": "Regulasi EU tentang minyak sawit berkelanjutan dan bebas GMO."},
    {"country_code": "DE", "rule_category": "Labeling", "forbidden_keywords": "",
     "required_specs": "CE Marking, Allergen Info, Nutritional Info, German/English Label",
     "description_rule": "Regulasi pelabelan EU dengan persyaratan CE marking."},
    {"country_code": "DE", "rule_category": "Physical", "forbidden_keywords": "",
     "required_specs": "CE Certification, EU Conformity Assessment",
     "description_rule": "Produk harus memenuhi standar keamanan dan kualitas EU."},
    # Australia
    {"country_code": "AU", "rule_category": "Ingredient", "forbidden_keywords": "Propolis mentah, Madu non-standar, Bahan dari tanaman invasif",
     "required_specs": "", "description_rule": "Persyaratan biosekuriti ketat untuk impor makanan."},
    {"country_code": "AU", "rule_category": "Labeling", "forbidden_keywords": "",
     "required_specs": "Country of Origin, Allergen Declaration, Nutritional Info Panel",
     "description_rule": "Australian Consumer Law mewajibkan pelabelan spesifik."},
    {"country_code": "AU", "rule_category": "Physical", "forbidden_keywords": "",
     "required_specs": "ISPM-15, Fumigation Certificate, Biosecurity Clearance",
     "description_rule": "Persyaratan karantina dan biosekuriti untuk semua kemasan."},
    # Singapore
    {"country_code": "SG", "rule_category": "Ingredient", "forbidden_keywords": "Pewarna Terlarang, Bahan Non-Halal (untuk produk Halal)",
     "required_specs": "", "description_rule": "Singapore Food Agency mengatur aditif makanan."},
    {"country_code": "SG", "rule_category": "Labeling", "forbidden_keywords": "",
     "required_specs": "English Label, Nutrition Information Panel, Allergen Info",
     "description_rule": "Label wajib dalam Bahasa Inggris dengan panel nutrisi."},
    {"country_code": "SG", "rule_category": "Physical", "forbidden_keywords": "",
     "required_specs": "SFA Import License, Halal Certification (jika berlaku)",
     "description_rule": "Lisensi impor dari SFA diperlukan untuk produk makanan."},
    # China
    {"country_code": "CN", "rule_category": "Ingredient", "forbidden_keywords": "Bahan Terlarang China, Pewarna Sintetis Tertentu",
     "required_specs": "", "description_rule": "Regulasi GACC tentang keamanan pangan."},
    {"country_code": "CN", "rule_category": "Labeling", "forbidden_keywords": "",
     "required_specs": "Chinese Language Label, GB Standards Compliance, CIQ Inspection",
     "description_rule": "Harus mematuhi standar GB nasional, label dalam Bahasa Mandarin."},
    {"country_code": "CN", "rule_category": "Physical", "forbidden_keywords": "",
     "required_specs": "CCC Certification, GACC Registration",
     "description_rule": "China Compulsory Certification untuk produk tertentu."},
    # South Korea
    {"country_code": "KR", "rule_category": "Ingredient", "forbidden_keywords": "Bahan Terlarang MFDS, Aditif Tanpa Izin",
     "required_specs": "", "description_rule": "MFDS mengatur aditif makanan dan bahan impor."},
    {"country_code": "KR", "rule_category": "Labeling", "forbidden_keywords": "",
     "required_specs": "Korean Language Label, Allergen Info, Expiry Date",
     "description_rule": "Label wajib dalam Bahasa Korea dengan deklarasi alergen."},
    {"country_code": "KR", "rule_category": "Physical", "forbidden_keywords": "",
     "required_specs": "KC Certification, MFDS Import Declaration",
     "description_rule": "KC certification untuk produk tertentu."},
    # United Kingdom
    {"country_code": "GB", "rule_category": "Ingredient", "forbidden_keywords": "Pewarna Azo, GMO, Sawit Non-Sustainable",
     "required_specs": "", "description_rule": "UK FSA mengatur keamanan pangan pasca-Brexit."},
    {"country_code": "GB", "rule_category": "Labeling", "forbidden_keywords": "",
     "required_specs": "UKCA Marking, Allergen Info, Nutritional Info, English Label",
     "description_rule": "UKCA marking menggantikan CE untuk banyak produk di UK."},
    {"country_code": "GB", "rule_category": "Physical", "forbidden_keywords": "",
     "required_specs": "UKCA Certification, EORI Number",
     "description_rule": "Persyaratan UKCA dan registrasi EORI untuk importir."},
    # Netherlands
    {"country_code": "NL", "rule_category": "Ingredient", "forbidden_keywords": "GMO, Pewarna Azo, Sawit Non-RSPO",
     "required_specs": "", "description_rule": "NVWA mengatur keamanan pangan di Belanda."},
    {"country_code": "NL", "rule_category": "Labeling", "forbidden_keywords": "",
     "required_specs": "EU Label, Allergen Info, Nutritional Info, English/Dutch Label",
     "description_rule": "Label EU dengan informasi nutrisi dan alergen."},
    {"country_code": "NL", "rule_category": "Physical", "forbidden_keywords": "",
     "required_specs": "CE Certification, EU Conformity, ISPM-15",
     "description_rule": "Standar keamanan EU dan ISPM-15 untuk kemasan kayu."},
    # UAE
    {"country_code": "AE", "rule_category": "Ingredient", "forbidden_keywords": "Babi, Alkohol, Gelatin Non-Halal, Lemak Hewani Non-Halal",
     "required_specs": "", "description_rule": "Semua produk makanan harus memenuhi standar Halal."},
    {"country_code": "AE", "rule_category": "Labeling", "forbidden_keywords": "",
     "required_specs": "Arabic Label, Halal Certification, Expiry Date, Country of Origin",
     "description_rule": "Label wajib mencakup teks Arab dan sertifikasi Halal."},
    {"country_code": "AE", "rule_category": "Physical", "forbidden_keywords": "",
     "required_specs": "ESMA Certification, Halal Certificate",
     "description_rule": "Persyaratan Emirates Authority for Standardization."},
    # Malaysia
    {"country_code": "MY", "rule_category": "Ingredient", "forbidden_keywords": "Bahan Non-Halal, Pewarna Terlarang",
     "required_specs": "", "description_rule": "JAKIM mengatur standar Halal di Malaysia."},
    {"country_code": "MY", "rule_category": "Labeling", "forbidden_keywords": "",
     "required_specs": "Malay/English Label, Halal Logo, Expiry Date",
     "description_rule": "Label wajib dalam Bahasa Melayu/Inggris dengan logo Halal."},
    {"country_code": "MY", "rule_category": "Physical", "forbidden_keywords": "",
     "required_specs": "Halal Certification, ISPM-15",
     "description_rule": "Sertifikasi Halal dari badan yang diakui."},
    # Thailand
    {"country_code": "TH", "rule_category": "Ingredient", "forbidden_keywords": "Pewarna Terlarang, Bahan Non-Halal",
     "required_specs": "", "description_rule": "Thai FDA mengatur aditif dan keamanan pangan."},
    {"country_code": "TH", "rule_category": "Labeling", "forbidden_keywords": "",
     "required_specs": "Thai Language Label, Allergen Info, Expiry Date",
     "description_rule": "Label wajib dalam Bahasa Thailand."},
    {"country_code": "TH", "rule_category": "Physical", "forbidden_keywords": "",
     "required_specs": "Thai FDA Import License, ISPM-15",
     "description_rule": "Lisensi impor dari Thai FDA."},
    # Saudi Arabia
    {"country_code": "SA", "rule_category": "Ingredient", "forbidden_keywords": "Babi, Alkohol, Gelatin Non-Halal, Bahan Non-Halal",
     "required_specs": "", "description_rule": "SFDA mewajibkan kepatuhan Halal ketat."},
    {"country_code": "SA", "rule_category": "Labeling", "forbidden_keywords": "",
     "required_specs": "Arabic Label, Halal Certification, Expiry Date",
     "description_rule": "Label wajib dalam Bahasa Arab dengan sertifikasi Halal."},
    {"country_code": "SA", "rule_category": "Physical", "forbidden_keywords": "",
     "required_specs": "SFDA Registration, Halal Certificate",
     "description_rule": "Registrasi produk di SFDA sebelum impor."},
    # Indonesia (untuk produk domestik / re-export)
    {"country_code": "ID", "rule_category": "Ingredient", "forbidden_keywords": "Formalin, Boraks, Rhodamine B, Bahan Terlarang BPOM",
     "required_specs": "", "description_rule": "BPOM mengatur bahan yang dilarang dalam pangan."},
    {"country_code": "ID", "rule_category": "Labeling", "forbidden_keywords": "",
     "required_specs": "Indonesian Label, BPOM MD Number, Halal Logo, Expiry Date",
     "description_rule": "Label wajib dalam Bahasa Indonesia dengan nomor BPOM."},
    {"country_code": "ID", "rule_category": "Physical", "forbidden_keywords": "",
     "required_specs": "SNI Certification (jika ada), Halal Certification",
     "description_rule": "Sertifikasi SNI untuk produk tertentu."},
]


def get_countries() -> list[dict]:
    return [dict(c) for c in COUNTRIES]


def get_regulations(country_code: str) -> list[dict]:
    return [dict(r) for r in REGULATIONS if r["country_code"] == country_code.upper()]


def get_country(country_code: str) -> dict | None:
    code = country_code.upper()
    for c in COUNTRIES:
        if c["country_code"] == code:
            return dict(c)
    return None


def resolve_country(value: str) -> str:
    """Ubah input (kode 2-huruf atau nama negara) menjadi kode ISO 2-huruf."""
    value = (value or "").strip()
    if not value:
        return "JP"
    code = value.upper()[:2]
    # Jika sudah berupa kode yang dikenal
    if get_country(code):
        return code
    # Coba cocokkan dengan nama negara
    for c in COUNTRIES:
        if c["country_name"].lower() == value.lower() or value.lower() in c["country_name"].lower():
            return c["country_code"]
    # Fallback: huruf pertama dari nama
    return code


def region_of(country_code: str) -> str:
    country = get_country(country_code)
    return (country or {}).get("region", "Asia")
