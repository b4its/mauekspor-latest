"""Curated research pointers from guideline/PANDUAN-REGULASI-EKSPOR-IMPOR-2026.md.

This snapshot is not a tariff schedule. Do not infer a duty or legal clearance
from a chapter-level HS match: consult the linked authority for national HS,
origin, product attributes, transaction date and any applicable exceptions.

Every record here is a *verification task* traceable to an official source,
never an automatic eligibility finding. Anything that could not be confirmed
against a primary source is deliberately omitted rather than guessed.
"""

from __future__ import annotations

SNAPSHOT_DATE = "2026-09-29"
GUIDE = "guideline/PANDUAN-REGULASI-EKSPOR-IMPOR-2026.md"

# Keep these records actionable and traceable. No invented prohibitions or
# rates: these are verification tasks, never automatic eligibility findings.
TRADE_RULES = (
    # ── Indonesia ──────────────────────────────────────────────────────────
    ("ID", "Documentation", "BTKI 2022 / PMK 26/PMK.010/2022: klasifikasi sampai 8 digit dan cek tarif/lartas di INSW sebelum PIB/PEB.", "https://www.insw.go.id/", "PMK 26/PMK.010/2022"),
    ("ID", "Documentation", "Impor: cek Permendag 16/2025 beserta regulasi sektoral (17/2025 tekstil, 18/2025 pertanian/peternakan, 19/2025 garam/perikanan); izin PI/LS sesuai barang di OSS/SINSW.", "https://jdih.kemendag.go.id/", "Permendag 16/2025"),
    ("ID", "Documentation", "Ekspor: cek lartas setelah perubahan Permendag 5/2026 dan larangan ekspor setelah Permendag 6/2026 (berlaku 1 April 2026); jangan anggap seluruh produk memerlukan PE.", "https://jdih.kemendag.go.id/", "Permendag 5/2026; Permendag 6/2026"),
    ("ID", "Documentation", "DHE SDA: PP 21/2026 (perubahan terbaru atas PP 36/2023) berlaku 1 Juni 2026 — repatriasi 100%, penempatan nonmigas 100% minimal 12 bulan, migas 30% minimal 3 bulan; verifikasi sebelum menetapkan kewajiban penempatan.", "https://peraturan.bpk.go.id/", "PP 36/2023; PP 21/2026"),
    ("ID", "Documentation", "Bea keluar komoditas (sawit/CPO, mineral olahan, kayu, kakao, dll.) mengacu PMK per komoditas; batu bara/emas: jangan asumsikan tarif tanpa PMK final yang berlaku.", "https://jdih.kemenkeu.go.id/", "PMK 68/2025 (dan PMK terkait)"),
    ("ID", "Documentation", "Barang kiriman (e-commerce/kurir): PMK 96/2023 jo. PMK 4/2025 — bebas BM ≤ USD 3, tarif flat umumnya 7,5% untuk USD 3–1.500, dan ketentuan impor umum di atasnya.", "https://jdih.kemenkeu.go.id/", "PMK 96/2023; PMK 4/2025"),
    ("ID", "Documentation", "Hilirisasi: larangan ekspor bijih nikel (2020), bauksit (2023), dan konsentrat tembaga; cek ketentuan terbaru Kementerian ESDM/Kemendag.", "https://jdih.esdm.go.id/", "Kebijakan hilirisasi minerba"),
    # ── United States ──────────────────────────────────────────────────────
    ("US", "Documentation", "Cek HTSUS termasuk Chapter 99, Section 301/232 dan AD/CVD untuk HS, asal dan tanggal impor; tarif IEEPA historis tidak boleh dipakai sebagai tarif kini (dibatalkan Mahkamah Agung AS, 20 Feb 2026).", "https://hts.usitc.gov/", "HTSUS / Chapter 99"),
    ("US", "Documentation", "Section 301 'forced labor' (berlaku 24 Jul 2026) menambah tarif di atas MFN (Indonesia 10%); cek daftar HTS per negara ART dan pengecualian. Status dalam sengketa di CIT (sidang 30 Sep 2026) — verifikasi sebelum menghitung landed cost.", "https://www.cbp.gov/trade/automated/csms", "CBP CSMS / Federal Register"),
    ("US", "Documentation", "De minimis USD 800 ditangguhkan untuk semua negara (29 Agu 2025; ditetapkan tanpa batas waktu via Interim Final Rules 24 Jun 2026); cek CSMS sebelum mengirim barang kiriman.", "https://www.cbp.gov/trade/automated/csms", "CBP CSMS"),
    ("US", "Documentation", "Section 232: baja/aluminium 50% atas nilai penuh (sejak 6 Apr 2026); cek Annex I-A/I-B dan tarif produk turunan terkini di HTSUS Chapter 99.", "https://hts.usitc.gov/", "Section 232 / HTSUS Ch.99"),
    ("US", "Documentation", "Agreement on Reciprocal Trade (ART) AS–Indonesia ditandatangani 19 Feb 2026 (tarif resiprokal 19%, produk tertentu 0% per Schedule 2B); cek HTS khusus per negara.", "https://ustr.gov/", "ART AS–Indonesia"),
    # ── Canada ─────────────────────────────────────────────────────────────
    ("CA", "Documentation", "ICA-CEPA: penandatanganan/ratifikasi bukan otomatis tarif preferensi; verifikasi tanggal berlaku setelah pertukaran nota diplomatik dan aturan asal barang.", "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/", "ICA-CEPA (SI/2026-30)"),
    # ── United Kingdom ─────────────────────────────────────────────────────
    ("GB", "Documentation", "Cek kode tarif impor nasional 10 digit dan status UK CBAM (sektor aluminium, semen, pupuk, hidrogen, besi & baja; mulai 1 Jan 2027) per produk/tanggal transaksi.", "https://www.trade-tariff.service.gov.uk/", "UK Global Tariff / UK CBAM"),
    # ── Mexico ─────────────────────────────────────────────────────────────
    ("MX", "Documentation", "Tarif 5–50% atas 1.463 pos tarif dari negara non-FTA (termasuk Indonesia) sejak 1 Jan 2026; cek kode tarif nasional dan bea tambahan sebelum menghitung landed cost.", "https://www.sat.gob.mx/", "Mexico customs tariff"),
    # ── Japan ──────────────────────────────────────────────────────────────
    ("JP", "Documentation", "Cek Japan Customs, IJEPA/RCEP beserta rules of origin dan ketentuan MAFF/MHLW untuk pangan (label bahasa Jepang, deklarasi alergen).", "https://www.customs.go.jp/english/", "Japan Customs / IJEPA"),
    # ── China ──────────────────────────────────────────────────────────────
    ("CN", "Documentation", "Registrasi produsen pangan luar negeri (GACC Decree 248 dan revisinya); kontrol ekspor tanah jarang Tiongkok (paket Apr 2025 tetap berlaku, paket Okt 2025 ditangguhkan hingga 10 Nov 2026).", "https://english.customs.gov.cn/", "GACC / MOFCOM Export Control Law"),
    # ── India ──────────────────────────────────────────────────────────────
    ("IN", "Documentation", "Wajib IEC; ICEGATE; BIS Quality Control Orders (QCO); cek ITC(HS) status free/restricted/prohibited dan SCOMET untuk dual-use.", "https://www.dgft.gov.in/", "DGFT / ITC(HS)"),
)

EU_RULES = (
    ("Documentation", "Cek TARIC 10 digit, preferensi GSP yang berlaku dan tindakan perdagangan untuk HS/tanggal impor; IEU-CEPA (target penandatanganan Okt 2026) yang belum berlaku tidak boleh memberi tarif preferensi.", "https://trade.ec.europa.eu/access-to-markets/en/home", "TARIC / Access2Markets"),
    ("Documentation", "CBAM: periode definitif mulai 1 Jan 2026 (besi & baja, aluminium, semen, pupuk, hidrogen, listrik); ambang de minimis 50 ton/importir/tahun; penjualan sertifikat mulai 1 Feb 2027, deklarasi pertama 30 Sep 2027. Cek Annex I/kode CN, status Authorised CBAM Declarant, dan data emisi tertanam.", "https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en", "Regulation (EU) 2023/956"),
    ("Documentation", "EUDR: berlaku 30 Des 2026 (operator besar/menengah) dan 30 Jun 2027 (mikro/kecil); cocokkan Annex I/kode CN, geolokasi lahan, legalitas, dan DDS. Delegated Act 13 Jul 2026 mengubah cakupan — verifikasi daftar terkini, tidak semua barang satu bab HS tercakup.", "https://environment.ec.europa.eu/topics/forests/deforestation-regulation_en", "Regulation (EU) 2023/1115"),
    ("Documentation", "Aturan e-commerce: mulai 1 Jul 2026 bea masuk tetap €3 per jenis barang (per kode tarif) untuk kiriman ≤ €150, sementara hingga 1 Jul 2028; pembebasan bea €150 berakhir.", "https://taxation-customs.ec.europa.eu/", "EU customs reform (temporary €3)"),
    ("Documentation", "GPSR (keamanan produk umum), REACH (kimia), CE marking, EU Batteries Regulation, PPWR (kemasan), dan Forced Labour Regulation (berlaku 2027) — cek per produk dan tanggal.", "https://ec.europa.eu/growth/single-market/ce-marking_en", "EU product & sustainability rules"),
)


# ── Struktur berikut menyediakan konteks terdalam untuk riset halaman admin/edu. ──
# Timeline peristiwa regulasi terverifikasi (sumber: guide Bagian 12 & ringkasan).
REGULATORY_TIMELINE = (
    ("2026-01-01", "CBAM UE fase definitif mulai; tarif Meksiko 5–50% untuk 1.463 pos dari negara non-FTA", "EU/MX"),
    ("2026-02-19", "Agreement on Reciprocal Trade (ART) AS–Indonesia ditandatangani (tarif resiprokal 19%)", "US"),
    ("2026-02-20", "Mahkamah Agung AS (6-3) menyatakan IEEPA tidak memberi wewenang tarif; tarif IEEPA dibatalkan", "US"),
    ("2026-03-30", "Moratorium bea e-commerce WTO (MC14) berakhir tanpa konsensus perpanjangan", "WTO"),
    ("2026-04-01", "Permendag 5/2026 & 6/2026 (deregulasi ekspor Indonesia) berlaku", "ID"),
    ("2026-04-06", "Section 232 AS: baja & aluminium 50% atas nilai penuh barang", "US"),
    ("2026-05-01", "EU–Mercosur diterapkan sementara; tarif nol Tiongkok untuk 53 negara Afrika", "EU/CN"),
    ("2026-06-01", "PP 21/2026 tentang DHE SDA berlaku (repatriasi 100%)", "ID"),
    ("2026-07-01", "UE: bea €3 per jenis barang untuk kiriman bernilai ≤ €150", "EU"),
    ("2026-07-24", "Section 301 'forced labor' AS berlaku atas 60 ekonomi (Indonesia 10%)", "US"),
    ("2026-11-10", "Batas gencatan dagang AS–Tiongkok & penangguhan kontrol tanah jarang Tiongkok", "US/CN"),
    ("2026-12-04", "Section 232 AS: tarif polysilicon & turunannya berlaku", "US"),
    ("2026-12-30", "EUDR berlaku untuk operator besar/menengah", "EU"),
    ("2027-01-01", "UK CBAM berlaku; kenaikan tarif AS untuk furnitur berkain & kabinet", "GB/US"),
    ("2027-02-01", "Penjualan sertifikat CBAM UE dimulai", "EU"),
    ("2027-06-30", "EUDR berlaku untuk operator mikro/kecil", "EU"),
    ("2027-09-30", "Deklarasi CBAM tahunan pertama UE", "EU"),
    ("2028-01-01", "HS 2028 berlaku secara global (edisi ke-8, Siklus Review ke-7 WCO)", "WCO"),
    ("2028-07-01", "Akhir masa bea sementara €3 UE (digantikan EU Customs Data Hub)", "EU"),
)

# Angka kunci HS 2028 (sumber WCO, berlaku 1 Jan 2028).
HS_2028_FACTS = {
    "effective": "2028-01-01",
    "edition": 8,
    "review_cycle": "7th Review Cycle (Jul 2019–Jun 2025)",
    "amendment_sets": 299,
    "headings_total": 1229,
    "subheadings_total": 5852,
    "headings_new": 6,
    "headings_deleted": 5,
    "subheadings_new": 428,
    "subheadings_deleted": 172,
    "highlights": (
        "Vaksin dipindah ke pos baru 30.07 & 30.08; pos baru 21.07 untuk suplemen makanan; "
        "restrukturisasi pos 39.15 untuk limbah plastik (selaras Konvensi Basel); "
        "Catatan 3 Bab 39 memperkenalkan konsep 'single-use' (sedotan, kemasan, peralatan makan, dll.); "
        "subpos baru untuk ambulans, APD, ventilator, dan alat diagnostik."
    ),
    "preparation": "WCO menyusun tabel korelasi HS 2022→2028; ASEAN/AHTN 2028 & BTKI baru menyusul; audit master data HS sejak 2027.",
    "sources": [{"name": "WCO HS 2028", "url": "https://www.wcoomd.org/"}],
}


def rules_for(country_code: str) -> list[dict]:
    """Return research pointers for a country; EU entries apply to EU members."""
    from app.data.regulatory_intel import COUNTRY_CUSTOMS

    code = (country_code or "").upper()
    rows = [row for row in TRADE_RULES if row[0] == code]
    if COUNTRY_CUSTOMS.get(code) == "EU":
        rows.extend((code, *row) for row in EU_RULES)
    return [
        {"id": f"REF-20260929-{code}-{i:02d}", "countryCode": code,
         "ruleCategory": category, "descriptionRule": description,
         "source": reference, "sourceUrl": url, "snapshotDate": SNAPSHOT_DATE,
         "reviewStatus": "research_only", "guide": GUIDE,
         "requiredSpecs": [], "forbiddenKeywords": []}
        for i, (_, category, description, url, reference) in enumerate(rows, 1)
    ]


def seed_trade_reference(db) -> None:
    """Install curated records without overwriting admin edits; retire old fake demo rows."""
    for record in db.all("regulations"):
        if (str(record.get("id", "")).startswith("REG-")
                and str(record.get("descriptionRule", "")) == f"Regulation for {record.get('countryCode')}."):
            db.delete("regulations", record["id"])
    from app.data.regulatory_intel import COUNTRY_CUSTOMS
    codes = ("ID", "US", "CA", "GB", "MX", "JP", "CN", "IN") + tuple(
        code for code, bloc in COUNTRY_CUSTOMS.items() if bloc == "EU"
    )
    for code in codes:
        for record in rules_for(code):
            if not db.get("regulations", record["id"]):
                db.insert("regulations", record)
