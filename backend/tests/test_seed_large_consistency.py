"""Regresi kualitas data seeder besar (app/seed_large.py).

Menutup tiga kelas bug yang sebelumnya bocor ke UI:
1. Produk mendapat kode HS acak yang tak berhubungan (kopi berlabel HS pisang).
2. Baris order tanpa `unitPrice` → halaman detail order menampilkan "RpNaN per unit".
3. Pembayaran dengan `paid` > `amount` → piutang negatif ("Tertunggug -Rp 1")
   dan progres terbayar > 100%.
Plus: analisis ekspor yang namanya tak sinkron dengan `productId`.
"""
from app import db
from app.main import app  # noqa: F401
from app.seed import seed_if_empty
from app.seed_large import PRODUCTS, PRODUCT_HS


def _seed():
    db.init_store()
    seed_if_empty()


def test_every_product_has_curated_hs_code():
    _seed()
    missing = [p for p in PRODUCTS if p not in PRODUCT_HS]
    assert missing == [], f"produk tanpa HS terkurasi: {missing}"
    for name, (code, desc) in PRODUCT_HS.items():
        assert str(code).isdigit(), f"{name}: kode HS bukan angka ({code!r})"
        assert 4 <= len(str(code)) <= 6, f"{name}: panjang kode HS tidak wajar ({code!r})"
        assert desc and desc.strip(), f"{name}: deskripsi HS kosong"


def test_key_products_map_to_sensible_hs_chapter():
    # Chapter HS yang paling jelas tidak boleh tertukar (regresi sample).
    expected_chapter = {
        "Kopi Arabika Gayo": "09",        # kopi
        "Kakao Fermentasi": "18",         # kakao
        "Madu Hutan Sumbawa": "04",       # madu
        "Lada Hitam": "09",               # rempah
        "Permadani Tenun": "57",          # karpet/tenun
        "Keramik Hias": "69",             # keramik
        "Rattan Anyaman": "46",           # anyaman rotan
        "Udang Vannamei": "03",           # perikanan
    }
    for name, chapter in expected_chapter.items():
        assert str(PRODUCT_HS[name][0])[:2] == chapter, f"{name} chapter HS salah"


def test_seeded_products_use_curated_hs():
    _seed()
    for product in db.all("products"):
        name = product.get("name")
        if name in PRODUCT_HS:
            assert product.get("hs") == PRODUCT_HS[name][0], f"{name} HS salah"


def test_order_lines_have_finite_unit_price():
    _seed()
    for order in db.all("orders"):
        for line in order.get("lines", []):
            assert "unitPrice" in line, f"order {order.get('id')} line tanpa unitPrice"
            assert isinstance(line["unitPrice"], (int, float)), "unitPrice bukan angka"
            assert line["unitPrice"] > 0, "unitPrice harus positif"


def test_payments_never_overpaid():
    _seed()
    for payment in db.all("payments"):
        amount = payment.get("amount", 0) or 0
        paid = payment.get("paid", 0) or 0
        assert paid <= amount, (
            f"payment {payment.get('id')} overpaid: paid={paid} > amount={amount}"
        )


def test_export_analysis_name_matches_product():
    _seed()
    products = {p["id"]: p.get("name", "") for p in db.all("products")}
    for analysis in db.all("export_analyses"):
        pid = analysis.get("productId")
        expected = products.get(pid)
        if expected:
            assert analysis.get("productName") == expected, (
                f"analysis {analysis.get('id')} nama produk tidak cocok productId "
                f"({analysis.get('productName')!r} != {expected!r})"
            )


def test_compliance_requirements_have_confidence():
    # UI menampilkan `confidence` di daftar & detail; tanpa ini muncul "%" kosong.
    _seed()
    for req in db.all("compliance_requirements"):
        assert req.get("confidence") is not None, (
            f"compliance_requirements {req.get('id')} tanpa confidence"
        )
        assert 0 <= int(req["confidence"]) <= 100


def test_compliance_requirements_have_evidence_fields():
    # Kartu "Bukti yang Diperlukan" merender requiredEvidence/currentEvidence.
    _seed()
    for req in db.all("compliance_requirements"):
        assert req.get("requiredEvidence"), (
            f"compliance_requirements {req.get('id')} tanpa requiredEvidence"
        )
        assert req.get("currentEvidence"), (
            f"compliance_requirements {req.get('id')} tanpa currentEvidence"
        )


def test_status_fields_have_healthy_distribution():
    """Regresi bug sebaran: `_pick` lama memakai `n % len` dari counter konstan
    sehingga status kolaps ke satu nilai (mis. 100 pembeli 'Qualified', 100
    supplier 'Pending'). Pastikan tiap tabel memakai lebih dari satu status."""
    _seed()
    checks = {
        "buyers": "status",
        "suppliers": "status",
        "payments": "status",
        "compliance_requirements": "status",
        "export_analyses": "status",
        "shipments": "status",
        "documents": "status",
        "quotations": "status",
        "rfqs": "status",
        "tasks": "status",
    }
    for table, field in checks.items():
        values = {str(r.get(field)) for r in db.all(table) if r.get(field)}
        assert len(values) >= 2, (
            f"{table}.{field} kolaps ke satu nilai: {values} "
            "(sebaran `_pick` tidak sehat)"
        )

