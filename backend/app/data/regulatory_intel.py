"""Global Export–Import Regulatory Intelligence baseline.

Snapshot per 15 Agustus 2026. Bukan pengganti pengecekan aturan resmi pada saat transaksi.
Referensi: WCO (HS), WTO (tarif/valuation), ITC Market Access Map, UNCTAD TRAINS,
portal bea cukai & kementerian dagang nasional (BTKI/INSW/DJBC, HTSUS, TARIC,
Japan Customs, KCS/UNI-PASS, DGFT, GACC, UK Integrated Online Tariff, CBSA, dll.).

Model yang dipakai:
    Regulatory Key = Origin + Destination + HS + Product Attributes + End User
                     + Incoterm + Value + FTA + Date
Eksportir WAJIB memeriksa ulang sebelum shipment karena aturan sering berubah.
"""

from __future__ import annotations

from typing import Any

# ----------------------------------------------------------------------------
# BLOKS & SERIKAT kepabeanan antarnegara
# ----------------------------------------------------------------------------
CUSTOMS_SYSTEMS: dict[str, dict[str, Any]] = {
    "ASEAN": {
        "label": "ASEAN / AHTN",
        "nomenclature": "AHTN 2022 (8 digit) atas basis HS",
        "tariffs": "MFN nasional + preferensi ATIGA/RCEP",
        "note": "ATIGA bukan otomatis 0%: cek eligibility, Product Specific Rule, bukti asal, direct consignment.",
        "sources": [
            {"name": "ASEAN Trade Repository", "url": "https://atr.asean.org/"},
        ],
    },
    "EU": {
        "label": "European Union / TARIC",
        "nomenclature": "Combined Nomenclature (8-10 digit) atas TARIC",
        "tariffs": "Common External Tariff (MFN) + preferensi FTA; VAT & product rules per negara.",
        "note": "Tarif 0% ≠ lolos pasar: CE marking, REACH, RoHS, food, phytosanitary, dst wajib dicek.",
        "sources": [
            {"name": "Access2Markets", "url": "https://trade.ec.europa.eu/access-to-markets/en/home"},
            {"name": "EU TARIC", "url": "https://ec.europa.eu/taxation_customs/taric_en"},
        ],
    },
    "MERCOSUR": {
        "label": "MERCOSUR / NCM",
        "nomenclature": "NCM (8 digit) atas basis HS",
        "tariffs": "Arancel Externo Común (AEC) + pengecualian nasional",
        "note": "Jangan anggap seragam: ada exception per negara anggota (mis. Brazil vs Paraguay).",
        "sources": [{"name": "MERCOSUR NCM/AEC", "url": "https://www.mercosur.int/"}],
    },
    "EAEU": {
        "label": "Eurasian Economic Union / CN FEA",
        "nomenclature": "CN FEA EAEU (10 digit)",
        "tariffs": "Common Customs Tariff EAEU",
        "note": "Layer tambahan vital: sanctions, restricted parties, banking, shipping, end-user control.",
        "sources": [{"name": "Eurasian Economic Commission", "url": "https://eec.eaeunion.org/"}],
    },
    "EAC": {
        "label": "East African Community / CET",
        "nomenclature": "EAC Common External Tariff",
        "tariffs": "CET bands dominan 0%, 10%, 25%, 35% (ada perlakuan khusus produk)",
        "note": "Cek exemption & sensitif list per komoditas.",
        "sources": [{"name": "EAC Trade Regime", "url": "https://www.eac.int/"}],
    },
    "AfCFTA": {
        "label": "AfCFTA",
        "nomenclature": "National tariff + AfCFTA tariff concessions",
        "tariffs": "Preferensi AfCFTA bila sesuai Rules of Origin",
        "note": "Rules of Origin sangat penting. e-Tariff Book disediakan WCO.",
        "sources": [{"name": "AfCFTA e-Tariff Book", "url": "https://www.wcoomd.org/"}],
    },
    "PRODCOM": {
        "label": "Uni Ekonomi / bilateral",
        "nomenclature": "HS nasional",
        "tariffs": "MFN nasional + FTA bilateral",
        "note": "Perlu pengecekan per negara anggota.",
        "sources": [],
    },
}

# Kode negara -> sistem kepabeanan/blok (default PRODCOM bila tak terdaftar)
COUNTRY_CUSTOMS: dict[str, str] = {
    "BN": "ASEAN", "KH": "ASEAN", "ID": "ASEAN", "LA": "ASEAN", "MY": "ASEAN",
    "MM": "ASEAN", "PH": "ASEAN", "SG": "ASEAN", "TH": "ASEAN", "VN": "ASEAN",
    "AT": "EU", "BE": "EU", "BG": "EU", "HR": "EU", "CY": "EU", "CZ": "EU",
    "DK": "EU", "EE": "EU", "FI": "EU", "FR": "EU", "DE": "EU", "GR": "EU",
    "HU": "EU", "IE": "EU", "IT": "EU", "LV": "EU", "LT": "EU", "LU": "EU",
    "MT": "EU", "NL": "EU", "PL": "EU", "PT": "EU", "RO": "EU", "SK": "EU",
    "SI": "EU", "ES": "EU", "SE": "EU",
    "AR": "MERCOSUR", "BR": "MERCOSUR", "PY": "MERCOSUR", "UY": "MERCOSUR",
    "AM": "EAEU", "BY": "EAEU", "KZ": "EAEU", "KG": "EAEU", "RU": "EAEU",
    "KE": "EAC", "TZ": "EAC", "UG": "EAC", "RW": "EAC", "BI": "EAC", "SS": "EAC",
    "GH": "AfCFTA", "NG": "AfCFTA", "ZA": "AfCFTA", "EG": "AfCFTA", "MA": "AfCFTA",
    "KE": "EAC", "UG": "EAC", "TZ": "EAC",
}


def customs_system_of(country_code: str) -> dict[str, Any]:
    return CUSTOMS_SYSTEMS.get(COUNTRY_CUSTOMS.get(country_code.upper(), "PRODCOM"))


# ----------------------------------------------------------------------------
# PROFIL REGULASI PER NEGARA (pasar utama; sisanya memakai template regional)
# ----------------------------------------------------------------------------
# Setiap profil: impor & ekspor aturan ringkas + tarif/nota + pajak domestik +
# dokumen + otoritas + status verifikasi. Nilai bersifat indikatif baseline.
COUNTRY_PROFILES: dict[str, dict[str, Any]] = {
    "ID": {
        "customs": "DJBC / BTKI 2022 (AHTN 8 digit); INSW gateway; PIB untuk impor, PEB untuk ekspor",
        "tariff": "Bea masuk MFN umumnya 0-150%, rata-rata ~8%; PPN 11% + PPh22 2.5-10% + PPnBM bila kena; bea keluar utk SDA strategis",
        "fta": "18 FTA/PTA: ATIGA, ACFTA, AKFTA, AIFTA, AANZFTA, AJCEP, AHKFTA, IJEPA, IPPTA, ICCEPA, IACEPA, IECEPA, D-8, IMPTA, RCEP, IKCEPA, IUAE-CEPA, MoU Palestine",
        "checks": "HS/AHTN -> Lartas -> bea masuk/keluar -> PPN/PPh/Cukai -> persetujuan impor/ekspor -> surveyor -> certificate -> COO -> karantina/BPOM/SNI",
        "import_rules": [
            "Gunakan pos tarif BTKI 2022 (8 digit) untuk seluruh pemberitahuan PIB/PEB.",
            "Cek lartas (larangan & pembatasan) per komoditas via INSW sebelum impor.",
            "Persetujuan impor dari K/L terkait bisa wajib (mis. karantina, BPOM, Kemenperin).",
            "Kebijakan komoditas berubah cepat: Permendag 11/2026 (impor pertanian), 16/2026 (kelapa sawit), 6/2026 (larangan ekspor).",
        ],
        "export_rules": [
            "PEB + persetujuan ekspor untuk barang tertentu (lartas ekspor).",
            "COO/surat keterangan asal untuk klaim FTA (ATIGA/RCEP/dll).",
            "Bea keluar berlaku untuk ekspor SDA strategis tertentu.",
        ],
        "documents": ["PIB / PEB", "Invoice & packing list", "Bill of lading/AWB", "Certificate of Origin (bila klaim FTA)", "Surat persetujuan ekspor/import (bila lartas)", "Sertifikat karantina/BPOM/SNI bila relevan"],
        "authorities": [
            {"name": "Bea Cukai (DJBC)", "url": "https://www.beacukai.go.id/"},
            {"name": "INSW", "url": "https://insw.go.id/"},
            {"name": "Kemendag (JDIH)", "url": "https://jdih.kemendag.go.id/"},
            {"name": "FTA DJBC", "url": "https://ftadjbc.info/"},
        ],
        "verified": "2026-08-15",
    },
    "JP": {
        "customs": "Japan Customs; statistical code 9 digit; tarif nasional + EPA/RCEP",
        "tariff": "Bea masuk + consumption tax 10%; bandingkan MFN vs IJEPA/RCEP/CPTPP",
        "fta": "IJEPA, RCEP, CPTPP, AJCEP",
        "checks": "HS -> tariff -> EPA preference -> RoO -> labeling -> food standard",
        "import_rules": [
            "Label wajib bahasa Jepang; deklarasi alergen (28 item); Food Sanitation Act.",
            "Persyaratan JAS untuk produk pertanian tertentu.",
            "Makin dalam EPA: pastikan memenuhi preferential Rules of Origin untuk tarif 0%/rendah.",
        ],
        "export_rules": ["Periksa izin ekspor bila barang tergolong strategic/dual-use (Export Control Order)."],
        "documents": ["Customs declaration", "Invoice & packing list", "Certificate of Origin (EPA/RCEP)", "Labeling compliance sheet"],
        "authorities": [{"name": "Japan Customs", "url": "https://www.customs.go.jp/english/"}, {"name": "METI (export control)", "url": "https://www.meti.go.jp/english/policy/external_economy/trade_control/"}],
        "verified": "2026-08-15",
    },
    "US": {
        "customs": "CBP; HTSUS (HTS Revision 15/2026); PGA (FDA/USDA/EPA/FCC/dst)",
        "tariff": "HTSUS MFN; + trade remedies (301, AD/CVD, Section 232); MPF 0.3464% (min $27.75/maks $538.40); HMF utk ocean",
        "fta": "USMCA, US-Japan, dst",
        "checks": "HTS -> rate -> Chapter 99 -> PGA -> EAR/ECCN -> OFAC screening",
        "import_rules": [
            "Klasifikasi HTS bisa 8-10 digit; cek note chapter & Chapter 99 untuk kode khusus.",
            "Barang tertentu under FDA/USDA/EPA/FCC; registrasi & label khusus mungkin wajib.",
            "Cek Section 301 & trade remedies (kurs bea bisa jauh di atas MFN).",
        ],
        "export_rules": ["EAR/ECCN -> Country Chart -> end use/user -> BIS license bila perlu; cek Consolidated Screening List."],
        "documents": ["Entry form (CBP Form 7501)", "Commercial invoice", "Packing list", "Bill of lading/AWB", "Entry bond", "Certificates (FDA/dll) bila relevan"],
        "authorities": [{"name": "USITC HTS", "url": "https://hts.usitc.gov/"}, {"name": "CBP", "url": "https://www.cbp.gov/"}, {"name": "BIS export control", "url": "https://www.trade.gov/us-export-controls"}, {"name": "OFAC", "url": "https://ofac.treasury.gov/"}],
        "verified": "2026-08-15",
    },
    "CN": {
        "customs": "GACC; klasifikasi HS nasional; pengawasan impor/ekspor GACC",
        "tariff": "MFN China + VAT 13% (umum); CCC untuk produk wajib",
        "fta": "RCEP, ACFTA, dll",
        "checks": "HS -> GACC -> product registration -> CCC -> food safety",
        "import_rules": [
            "Registrasi/perizinan GACC untuk banyak kategori barang (mis. pangan, kosmetik).",
            "CCC (China Compulsory Certification) untuk barang yang dibatasi.",
            "Import & export food safety process terpisah di GACC.",
        ],
        "export_rules": ["Cek daftar prohibited/restricted export GACC; export license mungkin wajib."],
        "documents": ["Customs declaration", "Commercial invoice", "Packing list", "CCC certificate", "Import license (bila wajib)"],
        "authorities": [{"name": "GACC", "url": "https://english.customs.gov.cn/"}],
        "verified": "2026-08-15",
    },
    "KR": {
        "customs": "Korea Customs Service (KCS); UNI-PASS; tarif HS 10 digit",
        "tariff": "MFN + preferensi FTA (IK-CEPA, RCEP, KORUS, EU-Korea); VAT 10%",
        "fta": "IK-CEPA, RCEP, KORUS",
        "checks": "HS10 -> tariff -> FTA RoO -> MFDS -> K-REACH dsb",
        "import_rules": [
            "Klasifikasi bisa s.d. 10 digit; gunakan UNI-PASS untuk deklarasi.",
            "KC (Korea Certification) diperlukan untuk produk tertentu.",
            "MFDS mengatur pangan/aditif; label Korea wajib utk banyak pangan.",
        ],
        "export_rules": ["Periksa export control Korea (KOSTA) untuk dual-use."],
        "documents": ["Import declaration (UNI-PASS)", "Invoice & packing list", "Certificate of Origin (FTA)", "KC certificate", "MFDS declaration (pangan)"],
        "authorities": [{"name": "KCS", "url": "https://www.customs.go.kr/english/"}, {"name": "UNI-PASS", "url": "https://unipass.customs.go.kr/"}],
        "verified": "2026-08-15",
    },
    "IN": {
        "customs": "ITC(HS) DGFT; India Customs",
        "tariff": "Tarif India tergolong tinggi; GST 18% (umum); cek ITC(HS) status free/restricted/prohibited",
        "fta": "AIFTA, RCEP (bukan anggota), CEPA bilateral",
        "checks": "ITC(HS) -> policy status -> SCOMET -> GST -> BIS/dll",
        "import_rules": [
            "ITC(HS) mengklasifikasi barang free / restricted / prohibited untuk import & export.",
            "SCOMET: lisensi ekspor barang strategic/dual-use dari DGFT.",
            "Sertifikasi BIS mungkin wajib untuk kategori produk tertentu.",
        ],
        "export_rules": ["Cek ITC(HS) policy & SCOMET sebelum mengekspor barang sensitif."],
        "documents": ["Bill of entry", "Commercial invoice", "Packing list", "ITC(HS) policy copy", "License (restricted/SCOMET)"],
        "authorities": [{"name": "DGFT", "url": "https://www.dgft.gov.in/"}, {"name": "India Customs", "url": "https://www.cbic.gov.in/"}],
        "verified": "2026-08-15",
    },
    "GB": {
        "customs": "HMRC; UK Integrated Online Tariff (UKGT)",
        "tariff": "UKGT (0-25% umum); Import VAT 20% (atas CIF+duty); de minimis £135 (VAT point of sale)",
        "fta": "TCA EU, CPTPP, UK-Japan, UK-Australia, UK-NZ, dst",
        "checks": "Commodity code -> UKGT -> VAT -> restrictions -> license",
        "import_rules": [
            "Commodity code 8-10 digit menentukan duty & applicable measures.",
            "Asal barang EU memenuhi TCA RoO agar duty 0% (bukan otomatis).",
            "VAT impor berlaku atas seluruh barang komersial; gunakan postponed VAT accounting bila memenuhi syarat.",
        ],
        "export_rules": ["Cek UK export licensing (strategic goods) bila relevan."],
        "documents": ["Import declaration (CDS)", "Commercial invoice", "Packing list & CoO (TCA/FTA)", "EORI number"],
        "authorities": [{"name": "UK Trade Tariff", "url": "https://www.gov.uk/trade-tariff"}, {"name": "GOV.UK import", "url": "https://www.gov.uk/import-goods-into-uk"}],
        "verified": "2026-08-15",
    },
    "CA": {
        "customs": "CBSA; Canadian Customs Tariff (10 digit); currency Code",
        "tariff": "MFN CBSA + preferensi CUSMA/CPTPP; GST/HST 5% (HST bervariasi provinsi)",
        "fta": "CUSMA, CPTPP, CETA",
        "checks": "classification -> origin -> valuation (6 metode) -> duty -> GST/HST -> permits",
        "import_rules": [
            "Klasifikasi impor 10 digit; transaction value umumnya metode valuation utama.",
            "Permit & OGD (other government departments) mungkin dibutuhkan.",
            "GST/HST dikenakan atas nilai CIF + duty.",
        ],
        "export_rules": ["Cek Canada export controls (ECCC list) utk dual-use."],
        "documents": ["Customs declaration (RMD)", "Commercial invoice", "Packing list", "Certificate of origin (CUSMA/CPTPP)", "Permits (bila relevan)"],
        "authorities": [{"name": "CBSA Tariff", "url": "https://www.cbsa-asfc.gc.ca/trade-commerce/tariff-tarif/menu-eng.html"}],
        "verified": "2026-08-15",
    },
    "AU": {
        "customs": "ABF; Australian Customs Tariff (Working Tariff)",
        "tariff": "MFN AU; GST 10% (umum); self-assessment classification",
        "fta": "IACEPA, AANZFTA, CPTPP, AUSFTA",
        "checks": "classification (self-assess) -> duty -> GST -> biosecurity",
        "import_rules": [
            "Importir melakukan self-assessment klasifikasi; kesalahan berisiko compliance.",
            "Biosecurity sangat ketat untuk tanam/hewan/makanan/kayu/organik.",
            "GST dikenakan atas nilai + duty; threshold AUD 1,000 untuk GST koleksi.",
        ],
        "export_rules": ["Periksa ABF export controls utk barang tertentu (mis. kayu, senjata)."],
        "documents": ["Import declarations", "Commercial invoice", "Packing list", "Biosecurity clearance / import permit"],
        "authorities": [{"name": "ABF", "url": "https://www.abf.gov.au/"}],
        "verified": "2026-08-15",
    },
    "NZ": {
        "customs": "NZ Customs; Working Tariff Document (efektif 1 Jul 2026)",
        "tariff": "MFN NZ; GST 15%",
        "fta": "AANZFTA, CPTPP, NZ-China, NZ-EU",
        "checks": "tariff -> duty -> GST -> MPI biosecurity",
        "import_rules": ["MPI biosecurity ketat utk produk organik/tumbuhan/hewan."],
        "export_rules": ["Export requirements ulang berlaku utk produk tertentu."],
        "documents": ["Import entry", "Commercial invoice", "Packing list", "Certificate (MPI) bila relevan"],
        "authorities": [{"name": "NZ Customs", "url": "https://www.customs.govt.nz/"}],
        "verified": "2026-08-15",
    },
    "SG": {
        "customs": "Singapore Customs; TradeNet (National Single Window)",
        "tariff": "Sebagian besar 0%; GST 9% (2024+); kontrol per kategori barang",
        "fta": "AANZFTA, RCEP, US-Singapore, EU-Singapore",
        "checks": "classification -> control list (controlled goods) -> GST",
        "import_rules": [
            "Impor via TradeNet; sebagian barang terkontrol (controlled) butuh izin.",
            "SFA mengatur pangan; halal bila mengklaim.",
        ],
        "export_rules": ["Strategic goods (SGP) screening & license bila perlu."],
        "documents": ["Import permit (TradeNet)", "Commercial invoice", "Packing list", "Certificate of origin (FTA)"],
        "authorities": [{"name": "Singapore Customs", "url": "https://www.customs.gov.sg/"}, {"name": "TradeNet", "url": "https://www.tradenet.gov.sg/"}],
        "verified": "2026-08-15",
    },
    "MY": {
        "customs": "Royal Malaysian Customs (RMCD); AHTN 8 digit; MyINTR",
        "tariff": "MFN MY + ATIGA/RCEP preferensi; SST (Sales & Service Tax)",
        "fta": "ATIGA, RCEP, MPCEPA, CPTPP",
        "checks": "HS -> duty -> ATIGA eligibility -> SST -> halal (bila relevan)",
        "import_rules": ["Import via MyINTR; sebagian barang butuh AP (Approved Permit).", "Halal certification may be expedited."],
        "export_rules": ["Export license utk barang terkontrol."],
        "documents": ["Customs declaration (MyINTR)", "Invoice & packing list", "Approved permit (bila relevan)", "Certificates"],
        "authorities": [{"name": "RMCD", "url": "https://mysst.customs.gov.my/"}, {"name": "MyINTR", "url": "https://myintr.customs.gov.my/"}],
        "verified": "2026-08-15",
    },
    "TH": {
        "customs": "Thai Customs; AHTN 8 digit; National Single Window",
        "tariff": "MFN TH + ACFTA/RCEP; VAT 7%",
        "fta": "ATIGA, ACFTA, RCEP, JTEPA, Thai-Australia",
        "checks": "HS -> duty -> FTA RoO -> FDA/FDA label -> TSLA",
        "import_rules": ["Thai FDA mengatur pangan: label Thailand wajib utk banyak produk.", "Restricted goods butuh izin impor."],
        "export_rules": ["Export license untuk barang tertentu."],
        "documents": ["Import declaration", "Invoice & packing list", "Certificate of origin (FTA)", "Permits"],
        "authorities": [{"name": "Thai Customs", "url": "https://www.customs.go.th/"}],
        "verified": "2026-08-15",
    },
    "VN": {
        "customs": "General Department of Vietnam Customs; VNACCS",
        "tariff": "MFN VN + ATIGA/AIFTA/RCEP; VAT 8-10%",
        "fta": "ATIGA, RCEP, VKFTA, EVFTA",
        "checks": "HS -> duty -> FTA -> licensing -> product standards",
        "import_rules": ["Vietnam Customs via VNACCS; izin impor untuk barang terkontrol.", "Label & standar TCVN mungkin wajib."],
        "export_rules": ["Several exports need license/permit."],
        "documents": ["Customs declaration", "Invoice & packing list", "Certificate of origin (FTA)", "Permits"],
        "authorities": [{"name": "Vietnam Customs", "url": "https://www.customs.gov.vn/"}],
        "verified": "2026-08-15",
    },
    "PH": {
        "customs": "BOC Philippines; AHTN 8 digit; e2m customs",
        "tariff": "MFN PH + ATIGA/RCEP; VAT 12%",
        "fta": "ATIGA, RCEP, PH-Japan EPA",
        "checks": "HS -> duty -> FTA -> FDA -> BOC clearance",
        "import_rules": ["FDA license untuk pangan/obat wajib sebelum import."],
        "export_rules": ["Periksa export licensing bila relevan."],
        "documents": ["Import entry", "Invoice & packing list", "FDA license", "Certificate of origin"],
        "authorities": [{"name": "BOC Philippines", "url": "https://customs.gov.ph/"}],
        "verified": "2026-08-15",
    },
    "AE": {
        "customs": "Federal Customs Authority (FCA); UAE single window",
        "tariff": "Common GCC tariff umum 5%; VAT 5%",
        "fta": "IUAE-CEPA, GAFTA",
        "checks": "HS -> GCC tariff -> ESMA -> halal -> import permit",
        "import_rules": ["Sertifikasi halal dan pendaftaran ESMA mungkin wajib utk pangan.", "Import license dari otoritas lepas Emirat kadang diminta."],
        "export_rules": ["Beberapa barang butuh izin ekspor UAE."],
        "documents": ["Customs declaration", "Invoice & packing list", "Halal certificate", "Certificate of origin"],
        "authorities": [{"name": "UAE Customs", "url": "https://www.tax.gov.ae/"}, {"name": "MoIAT ESMA", "url": "https://www.moiat.gov.ae/"}],
        "verified": "2026-08-15",
    },
    "SA": {
        "customs": "ZATCA (Zakat, Tax & Customs Authority)",
        "tariff": "Common GCC tariff 5%; VAT 15% (2020+)",
        "fta": "GAFTA, PTA dengan beberapa negara",
        "checks": "HS -> GCC tariff -> SASO -> halal/SFDA -> import permit",
        "import_rules": ["SFDA & SASO registrasi produk bisa wajib.", "Label Arab + halal certificate utk pangan."],
        "export_rules": ["Export kontrol utk barang tertentu."],
        "documents": ["Customs declaration", "Invoice & packing list", "Halal/SFDA certificate", "Certificate of origin"],
        "authorities": [{"name": "ZATCA", "url": "https://zatca.gov.sa/"}, {"name": "SFDA", "url": "https://www.sfda.gov.sa/"}],
        "verified": "2026-08-15",
    },
    "DE": {
        "customs": "German Customs (Zoll); EU TARIC/ECT",
        "tariff": "CET MFN + FTA preferensi; USt (VAT) 19%",
        "fta": "Semua FTA EU",
        "checks": "TARIC -> duty -> CE -> product rules -> VAT",
        "import_rules": ["CE marking & dokumentasi teknis wajib utk banyak produk.", "USt-IdNr untuk VAT intra-EU."],
        "export_rules": ["Export control (dual-use) sesuai aturan EU."],
        "documents": ["Import declaration (ATLAS)", "Invoice & packing list", "CE docs", "CoO bila FTA"],
        "authorities": [{"name": "German Customs", "url": "https://www.zoll.de/"}],
        "verified": "2026-08-15",
    },
    "FR": {
        "customs": "French Customs (douane)",
        "tariff": "CET MFN; TVA 20%",
        "fta": "Semua FTA EU + Accra",
        "checks": "TARIC -> duty -> CE -> imports permit -> TVA",
        "import_rules": ["CE & dokumentasi teknis wajib utk banyak produk.", "TVA dibayar saat import."],
        "export_rules": ["Export control EU untuk dual-use."],
        "documents": ["Import declaration (DELTA)", "Invoice & packing list", "CoO bila FTA"],
        "authorities": [{"name": "Douane", "url": "https://www.douane.gouv.fr/"}],
        "verified": "2026-08-15",
    },
    "NL": {
        "customs": "Dutch Customs (Belastingdienst/Douane)",
        "tariff": "CET MFN; BTW 21%",
        "fta": "Semua FTA EU",
        "checks": "TARIC -> duty -> CE -> BTW",
        "import_rules": ["CE marking & dokumentasi teknis wajib utk banyak produk.", "Rotterdam: transit & bonded warehouse fleksibel."],
        "export_rules": ["Export control EU untuk dual-use."],
        "documents": ["Import declaration", "Invoice & packing list", "CoO bila FTA"],
        "authorities": [{"name": "Dutch Customs", "url": "https://www.belastingdienst.nl/"}],
        "verified": "2026-08-15",
    },
    "BR": {
        "customs": "Receita Federal; Siscomex",
        "tariff": "AEC MERCOSUR (II) + ICMS (17-25%); IPI untuk beberapa barang",
        "fta": "MERCOSUR; Aladi",
        "checks": "NCM -> II -> ICMS -> ANVISA -> INMETRO",
        "import_rules": ["NCM 8 digit menentukan tarif & kontrol (ANVISA/INMETRO).", "Imposto de Importação atas CIF; ICMS atas basis tertentu."],
        "export_rules": ["Export control EUA/mercadoria sensitif."],
        "documents": ["Import declaration (DI)", "Invoice & packing list", "NCM code", "CIV/ANVISA bila relevan"],
        "authorities": [{"name": "Receita Federal", "url": "https://www.gov.br/receitafederal/"}, {"name": "MERCOSUR NCM", "url": "https://www.mercosur.int/"}],
        "verified": "2026-08-15",
    },
    "ZA": {
        "customs": "SARS Customs",
        "tariff": "MFN RSA + preferensi (SACU/AfCFTA); VAT 15%",
        "fta": "SACU, AfCFTA, EFTA-RSA, EU SADC EPA",
        "checks": "HS -> duty -> SACU -> VAT -> biosecurity",
        "import_rules": ["SARS customs engine menghitung duty + VAT 15%.", "Import permit utk barang terkontrol."],
        "export_rules": ["Export control & ITAC permits utk barang tertentu."],
        "documents": ["Customs declaration (SAD500)", "Invoice & packing list", "Permits", "CoO bila FTA"],
        "authorities": [{"name": "SARS", "url": "https://www.sars.gov.za/"}],
        "verified": "2026-08-15",
    },
    "TR": {
        "customs": "Turkish Customs (Ticaret Bakanlığı)",
        "tariff": "CCT Turkey + FTA; KDV 20%",
        "fta": "CU dengan EU (goods)", 
        "checks": "HS -> duty -> CE -> KDV -> import permit",
        "import_rules": ["Turkish Customs & CU dengan EU utk sebagian besar industri.", "CE & kontrol utk barang tertentu."],
        "export_rules": ["Export license utk barang tertentu."],
        "documents": ["Customs declaration", "Invoice & packing list", "CoO bila CU/FTA"],
        "authorities": [{"name": "Ticaret Bakanlığı", "url": "https://www.ticaret.gov.tr/"}],
        "verified": "2026-08-15",
    },
    "CH": {
        "customs": "Swiss Federal Customs Administration (FCA)",
        "tariff": "Swiss Customs Tariff; VAT 8.1%",
        "fta": "EFTA-FTA, CH-Indonesia CEPA (berlaku) & IECEPA",
        "checks": "HS -> duty -> CH tarif -> label -> IQ",
        "import_rules": ["Swiss label EU-aligned untuk banyak produk.", "CH-Indonesia CEPA beri preferensi bila RoO dipenuhi."],
        "export_rules": ["Export license bila relevan."],
        "documents": ["Customs declaration (NCTS)", "Invoice & packing list", "CoO bila FTA"],
        "authorities": [{"name": "Swiss Customs", "url": "https://www.bazg.admin.ch/"}],
        "verified": "2026-08-15",
    },
    "EG": {
        "customs": "Egypt Customs Authority (ECA)",
        "tariff": "MFN EG + preferensi (COMESA, PAFTA); VAT 14%",
        "fta": "COMESA, PAFTA, EU-Egypt Association",
        "checks": "HS -> duty -> VAT -> import permit",
        "import_rules": ["Import permit utk beberapa produk.", "Label & kontrol teknis mungkin wajib."],
        "export_rules": ["Export license utk barang tertentu."],
        "documents": ["Customs declaration", "Invoice & packing list", "Permits"],
        "authorities": [{"name": "Egypt Customs", "url": "https://www.customs.gov.eg/"}],
        "verified": "2026-08-15",
    },
    "NG": {
        "customs": "Nigeria Customs Service (NCS)",
        "tariff": "ECOWAS CET + MFN NG; VAT 7.5%",
        "fta": "ECOWAS CET, AfCFTA",
        "checks": "HS -> CET -> duty -> SONCAP -> import permit",
        "import_rules": ["SONCAP untuk banyak produk impor.", "Import ban utk barang tertentu."],
        "export_rules": ["Export license utk barang tertentu."],
        "documents": ["Customs declaration", "Invoice & packing list", "SONCAP certificate"],
        "authorities": [{"name": "Nigeria Customs", "url": "https://customs.gov.ng/"}],
        "verified": "2026-08-15",
    },
    "RU": {
        "customs": "FCS Russia; EAEU CN FEA",
        "tariff": "Common Customs Tariff EAEU; VAT 20%",
        "fta": "EAEU",
        "checks": "HS -> EAEU tariff -> import permit -> SANCTIONS & restricted parties",
        "import_rules": ["Layer ekstra: sanctions & restricted parties wajib di-screen mendekati transaksi.", "Produk ekspor/impor tertentu dikontrol ketat."],
        "export_rules": ["Export control (dual use) + re-export & end-user screening sangat penting."],
        "documents": ["Customs declaration", "Invoice & packing list", "Certificate of origin", "Control licenses"],
        "authorities": [{"name": "EEC EAEU", "url": "https://eec.eaeunion.org/"}, {"name": "FCS Russia", "url": "https://customs.gov.ru/"}],
        "verified": "2026-08-15",
        "sanctions_warning": "Transaksi dengan Rusia tunduk pada rezim sanksi internasional yang berubah cepat; screen pihak & bank sebelum proses.",
    },
    "CO": {
        "customs": "DIAN Colombia",
        "tariff": "MFN CO; IVA 19%",
        "fta": "Colombia-US, Colombia-EU, Colombia-Korea",
        "checks": "HS -> duty -> IVA -> import permit",
        "import_rules": ["Import license (registro) untuk beberapa barang."],
        "export_rules": ["Export control bila relevan."],
        "documents": ["Customs declaration", "Invoice & packing list", "Permits"],
        "authorities": [{"name": "DIAN", "url": "https://www.dian.gov.co/"}],
        "verified": "2026-08-15",
    },
    "MX": {
        "customs": "SAT Mexico",
        "tariff": "MFN MX + USMCA; IVA 16%",
        "fta": "USMCA, CPTPP, EU-Mexico",
        "checks": "HS -> duty -> USMCA RoO -> IVA -> NOM",
        "import_rules": ["NOM (standar) wajib utk banyak kategori.", "Port import dgn padron (list importer) mungkin."],
        "export_rules": ["Export license bila relevan."],
        "documents": ["Pedimento", "Invoice & packing list", "Certificado de origen (USMCA)"],
        "authorities": [{"name": "SAT", "url": "https://www.sat.gob.mx/"}],
        "verified": "2026-08-15",
    },
    "AR": {
        "customs": "AFIP Argentina",
        "tariff": "AEC MERCOSUR (II) + percepciones; VAT 21%",
        "fta": "MERCOSUR, Aladi",
        "checks": "NCM -> II -> IVA -> percepciones -> ANMAT",
        "import_rules": ["NCM menentukan tarif; ANMAT untuk pangan/obat.", "Percepciones pajak impor (PAIS/dll) menambah biaya."],
        "export_rules": ["Export permit (DJVE) untuk banyak barang."],
        "documents": ["Import declaration (SIMPLE)", "Invoice & packing list", "DJVE (ekspor)"],
        "authorities": [{"name": "AFIP", "url": "https://www.afip.gob.ar/"}],
        "verified": "2026-08-15",
    },
    "KE": {
        "customs": "Kenya Revenue Authority (KRA)",
        "tariff": "EAC CET + KRA; VAT 16%",
        "fta": "EAC CET, AfCFTA",
        "checks": "HS -> CET -> duty -> KEBs -> import permit",
        "import_rules": ["EAC CET band 0/10/25/35; cek sensitif list.", "Import permit untuk beberapa barang."],
        "export_rules": ["Export invoice & permit bila wajib."],
        "documents": ["Customs declaration (Simba)", "Invoice & packing list", "Permits"],
        "authorities": [{"name": "KRA", "url": "https://www.kra.go.ke/"}],
        "verified": "2026-08-15",
    },
}

# ----------------------------------------------------------------------------
# TEMPLATE REGIONAL untuk negara yang belum punya profil detail
# ----------------------------------------------------------------------------
REGIONAL_TEMPLATES: dict[str, dict[str, Any]] = {
    "Asia": {
        "note": "Negara Asia umumnya mengikuti HS, menerapkan MFN nasional, pajak konsumsi (VAT/GST 5-12%), dan serangkaian persyaratan labeling/standar.",
        "import_rules": ["Cek tarif MFN nasional via portal bea cukai setempat.", "Persyaratan label & standar (SPS/TBT) bisa wajib per kategori produk.", "Sebagian barang butuh izin impor/lisensi."],
        "export_rules": ["Cek daftar barang terkontrol bea cukai nasional.", "COO bila klaim FTA."],
        "documents": ["Customs declaration", "Commercial invoice", "Packing list", "Certificate of origin (bila FTA)"],
    },
    "Europe": {
        "note": "Non-EU Eropa mengikuti HS + sistem nasional; CE/standar EU sering diterima; VAT 19-27%.",
        "import_rules": ["Cek tarif nasional & persyaratan CE/standar.", "VAT lokal dikenakan saat impor."],
        "export_rules": ["Export control EU/domestik bila barang dual-use."],
        "documents": ["Import declaration", "Invoice & packing list", "CoO bila FTA"],
    },
    "Americas": {
        "note": "Benua Amerika menggunakan HS + tarif nasional (beberapa negara pakai tingkat lanjutan), IVA/GST 5-21%, dan kontrol OGD.",
        "import_rules": ["Cek tarif & toleransi waivers utk kategori tertentu.", "Standar (mis. NOM, INMETRO) mungkin wajib."],
        "export_rules": ["Export license untuk barang sensitif."],
        "documents": ["Import declaration", "Invoice & packing list", "Permits bila relevan"],
    },
    "Africa": {
        "note": "Afrika: per negara ada CET regional (EAC/ECOWAS/COMESA), SPS/biosecurity, dan preferensi AfCFTA.",
        "import_rules": ["Cek CET regional utk duty.", "SONCAP/kontrol teknis mungkin wajib utk produk tertentu."],
        "export_rules": ["Export permit untuk barang tertentu."],
        "documents": ["Import declaration", "Invoice & packing list", "Standards certificate bila relevan"],
    },
    "Oceania": {
        "note": "Negara Oceania umumnya memakai HS + sistem nasional; biosecurity dan standar labeling penting.",
        "import_rules": ["Biosecurity ketat utk produk pertanian/organik.", "GST/VAT setempat atas impor."],
        "export_rules": ["Export permit bila relevan."],
        "documents": ["Import declaration", "Invoice & packing list"],
    },
    "Middle East": {
        "note": "Timur Tengah: GCC memakai Common GCC Tariff, halal & standardisasi (SASO/ESMA) penting, VAT 5-15%.",
        "import_rules": ["Halal & standardisasi mungkin wajib utk pangan/products.", "Import license dari otoritas setempat kadang diminta."],
        "export_rules": ["Export license utk barang tertentu."],
        "documents": ["Import declaration", "Invoice & packing list", "Halal/standards certificate bila relevan"],
    },
    "default": {
        "note": "Data spesifik belum tersedia di baseline ini; gunakan hierarki: regulator nasional -> regional union -> WTO/WCO -> ITC -> UNCTAD.",
        "import_rules": ["Periksa HS & tarif via portal bea cukai nasional.", "Cek persyaratan licensing & standar dengan customs broker."],
        "export_rules": ["Cek export controls & licence bila relevan."],
        "documents": ["Customs declaration", "Commercial invoice", "Packing list"],
    },
}


# ----------------------------------------------------------------------------
# FUNGSI HELPER: bangun profil regulasi per negara
# ----------------------------------------------------------------------------
_KNOWN_REGIONS = {
    "Asia", "Europe", "Africa", "Americas", "Oceania", "Antarctic", "Middle East",
}


def _template_for(region: str) -> dict[str, Any]:
    key = region if region in REGIONAL_TEMPLATES else "default"
    if key == "default":
        # coba berbasis blok regional
        if region in _KNOWN_REGIONS or region == "Antarctic":
            return dict(REGIONAL_TEMPLATES["default"])
        return dict(REGIONAL_TEMPLATES["default"])
    return dict(REGIONAL_TEMPLATES[key])


def profile_for(country_code: str, region: str = "") -> dict[str, Any]:
    """Profil regulasi negara: profil detail bila ada, else template regional."""
    code = country_code.upper()
    if code in COUNTRY_PROFILES:
        return dict(COUNTRY_PROFILES[code])
    tpl = _template_for(region or "default")
    out = dict(tpl)
    out["_is_template"] = True
    return out


def has_profile(country_code: str) -> bool:
    return country_code.upper() in COUNTRY_PROFILES


def risk_level_for(country_code: str) -> str:
    """Indikator tingkat risiko regulasi (Low/Moderate/Elevated/High)."""
    code = country_code.upper()
    high = {"RU", "IR", "KP", "SY", "VE", "BY", "CU", "SD", "YE", "LY", "MM"}
    if code in high:
        return "High"
    if code in COUNTRY_PROFILES and COUNTRY_PROFILES[code].get("sanctions_warning"):
        return "High"
    if code in {"BR", "IN", "US", "CN", "TR", "EG", "NG", "AR"}:
        return "Elevated"
    return "Moderate" if has_profile(code) else "Low"


# ----------------------------------------------------------------------------
# REGULASI BERBASIS PRODUK (lampiran 7.1 dokumen proposal MauEkspor)
# Regulatory Key: Origin + Destination + HS + Product Attributes + End User
#                 + Incoterm + Value + FTA + Date
# ----------------------------------------------------------------------------
# HS chapter (2 digit pertama) -> daftar regulasi produk yang berlaku global.
PRODUCT_REGULATIONS: dict[str, list[dict[str, Any]]] = {
    # 09: Kopi | 18: Kakao | 40: Karet — EUDR (EU 2023/1115)
    "09": [{
        "id": "EUDR",
        "name": "EUDR — EU Deforestation Regulation",
        "ref": "Regulation (EU) 2023/1115",
        "scope": "Kopi, kakao, karet, kelapa sawit, kayu, soya, sapi (dan produk turunannya)",
        "requirement": "Produk wajib bebas deforestasi & degradasi hutan, dengan due diligence "
                       "statement + traceability geolokasi lahan produksi (plot-level coordinates).",
        "deadline": "Berlaku penuh 30 Desember 2026 (perusahaan besar); mikro/usaha kecil 30 Juni 2027.",
        "destinations": ["EU"],
        "risk_note": "±90% kakao global berasal dari petani kecil yang rentan kepatuhan (Springer, 2026). "
                     "Petani desa perlu pemetaan lahan & bukti asal sejak dini.",
        "sources": [{"name": "EU EUDR", "url": "https://environment.ec.europa.eu/topics/forests/deforestation-regulation_en"}],
    }],
    "18": [{
        "id": "EUDR",
        "name": "EUDR — EU Deforestation Regulation",
        "ref": "Regulation (EU) 2023/1115",
        "scope": "Kakao & produk turunan (butter, powder, paste)",
        "requirement": "Bebas deforestasi + due diligence + geolokasi lahan petani.",
        "deadline": "30 Desember 2026.",
        "destinations": ["EU"],
        "risk_note": "Kakao smallholder paling terdampak — siapkan pemetaan lahan petani.",
        "sources": [{"name": "EU EUDR", "url": "https://environment.ec.europa.eu/topics/forests/deforestation-regulation_en"}],
    }],
    "40": [{
        "id": "EUDR",
        "name": "EUDR — EU Deforestation Regulation",
        "ref": "Regulation (EU) 2023/1115",
        "scope": "Karet alam & produk turunan",
        "requirement": "Bebas deforestasi + due diligence + geolokasi lahan.",
        "deadline": "30 Desember 2026.",
        "destinations": ["EU"],
        "risk_note": "Traceability petani karet desa wajib disiapkan.",
        "sources": [{"name": "EU EUDR", "url": "https://environment.ec.europa.eu/topics/forests/deforestation-regulation_en"}],
    }],
    # 44: Kayu — EUDR + ISPM-15 relevan
    "44": [{
        "id": "EUDR",
        "name": "EUDR — EU Deforestation Regulation",
        "ref": "Regulation (EU) 2023/1115",
        "scope": "Kayu & produk kayu (termasuk furnitur, kerajinan kayu)",
        "requirement": "Legalitas kayu + bebas deforestasi + due diligence (timpa SVLK/EUTR).",
        "deadline": "30 Desember 2026.",
        "destinations": ["EU"],
        "risk_note": "Dokumen legalitas kayu (SVLK) + geolokasi hutan sumber.",
        "sources": [{"name": "EU EUDR", "url": "https://environment.ec.europa.eu/topics/forests/deforestation-regulation_en"}],
    }],
    # 08: Buah-buahan (manggis dll) — karantina EU
    "08": [{
        "id": "EU-PLANT-HEALTH",
        "name": "EU Plant Health Rules",
        "ref": "Regulation (EU) 2016/2031",
        "scope": "Buah & sayuran segar",
        "requirement": "Phytosanitary certificate (PC) untuk buah berisiko; cek daftar pestisida MRL EU.",
        "deadline": "Berlaku (berjalan).",
        "destinations": ["EU"],
        "risk_note": "Manggis & produk tropis: pastikan cold treatment & MRL compliance.",
        "sources": [{"name": "EU Plant Health", "url": "https://food.ec.europa.eu/plants/plant-health_en"}],
    }],
}

# Regulasi lintas-produk (berlaku untuk semua ekspor ke EU)
CROSS_PRODUCT_REGULATIONS: list[dict[str, Any]] = [
    {
        "id": "EU-PPWR",
        "name": "EU Packaging & Packaging Waste Regulation",
        "ref": "Regulation (EU) 2025/40",
        "scope": "Semua kemasan produk",
        "requirement": "Kemasan harus recyclable; larangan PFAS pada food-contact packaging; "
                       "label keterbukaan informasi daur ulang.",
        "deadline": "Berlaku 12 Agustus 2026 (penerapan bertahap).",
        "destinations": ["EU"],
        "risk_note": "Kemasan plastik/kertas bergrafik PFAS tinggi berisiko ditolak.",
        "sources": [{"name": "EU PPWR", "url": "https://environment.ec.europa.eu/topics/waste-and-recycling/packaging-waste_en"}],
    },
]


def product_regulations_for(hs_code: str, destination: str = "") -> list[dict[str, Any]]:
    """Kembalikan regulasi produk yang relevan untuk HS code (+destination opsional).

    Args:
        hs_code: Kode HS (minimal 2 digit chapter dipakai).
        destination: Kode negara tujuan (opsional — filter bila diisi;
                     negara di-resolve ke blok kepabeanan, mis. NL → EU).

    Returns:
        List regulasi (EUDR, plant health, dll) yang berlaku.
    """
    chapter = str(hs_code or "").replace(".", "").strip()[:2]
    regs: list[dict[str, Any]] = list(PRODUCT_REGULATIONS.get(chapter, []))
    regs.extend(CROSS_PRODUCT_REGULATIONS)
    if destination:
        dest = destination.upper()
        bloc = COUNTRY_CUSTOMS.get(dest, "")
        def _applies(r: dict[str, Any]) -> bool:
            targets = r.get("destinations") or []
            return not targets or dest in targets or bloc in targets
        regs = [r for r in regs if _applies(r)]
    return regs
