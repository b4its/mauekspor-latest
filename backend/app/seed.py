"""Seed helper: muat data demo ke store in-memory saat startup (jika kosong)."""
import logging

from app import db
from app.core.security import hash_password
from app.core.config import settings
from app.data import countries as country_data

logger = logging.getLogger("mauekspor.seed")


def seed_master_data() -> None:
    """Seed data MASTER FAKTUAL (bukan demo) — aman dijalankan di production.

    Hanya memuat data referensi yang bersumber dari otoritas resmi:
    - direktori negara dunia (ISO 3166, world_countries.py);
    - pointer regulasi terkurasi (trade_reference.py).

    Tidak membuat user/produk/pembeli/pesanan karangan. Dipakai baik saat
    ``seed_demo_data`` aktif maupun nonaktif, sehingga instance produksi tetap
    punya referensi regulasi tanpa data simulasi.
    """
    from app.data.trade_reference import seed_trade_reference, seed_regulatory_guide

    seed_trade_reference(db)
    # Data RIIL dari panduan 2026: regulations + knowledge_articles faktual.
    seed_regulatory_guide(db)
    if not db.loaded_records("countries"):
        for c in country_data.get_countries():
            db.insert("countries", {
                "id": db.gen_id("countries", "CTY"),
                "country_code": c["country_code"],
                "country_name": c["country_name"],
                "region": c["region"],
                "createdAt": "2026-07-01",
                "dataSource": "official_iso3166",
            })
    logger.info("Master data faktual (negara & regulasi) siap.")


def seed_if_empty():
    from app.data.trade_reference import seed_trade_reference
    # Run even when demo data has already been seeded; clean up legacy fake rules.
    seed_trade_reference(db)
    user_count = db.loaded_records("users")
    if user_count > 50:
        return  # sudah di-seed 100+

    # ---------- MASTER DATA: negara & regulasi (FAKTUAL, bukan demo) ----------
    seed_master_data()

    # ---------- AUTH / user ----------
    # Seed-if-missing: db.insert memperbarui in-place saat id sudah ada, sehingga
    # reseed saat restart akan MENIMPA edit user (termasuk ganti password). Guard.
    if not db.get("users", "U-001"):
        db.insert("users", {
            "id": "U-001", "email": settings.seed_admin_email, "fullName": "MauEkspor Admin",
            "role": "Admin", "password": hash_password(settings.seed_admin_password),
            "organization": "MauEkspor", "status": "Active", "createdAt": "2026-07-01", "lastLogin": "2026-08-06 10:58",
        })
    if not db.get("users", "U-002"):
        db.insert("users", {
            "id": "U-002", "email": settings.seed_exporter_email, "fullName": "Rizal Fahmi",
            "role": "Exporter", "password": hash_password(settings.seed_exporter_password),
            "organization": "PT Kopi Gayo Nusantara", "status": "Active", "createdAt": "2026-07-12", "lastLogin": "2026-08-06 09:20",
        })
    if not db.get("users", "U-003"):
        db.insert("users", {
            "id": "U-003", "email": "aya@hikari.example", "fullName": "Aya Nakamura",
            "role": "Buyer", "password": hash_password("buyer123"),
            "organization": "Hikari Foods Co.", "status": "Active", "createdAt": "2026-08-03", "lastLogin": "2026-08-06 08:00",
        })

    # ---------- Trade projects ----------
    db.insert("projects", {
        "id": "EXP-2408-017", "name": "Japan Coffee Trial Shipment", "buyer": "Hikari Foods Co.",
        "country": "Japan", "product": "Gayo Arabica Coffee Beans", "stage": "Compliance Review",
        "readiness": 82, "value": 42800, "risk": "Medium", "eta": "18 Sep 2026",
        "incoterm": "FOB Tanjung Priok", "hsCode": "0901.21", "port": "Tanjung Priok to Yokohama",
        "payment": "30% deposit, 70% before shipment", "updatedAt": "2026-08-06",
    })
    db.insert("projects", {
        "id": "EXP-2408-021", "name": "EU Rattan Furniture Program", "buyer": "Nordhaus Living",
        "country": "Germany", "product": "Handwoven Rattan Chair Set", "stage": "Quotation",
        "readiness": 74, "value": 96500, "risk": "High", "eta": "04 Oct 2026",
        "incoterm": "CIF Hamburg", "hsCode": "9401.53", "port": "Tanjung Perak to Hamburg",
        "payment": "LC at sight", "updatedAt": "2026-08-06",
    })
    db.insert("projects", {
        "id": "EXP-2408-026", "name": "Singapore Organic Snacks", "buyer": "Merlion Grocers",
        "country": "Singapore", "product": "Cassava Chips Sea Salt", "stage": "Documents",
        "readiness": 91, "value": 21800, "risk": "Low", "eta": "29 Aug 2026",
        "incoterm": "DAP Singapore DC", "hsCode": "2005.99", "port": "Belawan to Singapore",
        "payment": "Net 21 after delivery", "updatedAt": "2026-08-06",
    })

    # ---------- Products ----------
    db.insert("products", {
        "id": "PRD-COF-001", "name": "Gayo Arabica Coffee Beans", "category": "Food & Beverage",
        "status": "Enriched", "hs": "0901.21", "origin": "Aceh, Indonesia",
        "packaging": "250g valve bag, 24 bags per carton", "netWeight": "250g", "grossWeight": "280g",
        "moq": "2,000 bags", "leadTime": "21 days", "certificates": ["Halal", "Organic in progress", "Lab report required"],
        "readiness": 86, "updatedAt": "2026-08-06",
    })
    db.insert("products", {
        "id": "PRD-FUR-014", "name": "Handwoven Rattan Chair Set", "category": "Furniture & Craft",
        "status": "Needs HS Review", "hs": "9401.52", "origin": "Central Java, Indonesia",
        "packaging": "1 set per wooden crate, 2 crates per pallet", "netWeight": "18kg", "grossWeight": "21kg",
        "moq": "120 sets", "leadTime": "35 days", "certificates": ["SVLK evidence required", "Fumigation"],
        "readiness": 64, "updatedAt": "2026-08-04",
    })
    db.insert("products", {
        "id": "PRD-SNK-006", "name": "Cassava Chips Original", "category": "Food & Beverage",
        "status": "Ready", "hs": "1905.90", "origin": "Lampung, Indonesia",
        "packaging": "80g pouch, 24 pouches per carton", "netWeight": "80g", "grossWeight": "96g",
        "moq": "10,000 pouches", "leadTime": "14 days", "certificates": ["Halal", "Nutrition facts ready"],
        "readiness": 79, "updatedAt": "2026-08-03",
    })

    # ---------- Business profiles ----------
    db.insert("business_profiles", {
        "id": "BIZ-ACEH-COF", "companyName": "PT Kopi Gayo Nusantara", "address": "Takengon, Aceh, Indonesia",
        "productionCapacity": "12,000 retail bags / month", "yearEstablished": 2018,
        "certifications": ["Halal", "Origin declaration", "Organic in progress"], "status": "Needs Review",
        "owner": "Rizal Fahmi", "readiness": 82, "updatedAt": "2026-08-05",
    })
    db.insert("business_profiles", {
        "id": "BIZ-MEDAN-SNK", "companyName": "Medan Crispy Foods", "address": "Medan, North Sumatra, Indonesia",
        "productionCapacity": "75,000 pouches / month", "yearEstablished": 2020,
        "certifications": ["Halal", "HACCP", "Nutrition facts ready"], "status": "Complete",
        "owner": "Sinta Lestari", "readiness": 94, "updatedAt": "2026-08-05",
    })

    # ---------- Export analyses ----------
    db.insert("export_analyses", {
        "id": "ANL-COF-001", "productId": "PRD-COF-001", "productName": "Gayo Arabica Coffee Beans",
        "destination": "Japan", "status": "Ready", "hsCode": "0901.21", "confidence": 91, "score": 84,
        "marketDemand": "High", "duties": "0% (JP-EPA vulnerable to rules-of-origin checks)",
        "restrictions": ["Label in Japanese", "Lab report within 12 months", "Origin declaration"],
        "recommendations": [
            {"type": "Certificate", "title": "Certificate of Origin (IJEPA)", "status": "Required", "detail": "AANZ-JEPA format."},
            {"type": "Labeling", "title": "Japanese food label", "status": "Required", "detail": "Ingredients, importer, expiry."},
            {"type": "Document", "title": "Pesticide residue report", "status": "Required", "detail": "Within 12 months."},
        ],
        "summary": "High-demand 0% duty lane; labeling evidence & origin cert scope pending.",
        "updatedAt": "2026-08-06",
    })

    # ---------- Buyers ----------
    db.insert("buyers", {
        "id": "BUY-HIKARI-JP", "name": "Hikari Foods Co.", "country": "Japan", "segment": "Specialty food importer",
        "status": "Negotiating", "fitScore": 86, "projectIds": ["EXP-2408-017"],
        "interestedProducts": ["Gayo Arabica Coffee Beans"], "estimatedAnnualValue": 185000,
        "paymentProfile": "30% deposit, 70% before shipment", "lastContact": "2026-08-05 15:40",
        "nextStep": "Send label proof and lab report timing.", "contact": {
            "name": "Aya Nakamura", "role": "Import Category Manager", "email": "aya.nakamura@hikari-foods.example", "phone": "+81 45 0000 1901",
        },
        "signals": [{"label": "RFQ urgency", "detail": "Deadline in 6 days.", "tone": "orange"}], "notes": [],
    })
    db.insert("buyers", {
        "id": "BUY-NORDHAUS-DE", "name": "Nordhaus Living", "country": "Germany", "segment": "Home-living retail chain",
        "status": "At Risk", "fitScore": 71, "projectIds": ["EXP-2408-021"],
        "interestedProducts": ["Handwoven Rattan Chair Set"], "estimatedAnnualValue": 420000,
        "paymentProfile": "LC at sight", "lastContact": "2026-08-04 10:10", "nextStep": "Resolve SVLK scope.",
        "contact": {"name": "Lena Hartmann", "role": "Sourcing Lead", "email": "lena.hartmann@nordhaus.example", "phone": "+49 40 0000 2140"},
        "signals": [{"label": "Rate expiry", "detail": "Freight quote expires in 2 days.", "tone": "red"}], "notes": [],
    })

    # ---------- Buyer requests ----------
    db.insert("buyer_requests", {
        "id": "BRQ-JP-COF-001", "buyerId": "BUY-HIKARI-JP", "productId": "PRD-COF-001",
        "subject": "Trial shipment for Gayo Arabica coffee", "status": "Matched", "destination": "Japan",
        "quantity": "2,000 bags", "deadline": "2026-08-12", "requirements": ["Japanese label", "Lab report", "FOB quote"],
    })

    # ---------- Forwarders ----------
    db.insert("forwarders", {
        "id": "FWD-NGL", "name": "Nusantara Global Logistics", "coverage": "Japan and North Asia",
        "status": "Verified", "mode": "Ocean", "onTimeRate": 92, "quoteSpeed": "4 hours",
        "lanes": ["Tanjung Priok - Yokohama", "Surabaya - Osaka"], "contact": "ops@ngl.example",
    })
    db.insert("forwarders", {
        "id": "FWD-AFN", "name": "Archipelago Freight Network", "coverage": "Europe FCL and LCL",
        "status": "In Review", "mode": "Ocean", "onTimeRate": 81, "quoteSpeed": "1 day",
        "lanes": ["Tanjung Perak - Hamburg", "Tanjung Priok - Rotterdam"], "contact": "rates@afn.example",
    })

    # ---------- Catalogs / Costing / Markets / RFQ / Quotations / Orders ----------
    db.insert("catalogs", {
        "id": "CAT-COF-JP-001", "productId": "PRD-COF-001", "projectId": "EXP-2408-017",
        "title": "Premium Gayo Arabica Coffee Beans 250g", "status": "Needs Review",
        "targetMarket": "Japan specialty importers", "moq": "2,000 bags", "leadTime": "21 days after deposit",
        "priceRange": "FOB USD 20.80-21.40 per bag", "incoterms": ["EXW", "FOB"], "readiness": 78,
        "updatedAt": "2026-08-05 11:20", "description": "Single-origin Gayo Arabica beans for specialty retail.",
        "highlights": ["Single-origin Aceh profile", "Export valve bag", "FOB quote available"],
        "specifications": [{"label": "Variety", "value": "Arabica Gayo (G1)"}, {"label": "Processing", "value": "Fully washed, sun dried"}],
        "images": 4, "variants": ["250g valve bag", "1kg bulk"],
    })
    db.insert("costing", {
        "id": "CST-JP-017", "projectId": "EXP-2408-017", "productId": "PRD-COF-001", "title": "Japan Coffee FOB Base Case",
        "destination": "Japan", "incoterm": "FOB", "currency": "USD", "status": "Ready", "margin": 22, "exchangeRate": 16250,
        "exwPrice": 39150, "fobPrice": 42800, "cifPrice": 46200, "landedCost": 51380, "profit": 10950, "confidence": 84,
        "lines": [{"category": "Production", "label": "COGS", "amount": 28500}, {"category": "Freight", "label": "Ocean LCL estimate", "amount": 3400}],
        "risks": ["Freight estimate not converted to booking"], "updatedAt": "2026-08-06",
    })
    db.insert("markets", {
        "id": "MKT-JP-COF", "productId": "PRD-COF-001", "projectId": "EXP-2408-017", "country": "Japan",
        "marketScore": 84, "complianceComplexity": "Medium", "logisticsFeasibility": 78, "estimatedMargin": 22,
        "status": "Recommended", "importValue": "$1.61B roasted/green coffee category", "growth": "+5.8% YoY",
        "tariff": "Low tariff exposure; labeling evidence required", "entryStrategy": "Specialty importer trial shipment.",
        "opportunities": ["Specialty coffee demand resilient"], "risks": ["Label proof blocked"],
        "sources": [{"name": "Japan customs import statistics", "date": "2026-07-28"}], "updatedAt": "2026-08-06",
    })
    db.insert("rfqs", {
        "id": "RFQ-0891", "projectId": "EXP-2408-017", "productId": "PRD-COF-001", "buyerName": "Hikari Foods Co.",
        "destination": "Japan", "quantity": "2,000 bags / 500 kg", "incoterm": "FOB Tanjung Priok", "status": "Matching",
        "deadline": "2026-08-12", "matchScore": 86, "requirements": ["HS 0901.21", "Japanese label"],
        "matches": [{"supplier": "PT Kopi Gayo Nusantara", "catalog": "Premium Gayo Arabica 250g", "score": 86, "reason": "Strong fit."}],
    })
    db.insert("rfqs", {
        "id": "RFQ-0892", "projectId": "EXP-2408-026", "productId": "PRD-SNK-006", "buyerName": "Merlion Grocers",
        "destination": "Singapore", "quantity": "5,000 pouches", "incoterm": "DAP Singapore DC", "status": "Quoted",
        "deadline": "2026-08-20", "matchScore": 81, "requirements": ["Halal", "Nutrition facts", "Bilingual label"],
        "matches": [{"supplier": "North Sumatra Snacks", "catalog": "Cassava Chips Sea Salt 100g", "score": 81, "reason": "Price and capacity fit."}],
    })
    db.insert("quotations", {
        "id": "Q-2408-017-A", "rfqId": "RFQ-0891", "projectId": "EXP-2408-017", "supplier": "PT Kopi Gayo Nusantara",
        "buyer": "Hikari Foods Co.", "incoterm": "FOB Tanjung Priok", "value": 42800, "currency": "USD",
        "status": "In Review", "validUntil": "2026-08-20", "margin": 22, "notes": "Pending label proof.",
        "costLines": [{"label": "COGS", "amount": 28500}, {"label": "Margin", "amount": 10950}], "updatedAt": "2026-08-06",
    })
    db.insert("quotations", {
        "id": "Q-2408-026-A", "rfqId": "RFQ-0892", "projectId": "EXP-2408-026", "supplier": "North Sumatra Snacks",
        "buyer": "Merlion Grocers", "incoterm": "DAP Singapore DC", "value": 21800, "currency": "USD",
        "status": "Accepted", "validUntil": "2026-09-05", "margin": 19, "notes": "FOB DAP Singapore, net 21 days.",
        "costLines": [{"label": "COGS", "amount": 16800}, {"label": "Margin", "amount": 5000}], "updatedAt": "2026-08-06",
    })
    db.insert("orders", {
        "id": "SO-2408-026", "quotationId": "Q-2408-026-A", "projectId": "EXP-2408-026", "buyer": "Merlion Grocers",
        "supplier": "North Sumatra Snacks", "status": "Document Prep", "incoterm": "DAP Singapore DC", "value": 21800,
        "currency": "USD", "paymentTerms": "Net 21 after delivery", "deliveryWindow": "24-29 Aug 2026", "readiness": 88,
        "lines": [{"product": "Cassava Chips Sea Salt", "quantity": "5,000 pouches", "unitPrice": 4.36, "total": 21800}],
        "checklist": [{"label": "Quotation accepted", "status": "Done"}], "updatedAt": "2026-08-06",
    })
    db.insert("orders", {
        "id": "SO-2408-017", "quotationId": "Q-2408-017-A", "projectId": "EXP-2408-017", "buyer": "Hikari Foods Co.",
        "supplier": "PT Kopi Gayo Nusantara", "status": "Confirmed", "incoterm": "FOB Tanjung Priok", "value": 42800,
        "currency": "USD", "paymentTerms": "30% deposit, 70% on shipment", "deliveryWindow": "12-18 Sep 2026", "readiness": 74,
        "lines": [{"product": "Gayo Arabica Coffee Beans", "quantity": "2,000 bags", "unitPrice": 21.4, "total": 42800}],
        "checklist": [{"label": "Quotation accepted", "status": "Done"}, {"label": "Deposit received", "status": "Done"}], "updatedAt": "2026-08-06",
    })

    # ---------- Compliance / Documents / Shipments / Payments / Tasks ----------
    db.insert("compliance_requirements", {
        "id": "REQ-COF-LBL-001", "projectId": "EXP-2408-017", "productId": "PRD-COF-001",
        "title": "Japanese nutrition and allergen label proof", "category": "Labeling", "severity": "Critical",
        "status": "Blocked", "owner": "Exporter", "due": "Tomorrow", "source": "Consumer Affairs Agency Japan",
        "sourceDate": "2026-07-30", "requiredEvidence": "Japanese label artwork + importer review",
        "currentEvidence": "English label only", "confidence": 79, "updatedAt": "2026-08-06",
    })
    db.insert("documents", {
        "id": "DOC-JP-INV-001", "projectId": "EXP-2408-017", "type": "Commercial Invoice", "status": "Ready",
        "version": "v1.2", "owner": "Operations", "updatedAt": "2026-08-05 10:42", "validationScore": 96,
        "fields": {"invoiceNo": "INV-JP-2408-017", "totalValue": "42,800", "hsCode": "0901.21"},
        "checks": [{"label": "HS matches product", "status": "Passed", "detail": "Consistent."}],
    })
    db.insert("shipments", {
        "id": "SHP-JP-017", "projectId": "EXP-2408-017", "forwarder": "Nusantara Global Logistics",
        "mode": "Ocean LCL", "route": "Tanjung Priok - Yokohama", "status": "Customs Submitted", "eta": "18 Sep 2026",
        "progress": 48, "container": "LCL / 2.4 CBM", "bookingNo": "NGL-JP-240817",
        "milestones": [{"label": "Booking Confirmed", "status": "Done"}, {"label": "Customs Submitted", "status": "Current"}],
        "updatedAt": "2026-08-06",
    })
    db.insert("payments", {
        "id": "PAY-JP-017", "orderId": "SO-2408-017", "buyer": "Hikari Foods Co.", "status": "Deposit Paid",
        "currency": "USD", "amount": 42800, "paid": 12840, "dueDate": "2026-08-20", "method": "Bank Transfer",
        "risk": "Medium", "milestones": [{"label": "30% deposit", "amount": 12840, "status": "Done"}], "updatedAt": "2026-08-06",
    })
    db.insert("tasks", {
        "id": "TSK-COF-LABEL-01", "title": "Upload Japanese label proof", "module": "Compliance",
        "projectId": "EXP-2408-017", "owner": "Exporter", "priority": "Critical", "status": "Blocked", "due": "Tomorrow",
        "description": "Required before quotation approval.", "updatedAt": "2026-08-06",
    })

    # ---------- Team / Notifications / Integrations / Templates / Automations ----------
    db.insert("team_members", {
        "id": "USR-OPS-001", "name": "Nadia Prameswari", "role": "Operations", "status": "Active",
        "email": "nadia@mauekspor.example", "lastActive": "10 minutes ago",
        "permissions": ["Orders", "Documents", "Shipments"], "workload": 78,
    })
    db.insert("notifications", {
        "id": "NTF-001", "title": "Japanese label proof blocked", "description": "Critical compliance task.",
        "module": "Compliance", "severity": "Critical", "status": "Unread", "time": "8 min ago", "href": "/tasks/TSK-COF-LABEL-01",
    })
    db.insert("integrations", {
        "id": "INT-FORWARDER", "name": "Forwarder Rate Gateway", "category": "Logistics", "status": "Connected",
        "description": "Sync freight quotes and bookings.", "lastSync": "2026-08-06 10:30", "scopes": ["Rates", "Bookings"],
    })
    db.insert("templates", {
        "id": "TPL-CI-001", "title": "Commercial Invoice Export Template", "category": "Document", "status": "Ready",
        "description": "Reusable invoice layout.", "usedBy": "Documents", "updatedAt": "2026-08-06 10:05", "fields": ["Invoice number", "Buyer"],
    })
    db.insert("automations", {
        "id": "AUT-LABEL-BLOCKER", "name": "Create task when label evidence is blocked", "trigger": "Compliance item blocked",
        "action": "Create critical task and notify", "status": "Active", "module": "Compliance", "runs": 12,
        "lastRun": "2026-08-06 09:18", "description": "Keeps blockers visible.", "updatedAt": "2026-08-06",
    })

    # ---------- Knowledge / Educational / Calendar / Messages / Billing / Support / API Keys / Files / Reports / Audit / Chat ----------
    db.insert("knowledge_articles", {
        "id": "KB-EXPORT-START", "title": "How to start an export project", "category": "Export Basics",
        "status": "Published", "readTime": "6 min", "updatedAt": "2026-08-01",
        "summary": "Practical flow from readiness to first shipment.",
        "steps": ["Create a trade project", "Attach product master data", "Review target market"],
    })
    db.insert("educational_modules", {
        "id": "EDU-START", "title": "Export Readiness Foundations", "level": "Beginner", "status": "Published",
        "lessons": 8, "completion": 72, "summary": "Learn product readiness and first shipment basics.",
    })
    db.insert("educational_articles", {
        "id": "ART-READY", "title": "How to prepare export-ready product data", "status": "Published",
        "level": "Beginner", "readMinutes": 6, "tags": ["Product", "Readiness"],
        "summary": "Capture minimum data set for HS classification.",
        "body": "Split description, weights, dimensions, and packaging into structured specs.",
    })
    db.insert("calendar_events", {
        "id": "CAL-JP-LABEL", "title": "Japanese label proof deadline", "date": "2026-08-07", "time": "10:00",
        "type": "Compliance", "status": "Blocked", "projectId": "EXP-2408-017", "owner": "Exporter",
        "description": "Label proof must be uploaded.", "updatedAt": "2026-08-06",
    })
    db.insert("messages", {
        "id": "MSG-HIKARI-LABEL", "subject": "Label proof and lab report timing", "party": "Hikari Foods Co.",
        "channel": "Email", "status": "Waiting Reply", "lastMessage": "Bilingual label review by Friday?",
        "time": "18 min ago", "linkedTo": "EXP-2408-017", "participants": ["Aya Nakamura", "Nadia Prameswari"],
    })
    db.insert("billing_records", {
        "id": "BIL-ORG-001", "plan": "Growth", "status": "Active", "amount": 99000, "currency": "USD",
        "period": "2026-08", "dueDate": "2026-08-31", "usage": [{"label": "Products", "used": 5, "limit": 50}],
        "updatedAt": "2026-08-01",
    })
    db.insert("support_tickets", {
        "id": "SUPPORT-1041", "subject": "Need help configuring bank tracking", "category": "Integration",
        "status": "Open", "priority": "High", "createdAt": "2026-08-06 11:05", "owner": "Leony Tan",
        "description": "Finance team help connecting bank tracker.",
    })
    db.insert("api_keys", {
        "id": "KEY-LOG-001", "name": "Forwarder webhook key", "prefix": "mek_live_log_", "status": "Active",
        "scopes": ["shipments:write", "rates:read"], "createdAt": "2026-08-01", "lastUsed": "2026-08-06 10:30", "owner": "Operations",
    })
    db.insert("files", {
        "id": "FIL-CI-JP", "name": "INV-JP-2408-017.pdf", "type": "Document", "status": "Verified",
        "projectId": "EXP-2408-017", "owner": "Operations", "updatedAt": "2026-08-05 10:42", "size": "184 KB",
        "tags": ["Commercial Invoice", "Japan", "Coffee"],
    })
    db.insert("reports", {
        "id": "RPT-EXEC-2408", "title": "August Export Executive Brief", "type": "Executive", "status": "Ready",
        "period": "August 2026", "owner": "Management", "updatedAt": "2026-08-06 10:20",
        "sections": ["Pipeline value", "Compliance blockers"], "insights": ["Singapore lane ready for reorder."],
    })
    db.insert("audit_events", {
        "id": "AUD-1001", "time": "2026-08-06 10:42", "actor": "AI Copilot", "action": "Generated market insight",
        "module": "Markets", "entity": "MKT-SG-SNK", "severity": "Info", "detail": "Singapore route scored 91.",
    })

    # ---------- Suppliers ----------
    db.insert("suppliers", {
        "id": "SUP-KOPI-GAYO", "name": "PT Kopi Gayo Nusantara", "location": "Aceh, Indonesia",
        "category": "Coffee processor", "status": "Verified", "capabilityScore": 88, "capacity": "12,000 retail bags / month",
        "leadTime": "21 days", "qualityScore": 91, "complianceScore": 82, "contact": "Rizal Fahmi",
        "certificates": ["Halal", "Origin declaration"], "risks": [], "nextAudit": "2026-09-12", "productIds": ["PRD-COF-001"],
    })
    db.insert("suppliers", {
        "id": "SUP-CIREBON-RATTAN", "name": "Cirebon Rattan Works", "location": "Cirebon, Indonesia",
        "category": "Furniture manufacturer", "status": "Needs Evidence", "capabilityScore": 74, "productIds": ["PRD-FUR-014"],
        "capacity": "180 sets / month", "leadTime": "45 days", "qualityScore": 78, "complianceScore": 61, "contact": "Maya Kartika",
        "certificates": ["SVLK scope pending"], "risks": [], "nextAudit": "2026-08-20",
    })

    # ---------- ENRICHMENT (produk) ----------
    db.insert("product_enrichments", {
        "id": "ENR-COF-001", "productId": "PRD-COF-001",
        "hsCodeRecommendation": "0901.21", "skuGenerated": "COF-ACE-001",
        "nameEnglishB2b": "Gayo Arabica Coffee Beans - Single Origin",
        "descriptionEnglishB2b": "Specialty single-origin arabica from the Gayo highlands, fully washed and sun dried.",
        "marketingHighlights": ["Single-origin Aceh", "Specialty grade", "Export valve bag"],
        "lastUpdatedAi": "2026-08-06 10:30",
    })
    db.insert("product_enrichments", {
        "id": "ENR-FUR-014", "productId": "PRD-FUR-014",
        "hsCodeRecommendation": "9401.52", "skuGenerated": "FUR-CIR-001",
        "nameEnglishB2b": "Handwoven Rattan Chair Set",
        "descriptionEnglishB2b": "Artisan handwoven rattan chair set from Central Java.",
        "marketingHighlights": ["Handcrafted", "SVLK compliant wood", "Durable weave"],
        "lastUpdatedAi": "2026-08-04 09:00",
    })
    db.insert("product_enrichments", {
        "id": "ENR-SNK-006", "productId": "PRD-SNK-006",
        "hsCodeRecommendation": "1905.90", "skuGenerated": "SNK-LAM-001",
        "nameEnglishB2b": "Cassava Chips Original",
        "descriptionEnglishB2b": "Crunchy cassava chips, sea salt flavor, ready for retail.",
        "marketingHighlights": ["Halal certified", "Retail pouch", "Long shelf life"],
        "lastUpdatedAi": "2026-08-03 11:00",
    })

    # ---------- MARKET INTELLIGENCE & PRICING (produk kopi) ----------
    db.insert("market_intelligence", {
        "id": "MI-COF-001", "productId": "PRD-COF-001",
        "recommendedCountries": [
            {"country": "Japan", "code": "JP", "score": 88, "reason": "Specialty coffee demand tinggi; EPA zero duty.",
             "market_size": "US$1.6B", "competition_level": "Sedang", "price_range": "Premium",
             "entry_strategy": "Trial shipment via specialty importer.",
             "forwarders": [
                 {"id": "FWD-NGL", "name": "Nusantara Global Logistics", "averageRating": 4.5,
                  "serviceTypes": ["Ocean LCL", "Customs"], "contactInfo": {"phone": "+62 21 555 0100", "email": "ops@ngl.example"}},
             ]},
            {"country": "Singapore", "code": "SG", "score": 82, "reason": "Hub re-export; regulasi labeling ringan.",
             "market_size": "US$0.4B", "competition_level": "Tinggi", "price_range": "Kompetitif",
             "entry_strategy": "Gunakan Singapore sebagai hub distribusi.",
             "forwarders": []},
        ],
        "countriesToAvoid": [{"country": "North Korea", "code": "KP", "reason": "Sanksi internasional."}],
        "marketTrends": ["Kenaikan permintaan kopi specialty", "Preferensi single-origin"],
        "competitiveLandscape": "Banyak eksportir Vietnam & Brasil; diferensiasi lewat cerita asal-usul Gayo.",
        "growthOpportunities": ["Roaster specialty Jepang", "Kemasan retail premium"],
        "risksAndChallenges": ["Kepatuhan label Bahasa Jepang", "Fluktuasi freight"],
        "overallRecommendation": "Fokus pada Jepang & Singapura sebagai pasar awal.",
        "generatedAt": "2026-08-06 10:35",
    })
    db.insert("pricing_results", {
        "id": "PRC-COF-001", "productId": "PRD-COF-001",
        "cogsPerUnitIdr": 28500, "targetMarginPercent": 22, "targetCountryCode": "JP",
        "exchangeRateUsed": 15800, "exwPrice": 2.20, "fobPrice": 2.44, "cifPrice": 2.66,
        "pricingInsight": "Harga kompetitif untuk segmen specialty; pastikan margin menutup biaya label.",
        "pricingBreakdown": {"HPP (IDR)": 28500, "Margin": "22%", "EXW": 2.20, "FOB": 2.44, "CIF": 2.66},
        "generatedAt": "2026-08-06 10:40",
    })

    # ---------- CHAT SESSION ----------
    db.insert("chat_sessions", {
        "id": "CHS-001", "title": "Japan coffee compliance guidance",
        "messages": [
            {"role": "user", "text": "Apa yang menghalangi pengiriman kopi ke Jepang?"},
            {"role": "ai", "text": "Bukti label Bahasa Jepang dan laporan lab diperlukan sebelum quotation disetujui."},
        ],
        "createdAt": "2026-08-06 11:20", "updatedAt": "2026-08-06 11:22",
    })

    # ---------- BUYER PROFILE & FORWARDER PROFILE (demo) ----------
    db.insert("buyer_profiles", {
        "id": "BYP-001", "userId": "U-003",
        "companyName": "Hikari Foods Co.", "companyDescription": "Specialty food importer based in Yokohama.",
        "contactInfo": {"name": "Aya Nakamura", "email": "aya.nakamura@hikari-foods.example", "phone": "+81 45 0000 1901"},
        "preferredProductCategories": ["Makanan Olahan", "Minuman"],
        "preferredProductCategoriesDescription": "Kopi specialty dan makanan ringan premium.",
        "sourceCountries": ["Indonesia", "Vietnam"],
        "sourceCountriesDescription": "Utama dari Indonesia.",
        "businessType": "Importer / Distributor",
        "businessTypeDescription": "Importir dan distributor ritel.",
        "annualImportVolume": "US$1-5M",
        "annualImportVolumeDescription": "Volume impor tahunan 1-5 juta USD.",
        "createdAt": "2026-08-03",
    })
    db.insert("forwarder_profiles", {
        "id": "FWP-001", "userId": "U-002",
        "companyName": "Nusantara Global Logistics", "contactInfo": {"email": "ops@ngl.example", "phone": "+62 21 555 0100"},
        "specializationRoutes": ["ID-JP", "ID-SG"], "serviceTypes": ["Ocean Freight", "Customs Brokerage"],
        "averageRating": 4.5, "totalReviews": 2,
        "createdAt": "2026-07-15",
    })
    db.insert("forwarder_reviews", {
        "id": "REV-001", "forwarderId": "FWD-NGL", "rating": 5, "reviewText": "Proses booking cepat dan komunikatif.",
        "umkmId": "U-002", "reviewerName": "Rizal Fahmi", "createdAt": "2026-08-01",
    })
    db.insert("forwarder_reviews", {
        "id": "REV-002", "forwarderId": "FWD-NGL", "rating": 4, "reviewText": "Rate kompetitif, update tracking rutin.",
        "umkmId": "U-002", "reviewerName": "Sinta Lestari", "createdAt": "2026-08-04",
    })

    # ---------- LARGE SEED: 100 records per table ----------
    try:
        from app.seed_large import seed_100_records
        seed_100_records()
    except ImportError:
        logger.info("seed_large.py tidak ditemukan — skipping 100-record seed")

    # ---------- KOMODITAS DESA: kurasi kopi, kakao, rempah, rotan, HHNK ----------
    try:
        from app.seed_village_commodities import seed_village_commodities
        seed_village_commodities()
    except ImportError:
        logger.info("seed_village_commodities.py tidak ditemukan — skipping village commodities seed")


def _seed_educational_lessons():
    """Seed pelajaran edukasi (termasuk lesson kuis) per modul desa.

    Dipanggil dari seed_village_commodities setelah modul desa dibuat. Materi
    tiap lesson memuat istilah kunci topik modul sehingga bank soal kuis
    (`app.services.quiz`) dapat memilih soal yang relevan.
    """
    if db.loaded_records("educational_lessons") > 0:
        return
    lessons = [
        # EDU-DES-PANEN-01 — karantina / phytosanitary
        {"id": "LSN-DES-PANEN-01", "moduleId": "EDU-DES-PANEN-01", "title": "Kenali komoditas & hama karantina",
         "kind": "Video", "duration": "5 min",
         "content": "Hasil panen segar wajib melewati karantina pertanian. Kenali media pembawa, hama penyakit, dan syarat phytosanitary negara tujuan.",
         "keyPoints": ["Identifikasi jenis komoditas & hama", "Karantina pertanian menerbitkan phytosanitary", "Sampel & pemeriksaan lapangan"]},
        {"id": "LSN-DES-PANEN-02", "moduleId": "EDU-DES-PANEN-01", "title": "Mengurus Sertifikat Kesehatan Tumbuhan",
         "kind": "Reading", "duration": "6 min",
         "content": "Alur permohonan sertifikat kesehatan tumbuhan: surat permohonan, data komoditas, negara tujuan, jadwal pemeriksaan sebelum kontainer ditutup.",
         "keyPoints": ["Ajukan ke Badan Karantina Pertanian", "Lampirkan sertifikat ke dokumen ekspor"]},
        {"id": "LSN-DES-PANEN-07", "moduleId": "EDU-DES-PANEN-01", "title": "Kuis: karantina hasil panen",
         "kind": "Quiz", "duration": "4 min",
         "content": "Kuis singkat seputar karantina pertanian, phytosanitary, dan dokumen hasil panen segar.",
         "keyPoints": ["Ulangi jenis dokumen karantina", "Ulangi alur pemeriksaan"]},
        # EDU-DES-HALAL-02 — sertifikasi halal
        {"id": "LSN-DES-HALAL-01", "moduleId": "EDU-DES-HALAL-02", "title": "Bahan & proses produksi halal",
         "kind": "Video", "duration": "5 min",
         "content": "Sertifikasi halal menilai bahan, pemasok, dan proses produksi (PPH). Pahami requirement negara tujuan seperti GAC/SMAS di Timur Tengah.",
         "keyPoints": ["Kumpulkan daftar bahan & pemasok", "Amankan proses produksi halal", "Cek requirement negara tujuan"]},
        {"id": "LSN-DES-HALAL-06", "moduleId": "EDU-DES-HALAL-02", "title": "Kuis: sertifikasi halal",
         "kind": "Quiz", "duration": "4 min",
         "content": "Kuis singkat seputar sertifikasi halal, label, dan persyaratan pasar Timur Tengah.",
         "keyPoints": ["Ulangi alur SIHALAL", "Ulangi label halal"]},
        # EDU-DES-KEMAS-03 — pengemasan
        {"id": "LSN-DES-KEMAS-01", "moduleId": "EDU-DES-KEMAS-03", "title": "Hitung dimensi & container loading",
         "kind": "Reading", "duration": "6 min",
         "content": "Teknik packing kriya rotan, kayu, dan tekstil agar selamat perjalanan laut. Hitung dimensi karton, dunnage, stacking limit, dan moisture barrier.",
         "keyPoints": ["Hitung dimensi karton & loading", "Gunakan silica gel & wrapping", "Foto kondisi packing sebagai bukti"]},
        {"id": "LSN-DES-KEMAS-05", "moduleId": "EDU-DES-KEMAS-03", "title": "Kuis: standar pengemasan ekspor",
         "kind": "Quiz", "duration": "4 min",
         "content": "Kuis singkat seputar standar pengemasan (packaging) kriya untuk pengiriman laut.",
         "keyPoints": ["Ulangi standar packaging", "Ulangi bukti klaim asuransi"]},
        # EDU-DES-NIB-04 — legalitas NIB/IUMK
        {"id": "LSN-DES-NIB-01", "moduleId": "EDU-DES-NIB-04", "title": "Registrasi OSS-RBA & KBLI",
         "kind": "Video", "duration": "5 min",
         "content": "Urusan legalitas dasar: Nomor Induk Berusaha (NIB) dan IUMK lewat OSS-RBA, isi KBLI sesuai komoditas, dan fasilitas kepabeanan bagi UMK.",
         "keyPoints": ["Siapkan akta & NPWP", "Isi KBLI 5 digit", "Unduh NIB & IUMK"]},
        {"id": "LSN-DES-NIB-06", "moduleId": "EDU-DES-NIB-04", "title": "Kuis: legalitas & dokumen usaha",
         "kind": "Quiz", "duration": "4 min",
         "content": "Kuis singkat seputar NIB, IUMK, dan dokumen legalitas ekspor.",
         "keyPoints": ["Ulangi NIB vs IUMK", "Ulangi fasilitas bea cukai UMK"]},
        # EDU-DES-DOC-05 — dokumen wajib per negara
        {"id": "LSN-DES-DOC-01", "moduleId": "EDU-DES-DOC-05", "title": "Checklist dokumen per negara",
         "kind": "Reading", "duration": "7 min",
         "content": "Dokumen wajib ekspor ke Singapura dan Jepang: commercial invoice, packing list, COO Form D/AI, phytosanitary, health certificate, dan label Jepang.",
         "keyPoints": ["Dokumen dasar semua negara", "COO Form D & SFA untuk Singapura", "Label Bahasa Jepang & JEPA untuk Jepang"]},
        {"id": "LSN-DES-DOC-08", "moduleId": "EDU-DES-DOC-05", "title": "Kuis: dokumen ekspor",
         "kind": "Quiz", "duration": "4 min",
         "content": "Kuis singkat seputar dokumen (invoice, packing list, COO, sertifikat) untuk ekspor.",
         "keyPoints": ["Ulangi rekonsiliasi invoice & packing list", "Ulangi sertifikat asal"]},
        # EDU-DES-KARANTINA-06 — regulasi karantina
        {"id": "LSN-DES-KARANTINA-01", "moduleId": "EDU-DES-KARANTINA-06", "title": "PP 28/2024 & tindakan karantina",
         "kind": "Video", "duration": "5 min",
         "content": "Memahami PP 28/2024 tentang karantina hewan, ikan, dan tumbuhan: penggolongan media pembawa, wilayah karantina, dan tindakan P4/PK/PKHP.",
         "keyPoints": ["Golongan MHK/MKH/TIK", "Tindakan karantina P4/PK/PKHP", "Biaya & layanan cepat karantina"]},
        {"id": "LSN-DES-KARANTINA-05", "moduleId": "EDU-DES-KARANTINA-06", "title": "Kuis: regulasi karantina",
         "kind": "Quiz", "duration": "4 min",
         "content": "Kuis singkat seputar regulasi karantina (compliance) PP 28/2024.",
         "keyPoints": ["Ulangi golongan media pembawa", "Ulangi tindakan karantina"]},
        # EDU-DES-CITES-07 — CITES & legalitas bahan
        {"id": "LSN-DES-CITES-01", "moduleId": "EDU-DES-CITES-07", "title": "CITES & legalitas bahan baku",
         "kind": "Reading", "duration": "6 min",
         "content": "Untuk kriya dari kayu, rotan, dan bahan alam: pastikan bahan bukan spesies dilindungi CITES (cek appendix) dan siapkan legalitas bahan (SVLK).",
         "keyPoints": ["Cek appendix CITES", "Legalitas bahan baku SVLK", "Dokumen asal-usul bahan"]},
        {"id": "LSN-DES-CITES-06", "moduleId": "EDU-DES-CITES-07", "title": "Kuis: CITES & dokumen asal bahan",
         "kind": "Quiz", "duration": "4 min",
         "content": "Kuis singkat seputar CITES, legalitas kayu, dan sertifikat asal bahan baku.",
         "keyPoints": ["Ulangi CITES appendix", "Ulangi legalitas bahan"]},
    ]
    for lesson in lessons:
        db.insert("educational_lessons", {
            **lesson,
            "orderIndex": 0,
            "createdAt": "now",
            "updatedAt": "now",
        })
