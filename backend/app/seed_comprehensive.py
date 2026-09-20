"""Seeder komprehensif untuk seluruh sistem MauEkspor.

Mengisi semua tabel database dengan data demo realistis yang saling terhubung.
Aman dipanggil berulang (idempotent).
"""
from app import db
from app.core.security import hash_password


def seed_comprehensive():
    """Seed semua tabel dengan data lengkap."""
    print("🌱 Starting comprehensive seeding...")
    
    # 1. MASTER DATA: Countries & HS Codes
    print("✓ Seeding countries...")
    _seed_countries()
    
    print("✓ Seeding HS codes (village commodities)...")
    _seed_hs_codes()
    
    # 2. USERS & AUTH
    print("✓ Seeding users...")
    _seed_users()
    
    # 3. PRODUCTS & BUSINESS PROFILES
    print("✓ Seeding products...")
    _seed_products()
    
    print("✓ Seeding business profiles...")
    _seed_business_profiles()
    
    # 4. PROJECTS & EXPORT ANALYSIS
    print("✓ Seeding projects...")
    _seed_projects()
    
    print("✓ Seeding export analyses...")
    _seed_export_analyses()
    
    # 5. BUYERS & BUYER REQUESTS
    print("✓ Seeding buyers...")
    _seed_buyers()
    
    print("✓ Seeding buyer requests...")
    _seed_buyer_requests()
    
    # 6. FORWARDERS
    print("✓ Seeding forwarders...")
    _seed_forwarders()
    
    # 7. CATALOGS & COSTING
    print("✓ Seeding catalogs...")
    _seed_catalogs()
    
    print("✓ Seeding costing...")
    _seed_costing()
    
    # 8. MARKETS & RFQS
    print("✓ Seeding markets...")
    _seed_markets()
    
    print("✓ Seeding RFQs...")
    _seed_rfqs()
    
    # 9. QUOTATIONS & ORDERS
    print("✓ Seeding quotations...")
    _seed_quotations()
    
    print("✓ Seeding orders...")
    _seed_orders()
    
    # 10. COMPLIANCE & DOCUMENTS
    print("✓ Seeding compliance requirements...")
    _seed_compliance_requirements()
    
    print("✓ Seeding documents...")
    _seed_documents()
    
    # 11. SHIPMENTS & PAYMENTS
    print("✓ Seeding shipments...")
    _seed_shipments()
    
    print("✓ Seeding payments...")
    _seed_payments()
    
    # 12. TASKS & TEAM
    print("✓ Seeding tasks...")
    _seed_tasks()
    
    print("✓ Seeding team members...")
    _seed_team_members()
    
    # 13. NOTIFICATIONS & INTEGRATIONS
    print("✓ Seeding notifications...")
    _seed_notifications()
    
    print("✓ Seeding integrations...")
    _seed_integrations()
    
    # 14. KNOWLEDGE & EDUCATIONAL
    print("✓ Seeding knowledge articles...")
    _seed_knowledge_articles()
    
    print("✓ Seeding educational modules...")
    _seed_educational_modules()
    
    print("✓ Seeding educational articles...")
    _seed_educational_articles()
    
    # 15. CALENDAR & MESSAGES
    print("✓ Seeding calendar events...")
    _seed_calendar_events()
    
    print("✓ Seeding messages...")
    _seed_messages()
    
    # 16. BILLING & SUPPORT
    print("✓ Seeding billing records...")
    _seed_billing_records()
    
    print("✓ Seeding support tickets...")
    _seed_support_tickets()
    
    # 17. API KEYS & FILES
    print("✓ Seeding api keys...")
    _seed_api_keys()
    
    print("✓ Seeding files...")
    _seed_files()
    
    # 18. REPORTS & AUDIT
    print("✓ Seeding reports...")
    _seed_reports()
    
    print("✓ Seeding audit events...")
    _seed_audit_events()
    
    # 19. CHAT & REGULATION
    print("✓ Seeding chat sessions...")
    _seed_chat_sessions()
    
    print("✓ Seeding regulation recommendations...")
    _seed_regulation_recommendations()
    
    # 20. PRODUCT ENRICHMENT & MARKET INTELLIGENCE
    print("✓ Seeding product enrichments...")
    _seed_product_enrichments()
    
    print("✓ Seeding market intelligence...")
    _seed_market_intelligence()
    
    print("✓ Seeding pricing results...")
    _seed_pricing_results()
    
    # 21. VILLAGES & VILLAGE PRODUCTS
    print("✓ Seeding villages...")
    _seed_villages()
    
    # 22. SETTINGS
    print("✓ Seeding settings...")
    _seed_settings()
    
    print("✅ Comprehensive seeding completed!")


# ============================================================================
# 1. MASTER DATA
# ============================================================================

def _seed_countries():
    """Seed master data negara (jika belum ada)."""
    existing = {c["country_code"] for c in db.all("countries")}
    
    from app.data import countries as country_data
    
    for c in country_data.get_countries():
        if c["country_code"] not in existing:
            db.insert("countries", {
                "id": db.gen_id("countries", "CTY"),
                "country_code": c["country_code"],
                "country_name": c["country_name"],
                "region": c["region"],
                "createdAt": "2026-07-01",
            })


def _seed_hs_codes():
    """Seed kode HS chapter komoditas desa (01-24, 46, 68-70)."""
    if db.loaded_records("hs_codes") >= 100:
        return
    
    from app.seed_village_commodities import filter_village_hs_codes
    from app.data import hs_loader
    
    loader = hs_loader.get_hs_loader()
    village_codes = filter_village_hs_codes(loader.codes)
    
    for i, code in enumerate(village_codes, 1):
        hs_code = code.get("hs_code", "")
        description = code.get("description", "")
        
        # Skip jika sudah ada
        if db.get_by("hs_codes", hs_code=hs_code[:6]):
            continue
            
        db.insert("hs_codes", {
            "id": f"HS-{i:04d}",
            "hs_code": hs_code,
            "description": description,
            "section": code.get("section", ""),
            "level": code.get("level", len(hs_code)),
            "parent": code.get("parent", ""),
            "is_village_priority": True,
            "commodity_group": _commodity_group_for_hs(hs_code),
            "createdAt": "2026-07-01",
        })


def _commodity_group_for_hs(hs_code: str) -> str:
    """Map HS code ke commodity group."""
    try:
        chapter = int(str(hs_code)[:2])
    except:
        return "pertanian"
    
    if chapter == 3:
        return "perikanan"
    if chapter in {46, 68, 69, 70}:
        return "kerajinan"
    return "pertanian"


# ============================================================================
# 2. USERS
# ============================================================================

def _seed_users():
    """Seed users dengan berbagai roles."""
    emails = ["admin@mauekspor.example", "rizal@kopigayo.example", 
              "aya@hikari.example", "nadia@ops.mauekspor.example"]
    
    existing = {u["email"] for u in db.all("users")}
    
    users_data = [
        {"email": "admin@mauekspor.example", "role": "Admin", "fullName": "MauEkspor Admin", "organization": "MauEkopor"},
        {"email": "rizal@kopigayo.example", "role": "Exporter", "fullName": "Rizal Fahmi", "organization": "PT Kopi Gayo Nusantara"},
        {"email": "aya@hikari.example", "role": "Buyer", "fullName": "Aya Nakamura", "organization": "Hikari Foods Co."},
        {"email": "nadia@ops.mauekspor.example", "role": "Exporter", "fullName": "Nadia Prameswari", "organization": "PT Kopi Gayo Nusantara"},
        {"email": "sinta@medansnacks.example", "role": "Exporter", "fullName": "Sinta Lestari", "organization": "Medan Crispy Foods"},
        {"email": "lena@nordhaus.example", "role": "Buyer", "fullName": "Lena Hartmann", "organization": "Nordhaus Living"},
    ]
    
    for user in users_data:
        if user["email"] not in existing:
            db.insert("users", {
                "id": db.gen_id("users", "USR"),
                "email": user["email"],
                "fullName": user["fullName"],
                "role": user["role"],
                "password": hash_password("password123"),
                "organization": user["organization"],
                "status": "Active",
                "createdAt": "2026-07-01",
                "lastLogin": "2026-08-06",
            })


# ============================================================================
# 3-4. PRODUCTS & BUSINESS PROFILES
# ============================================================================

def _seed_products():
    """Seed produk ekspor unggulan."""
    existing = {p["id"] for p in db.all("products")}
    
    products = [
        {"id": "PRD-COF-001", "name": "Gayo Arabica Coffee Beans", "category": "Perkebunan", "hs": "09011100", "origin": "Aceh, Indonesia", "readiness": 86},
        {"id": "PRD-FUR-014", "name": "Handwoven Rattan Chair Set", "category": "Kriya Rotan", "hs": "46021200", "origin": "Central Java, Indonesia", "readiness": 74},
        {"id": "PRD-SNK-006", "name": "Cassava Chips Original", "category": "Olahan Pertanian", "hs": "19059000", "origin": "Lampung, Indonesia", "readiness": 79},
        {"id": "PRD-BAT-023", "name": "Batik Tulis Premium", "category": "Kriya Tekstil", "hs": "61142000", "origin": "Yogyakarta, Indonesia", "readiness": 82},
        {"id": "PRD-FISH-011", "name": "Frozen Tuna Sashimi Grade", "category": "Perikanan", "hs": "03032200", "origin": "Ternate, Indonesia", "readiness": 88},
    ]
    
    for prod in products:
        if prod["id"] not in existing:
            db.insert("products", {
                **prod,
                "status": "Ready",
                "packaging": "Export-ready packaging",
                "netWeight": f"{prod['readiness'] / 10} kg",
                "grossWeight": f"{prod['readiness'] / 10 + 0.5} kg",
                "moq": "500 units",
                "leadTime": "21 days",
                "certificates": ["Halal", "Certificate of Origin"],
                "updatedAt": "2026-08-06",
            })


def _seed_business_profiles():
    """Seed business profiles exporter."""
    existing = {p["id"] for p in db.all("business_profiles")}
    
    profiles = [
        {"id": "BIZ-GAYO-001", "companyName": "PT Kopi Gayo Nusantara", "owner": "Rizal Fahmi", "readiness": 86},
        {"id": "BIZ-MEDAN-001", "companyName": "Medan Crispy Foods", "owner": "Sinta Lestari", "readiness": 94},
        {"id": "BIZ-YOGA-001", "companyName": "Batik Jogja Heritage", "owner": "Bagus Santoso", "readiness": 82},
    ]
    
    for profile in profiles:
        if profile["id"] not in existing:
            db.insert("business_profiles", {
                **profile,
                "address": f"Jakarta, Indonesia",
                "productionCapacity": "5000 units / month",
                "yearEstablished": 2018,
                "certifications": ["Halal", "ISO 9001"],
                "status": "Complete",
                "updatedAt": "2026-08-06",
            })


# ============================================================================
# 5-7. PROJECTS, EXPORT ANALYSES, BUYERS
# ============================================================================

def _seed_projects():
    """Seed trade projects."""
    existing = {p["id"] for p in db.all("projects")}
    
    projects = [
        {"id": "EXP-2408-017", "name": "Japan Coffee Trial Shipment", "buyer": "Hikari Foods Co.", "country": "Japan", "product": "Gayo Arabica Coffee Beans", "stage": "Compliance Review", "readiness": 82},
        {"id": "EXP-2408-021", "name": "EU Rattan Furniture Program", "buyer": "Nordhaus Living", "country": "Germany", "product": "Handwoven Rattan Chair Set", "stage": "Quotation", "readiness": 74},
        {"id": "EXP-2408-026", "name": "Singapore Organic Snacks", "buyer": "Merlion Grocers", "country": "Singapore", "product": "Cassava Chips Sea Salt", "stage": "Documents", "readiness": 91},
    ]
    
    for proj in projects:
        if proj["id"] not in existing:
            db.insert("projects", {
                **proj,
                "value": 42800,
                "risk": "Medium",
                "eta": "18 Sep 2026",
                "incoterm": "FOB Tanjung Priok",
                "hsCode": proj["product"].split()[0][:4],
                "port": "Jakarta to destination",
                "payment": "30% deposit, 70% before shipment",
                "updatedAt": "2026-08-06",
            })


def _seed_export_analyses():
    """Seed export analysis reports."""
    existing = {e["id"] for e in db.all("export_analyses")}
    
    analyses = [
        {"id": "ANL-COF-001", "productId": "PRD-COF-001", "productName": "Gayo Arabica Coffee Beans", "destination": "Japan", "status": "Ready", "hsCode": "090111", "confidence": 91, "score": 84},
    ]
    
    for ana in analyses:
        if ana["id"] not in existing:
            db.insert("export_analyses", {
                **ana,
                "marketDemand": "High",
                "duties": "0% (JP-EPA)",
                "restrictions": ["Label in Japanese", "Lab report within 12 months"],
                "recommendations": [{"type": "Certificate", "title": "Certificate of Origin", "status": "Required"}],
                "summary": "High-demand zero duty lane; labeling evidence required.",
                "updatedAt": "2026-08-06",
            })


def _seed_buyer_requests():
    """Seed buyer requests."""
    existing = {r["id"] for r in db.all("buyer_requests")}
    
    reqs = [
        {"id": "BRQ-JP-COF-001", "buyerId": "BUY-HIKARI-JP", "productId": "PRD-COF-001", "subject": "Trial shipment for Gayo Arabica coffee", "status": "Matched"},
    ]
    
    for req in reqs:
        if req["id"] not in existing:
            db.insert("buyer_requests", {
                **req,
                "destination": "Japan",
                "quantity": "2,000 bags",
                "deadline": "2026-08-12",
                "requirements": ["Japanese label", "Lab report", "FOB quote"],
            })


def _seed_buyers():
    """Seed buyer companies."""
    existing = {b["id"] for b in db.all("buyers")}
    
    buyers = [
        {"id": "BUY-HIKARI-JP", "name": "Hikari Foods Co.", "country": "Japan", "segment": "Specialty food importer", "status": "Negotiating", "fitScore": 86},
        {"id": "BUY-NORDHAUS-DE", "name": "Nordhaus Living", "country": "Germany", "segment": "Home-living retail chain", "status": "At Risk", "fitScore": 71},
        {"id": "BUY-MERLION-SG", "name": "Merlion Grocers", "country": "Singapore", "segment": "Regional distributor", "status": "Confirmed", "fitScore": 91},
    ]
    
    for buy in buyers:
        if buy["id"] not in existing:
            db.insert("buyers", {
                **buy,
                "projectIds": ["EXP-2408-017"],
                "interestedProducts": ["Gayo Arabica Coffee Beans"],
                "estimatedAnnualValue": 185000,
                "paymentProfile": "LC at sight",
                "lastContact": "2026-08-05",
                "nextStep": "Send label proof and lab report timing.",
                "contact": {"name": "Aya Nakamura", "role": "Import Manager", "email": "aya@hikari.example"},
                "signals": [{"label": "RFQ urgency", "detail": "Deadline in 6 days.", "tone": "orange"}],
                "notes": [],
            })


# ============================================================================
# 8-12. FORWARDERS, CATALOGS, COSTING, MARKETS, RFQS, QUOTATIONS, ORDERS
# ============================================================================

def _seed_forwarders():
    """Seed logistics forwarders."""
    existing = {f["id"] for f in db.all("forwarders")}
    
    forwarders = [
        {"id": "FWD-NGL", "name": "Nusantara Global Logistics", "coverage": "Asia Pacific", "status": "Verified", "mode": "Ocean", "onTimeRate": 92},
        {"id": "FWD-AFN", "name": "Archipelago Freight Network", "coverage": "Europe FCL/LCL", "status": "In Review", "mode": "Ocean", "onTimeRate": 81},
    ]
    
    for fwd in forwarders:
        if fwd["id"] not in existing:
            db.insert("forwarders", {
                **fwd,
                "quoteSpeed": "4 hours",
                "lanes": ["Jakarta - Yokohama", "Surabaya - Rotterdam"],
                "contact": "ops@forwarder.example",
            })


def _seed_catalogs():
    """Seed product catalogs."""
    existing = {c["id"] for c in db.all("catalogs")}
    
    catalogs = [
        {"id": "CAT-COF-JP-001", "productId": "PRD-COF-001", "projectId": "EXP-2408-017", "title": "Premium Gayo Arabica Coffee Beans 250g", "status": "Needs Review"},
    ]
    
    for cat in catalogs:
        if cat["id"] not in existing:
            db.insert("catalogs", {
                **cat,
                "targetMarket": "Japan specialty importers",
                "moq": "2,000 bags",
                "leadTime": "21 days after deposit",
                "priceRange": "FOB USD 20.80-21.40 per bag",
                "incoterms": ["EXW", "FOB"],
                "readiness": 78,
                "updatedAt": "2026-08-05",
                "description": "Single-origin Gayo Arabica beans for specialty retail.",
                "highlights": ["Single-origin Aceh profile", "Export valve bag"],
                "specifications": [{"label": "Variety", "value": "Arabica Gayo (G1)"}],
                "images": 4,
                "variants": ["250g valve bag", "1kg bulk"],
            })


def _seed_costing():
    """Seed cost analysis."""
    existing = {c["id"] for c in db.all("costing")}
    
    costing = [
        {"id": "CST-JP-017", "projectId": "EXP-2408-017", "productId": "PRD-COF-001", "title": "Japan Coffee FOB Base Case", "destination": "Japan", "incoterm": "FOB", "currency": "USD", "status": "Ready", "margin": 22},
    ]
    
    for cst in costing:
        if cst["id"] not in existing:
            db.insert("costing", {
                **cst,
                "exchangeRate": 16250,
                "exwPrice": 39150,
                "fobPrice": 42800,
                "cifPrice": 46200,
                "landedCost": 51380,
                "profit": 10950,
                "confidence": 84,
                "lines": [{"category": "Production", "label": "COGS", "amount": 28500}],
                "risks": ["Freight estimate not converted to booking"],
                "updatedAt": "2026-08-06",
            })


def _seed_markets():
    """Seed market intelligence."""
    existing = {m["id"] for m in db.all("markets")}
    
    markets = [
        {"id": "MKT-JP-COF", "productId": "PRD-COF-001", "projectId": "EXP-2408-017", "country": "Japan", "marketScore": 84, "complianceComplexity": "Medium", "logisticsFeasibility": 78, "estimatedMargin": 22, "status": "Recommended"},
    ]
    
    for mkt in markets:
        if mkt["id"] not in existing:
            db.insert("markets", {
                **mkt,
                "importValue": "$1.61B roasted/green coffee category",
                "growth": "+5.8% YoY",
                "tariff": "Low tariff exposure; labeling evidence required",
                "entryStrategy": "Specialty importer trial shipment.",
                "opportunities": ["Specialty coffee demand resilient"],
                "risks": ["Label proof blocked"],
                "sources": [{"name": "Japan customs import statistics", "date": "2026-07-28"}],
                "updatedAt": "2026-08-06",
            })


def _seed_rfqs():
    """Seed RFQs (Request for Quotation)."""
    existing = {r["id"] for r in db.all("rfqs")}
    
    rfqs = [
        {"id": "RFQ-0891", "projectId": "EXP-2408-017", "productId": "PRD-COF-001", "buyerName": "Hikari Foods Co.", "destination": "Japan", "quantity": "2,000 bags / 500 kg", "incoterm": "FOB Tanjung Priok", "status": "Matching"},
    ]
    
    for rfq in rfqs:
        if rfq["id"] not in existing:
            db.insert("rfqs", {
                **rfq,
                "deadline": "2026-08-12",
                "matchScore": 86,
                "requirements": ["HS 0901.21", "Japanese label"],
                "matches": [{"supplier": "PT Kopi Gayo Nusantara", "catalog": "Premium Gayo Arabica 250g", "score": 86, "reason": "Strong fit."}],
            })


def _seed_quotations():
    """Seed quotations."""
    existing = {q["id"] for q in db.all("quotations")}
    
    quotations = [
        {"id": "Q-2408-017-A", "rfqId": "RFQ-0891", "projectId": "EXP-2408-017", "supplier": "PT Kopi Gayo Nusantara", "buyer": "Hikari Foods Co.", "incoterm": "FOB Tanjung Priok", "value": 42800, "currency": "USD", "status": "In Review"},
    ]
    
    for quot in quotations:
        if quot["id"] not in existing:
            db.insert("quotations", {
                **quot,
                "validUntil": "2026-08-20",
                "margin": 22,
                "notes": "Pending label proof.",
                "costLines": [{"label": "COGS", "amount": 28500}],
                "updatedAt": "2026-08-06",
            })


def _seed_orders():
    """Seed purchase orders."""
    existing = {o["id"] for o in db.all("orders")}
    
    orders = [
        {"id": "SO-2408-026", "quotationId": "Q-2408-026-A", "projectId": "EXP-2408-026", "buyer": "Merlion Grocers", "supplier": "North Sumatra Snacks", "status": "Document Prep", "incoterm": "DAP Singapore DC", "value": 21800, "currency": "USD", "readiness": 88},
    ]
    
    for order in orders:
        if order["id"] not in existing:
            db.insert("orders", {
                **order,
                "paymentTerms": "Net 21 after delivery",
                "deliveryWindow": "24-29 Aug 2026",
                "lines": [{"product": "Cassava Chips Sea Salt", "quantity": "5,000 pouches", "unitPrice": 4.36, "total": 21800}],
                "checklist": [{"label": "Quotation accepted", "status": "Done"}],
                "updatedAt": "2026-08-06",
            })


# ============================================================================
# 13-18. COMPLIANCE, DOCUMENTS, SHIPMENTS, PAYMENTS, TASKS, TEAM, NOTIFICATIONS
# ============================================================================

def _seed_compliance_requirements():
    """Seed compliance requirements."""
    existing = {c["id"] for c in db.all("compliance_requirements")}
    
    comps = [
        {"id": "REQ-COF-LBL-001", "projectId": "EXP-2408-017", "productId": "PRD-COF-001", "title": "Japanese nutrition and allergen label proof", "category": "Labeling", "severity": "Critical", "status": "Blocked"},
    ]
    
    for comp in comps:
        if comp["id"] not in existing:
            db.insert("compliance_requirements", {
                **comp,
                "owner": "Exporter",
                "due": "Tomorrow",
                "source": "Consumer Affairs Agency Japan",
                "sourceDate": "2026-07-30",
                "requiredEvidence": "Japanese label artwork + importer review",
                "currentEvidence": "English label only",
                "confidence": 79,
                "updatedAt": "2026-08-06",
            })


def _seed_documents():
    """Seed shipping/compliance documents."""
    existing = {d["id"] for d in db.all("documents")}
    
    docs = [
        {"id": "DOC-JP-INV-001", "projectId": "EXP-2408-017", "type": "Commercial Invoice", "status": "Ready", "version": "v1.2"},
    ]
    
    for doc in docs:
        if doc["id"] not in existing:
            db.insert("documents", {
                **doc,
                "owner": "Operations",
                "updatedAt": "2026-08-05",
                "validationScore": 96,
                "fields": {"invoiceNo": "INV-JP-2408-017", "totalValue": "42,800", "hsCode": "0901.21"},
                "checks": [{"label": "HS matches product", "status": "Passed"}],
            })


def _seed_shipments():
    """Seed shipment tracking."""
    existing = {s["id"] for s in db.all("shipments")}
    
    ships = [
        {"id": "SHP-JP-017", "projectId": "EXP-2408-017", "forwarder": "Nusantara Global Logistics", "mode": "Ocean LCL", "route": "Jakarta - Yokohama", "status": "Customs Submitted", "eta": "18 Sep 2026", "progress": 48},
    ]
    
    for ship in ships:
        if ship["id"] not in existing:
            db.insert("shipments", {
                **ship,
                "container": "LCL / 2.4 CBM",
                "bookingNo": "NGL-JP-240817",
                "milestones": [{"label": "Booking Confirmed", "status": "Done"}, {"label": "Customs Submitted", "status": "Current"}],
                "updatedAt": "2026-08-06",
            })


def _seed_payments():
    """Seed payment tracking."""
    existing = {p["id"] for p in db.all("payments")}
    
    pays = [
        {"id": "PAY-JP-017", "orderId": "SO-2408-017", "buyer": "Hikari Foods Co.", "status": "Deposit Paid", "currency": "USD", "amount": 42800, "paid": 12840},
    ]
    
    for pay in pays:
        if pay["id"] not in existing:
            db.insert("payments", {
                **pay,
                "dueDate": "2026-08-20",
                "method": "Bank Transfer",
                "risk": "Medium",
                "milestones": [{"label": "30% deposit", "amount": 12840, "status": "Done"}],
                "updatedAt": "2026-08-06",
            })


def _seed_tasks():
    """Seed pending tasks."""
    existing = {t["id"] for t in db.all("tasks")}
    
    tasks = [
        {"id": "TSK-COF-LABEL-01", "title": "Upload Japanese label proof", "module": "Compliance", "projectId": "EXP-2408-017", "owner": "Exporter", "priority": "Critical", "status": "Blocked"},
    ]
    
    for task in tasks:
        if task["id"] not in existing:
            db.insert("tasks", {
                **task,
                "due": "Tomorrow",
                "description": "Required before quotation approval.",
                "updatedAt": "2026-08-06",
            })


def _seed_team_members():
    """Seed team members."""
    existing = {t["id"] for t in db.all("team_members")}
    
    teams = [
        {"id": "TM-OPS-001", "name": "Nadia Prameswari", "role": "Operations", "status": "Active"},
        {"id": "TM-FIN-001", "name": "Leony Tan", "role": "Finance", "status": "Active"},
    ]
    
    for tm in teams:
        if tm["id"] not in existing:
            db.insert("team_members", {
                **tm,
                "email": f"{tm['name'].lower().replace(' ', '.')}@mauekspor.example",
                "lastActive": "10 minutes ago",
                "permissions": ["Orders", "Documents", "Shipments"],
                "workload": 78,
            })


def _seed_notifications():
    """Seed system notifications."""
    existing = {n["id"] for n in db.all("notifications")}
    
    ntf = [
        {"id": "NTF-001", "title": "Japanese label proof blocked", "description": "Critical compliance task.", "module": "Compliance", "severity": "Critical", "status": "Unread"},
    ]
    
    for note in ntf:
        if note["id"] not in existing:
            db.insert("notifications", {
                **note,
                "time": "8 min ago",
                "href": "/tasks/TSK-COF-LABEL-01",
            })


# ============================================================================
# 19-24. INTEGRATIONS, KNOWLEDGE, EDUCATION, CALENDAR, MESSAGES, BILLING
# ============================================================================

def _seed_integrations():
    """Seed third-party integrations."""
    existing = {i["id"] for i in db.all("integrations")}
    
    ints = [
        {"id": "INT-FORWARDER", "name": "Forwarder Rate Gateway", "category": "Logistics", "status": "Connected"},
    ]
    
    for inte in ints:
        if inte["id"] not in existing:
            db.insert("integrations", {
                **inte,
                "description": "Sync freight quotes and bookings.",
                "lastSync": "2026-08-06",
                "scopes": ["Rates", "Bookings"],
            })


def _seed_knowledge_articles():
    """Seed help/knowledge base articles."""
    existing = {k["id"] for k in db.all("knowledge_articles")}
    
    arts = [
        {"id": "KB-EXPORT-START", "title": "How to start an export project", "category": "Export Basics", "status": "Published"},
    ]
    
    for art in arts:
        if art["id"] not in existing:
            db.insert("knowledge_articles", {
                **art,
                "readTime": "6 min",
                "updatedAt": "2026-08-01",
                "summary": "Practical flow from readiness to first shipment.",
                "steps": ["Create a trade project", "Attach product master data", "Review target market"],
            })


def _seed_educational_modules():
    """Seed educational learning modules."""
    existing = {e["id"] for e in db.all("educational_modules")}
    
    mods = [
        {"id": "EDU-START", "title": "Export Readiness Foundations", "level": "Beginner", "status": "Published"},
        {"id": "EDU-PACK", "title": "Export Packaging Standards", "level": "Intermediate", "status": "Published"},
        {"id": "EDU-CUSTOMS", "title": "Customs Clearance Basics", "level": "Beginner", "status": "Published"},
    ]
    
    for mod in mods:
        if mod["id"] not in existing:
            db.insert("educational_modules", {
                **mod,
                "lessons": 8,
                "completion": 72,
                "summary": "Learn export basics and documentation.",
            })


def _seed_educational_articles():
    """Seed educational blog/article content."""
    existing = {a["id"] for a in db.all("educational_articles")}
    
    arts = [
        {"id": "ART-READY", "title": "How to prepare export-ready product data", "status": "Published"},
    ]
    
    for art in arts:
        if art["id"] not in existing:
            db.insert("educational_articles", {
                **art,
                "level": "Beginner",
                "readMinutes": 6,
                "tags": ["Product", "Readiness"],
                "summary": "Capture minimum data set for HS classification.",
                "body": "Split description, weights, dimensions, and packaging into structured specs.",
            })


def _seed_calendar_events():
    """Seed important dates/deadlines."""
    existing = {c["id"] for c in db.all("calendar_events")}
    
    cal = [
        {"id": "CAL-JP-LABEL", "title": "Japanese label proof deadline", "date": "2026-08-07", "time": "10:00", "type": "Compliance"},
    ]
    
    for event in cal:
        if event["id"] not in existing:
            db.insert("calendar_events", {
                **event,
                "status": "Blocked",
                "projectId": "EXP-2408-017",
                "owner": "Exporter",
                "description": "Label proof must be uploaded.",
                "updatedAt": "2026-08-06",
            })


def _seed_messages():
    """Seed buyer-seller communications."""
    existing = {m["id"] for m in db.all("messages")}
    
    msgs = [
        {"id": "MSG-HIKARI-LABEL", "subject": "Label proof and lab report timing", "party": "Hikari Foods Co.", "channel": "Email"},
    ]
    
    for msg in msgs:
        if msg["id"] not in existing:
            db.insert("messages", {
                **msg,
                "status": "Waiting Reply",
                "lastMessage": "Bilingual label review by Friday?",
                "time": "18 min ago",
                "linkedTo": "EXP-2408-017",
                "participants": ["Aya Nakamura", "Nadia Prameswari"],
            })


def _seed_billing_records():
    """Seed subscription/billing info."""
    existing = {b["id"] for b in db.all("billing_records")}
    
    bills = [
        {"id": "BIL-ORG-001", "plan": "Growth", "status": "Active", "amount": 99000, "currency": "USD", "period": "2026-08"},
    ]
    
    for bill in bills:
        if bill["id"] not in existing:
            db.insert("billing_records", {
                **bill,
                "dueDate": "2026-08-31",
                "usage": [{"label": "Products", "used": 5, "limit": 50}],
                "updatedAt": "2026-08-01",
            })


# ============================================================================
# 25-30. SUPPORT, API KEYS, FILES, REPORTS, AUDIT, CHAT
# ============================================================================

def _seed_support_tickets():
    """Seed customer support tickets."""
    existing = {s["id"] for s in db.all("support_tickets")}
    
    tickets = [
        {"id": "SUPPORT-1041", "subject": "Need help configuring bank tracking", "category": "Integration", "status": "Open", "priority": "High"},
    ]
    
    for ticket in tickets:
        if ticket["id"] not in existing:
            db.insert("support_tickets", {
                **ticket,
                "createdAt": "2026-08-06",
                "owner": "Leony Tan",
                "description": "Finance team help connecting bank tracker.",
            })


def _seed_api_keys():
    """Seed API integration keys."""
    existing = {a["id"] for a in db.all("api_keys")}
    
    keys = [
        {"id": "KEY-LOG-001", "name": "Forwarder webhook key", "prefix": "mek_live_log_", "status": "Active"},
    ]
    
    for key in keys:
        if key["id"] not in existing:
            db.insert("api_keys", {
                **key,
                "scopes": ["shipments:write", "rates:read"],
                "createdAt": "2026-08-01",
                "lastUsed": "2026-08-06",
                "owner": "Operations",
            })


def _seed_files():
    """Seed uploaded documents/files."""
    existing = {f["id"] for f in db.all("files")}
    
    files = [
        {"id": "FIL-CI-JP", "name": "INV-JP-2408-017.pdf", "type": "Document", "status": "Verified"},
    ]
    
    for fil in files:
        if fil["id"] not in existing:
            db.insert("files", {
                **fil,
                "projectId": "EXP-2408-017",
                "owner": "Operations",
                "updatedAt": "2026-08-05",
                "size": "184 KB",
                "tags": ["Commercial Invoice", "Japan", "Coffee"],
            })


def _seed_reports():
    """Seed analytics/reports."""
    existing = {r["id"] for r in db.all("reports")}
    
    reps = [
        {"id": "RPT-EXEC-2408", "title": "August Export Executive Brief", "type": "Executive", "status": "Ready"},
    ]
    
    for rep in reps:
        if rep["id"] not in existing:
            db.insert("reports", {
                **rep,
                "period": "August 2026",
                "owner": "Management",
                "updatedAt": "2026-08-06",
                "sections": ["Pipeline value", "Compliance blockers"],
                "insights": ["Singapore lane ready for reorder."],
            })


def _seed_audit_events():
    """Seed audit log entries."""
    existing = {a["id"] for a in db.all("audit_events")}
    
    audits = [
        {"id": "AUD-1001", "time": "2026-08-06", "actor": "AI Copilot", "action": "Generated market insight", "module": "Markets", "entity": "MKT-SG-SNK"},
    ]
    
    for aud in audits:
        if aud["id"] not in existing:
            db.insert("audit_events", {
                **aud,
                "severity": "Info",
                "detail": "Singapore route scored 91.",
            })


def _seed_chat_sessions():
    """Seed AI chat conversation history."""
    existing = {c["id"] for c in db.all("chat_sessions")}
    
    chats = [
        {"id": "CHS-001", "title": "Japan coffee compliance guidance"},
    ]
    
    for chat in chats:
        if chat["id"] not in existing:
            db.insert("chat_sessions", {
                **chat,
                "messages": [
                    {"role": "user", "text": "Apa yang menghalangi pengiriman kopi ke Jepang?"},
                    {"role": "ai", "text": "Bukti label Bahasa Jepang dan laporan lab diperlukan sebelum quotation disetujui."},
                ],
                "createdAt": "2026-08-06",
                "updatedAt": "2026-08-06",
            })


def _seed_regulation_recommendations():
    """Seed regulatory requirement recommendations."""
    existing = {r["id"] for r in db.all("regulation_recommendations")}
    
    recs = [
        {"id": "REC-JP-001", "hsCode": "090111", "country": "Japan", "title": "Food Labeling and Health Regulations"},
    ]
    
    for rec in recs:
        if rec["id"] not in existing:
            db.insert("regulation_recommendations", {
                **rec,
                "requirements": ["Nutrition facts panel", "Allergen declaration", "Importer name/address"],
                "penalties": "Product recall or seizure",
                "source": "Japan Food Labeling Act",
                "updatedAt": "2026-08-06",
            })


# ============================================================================
# 31-33. ENRICHMENT, MARKET INTEL, PRICING
# ============================================================================

def _seed_product_enrichments():
    """Seed AI-enriched product descriptions."""
    existing = {e["id"] for e in db.all("product_enrichments")}
    
    enhs = [
        {"id": "ENR-COF-001", "productId": "PRD-COF-001"},
    ]
    
    for enh in enhs:
        if enh["id"] not in existing:
            db.insert("product_enrichments", {
                **enh,
                "hsCodeRecommendation": "09011100",
                "skuGenerated": "COF-ACE-001",
                "nameEnglishB2b": "Gayo Arabica Coffee Beans - Single Origin",
                "descriptionEnglishB2b": "Specialty single-origin arabica from the Gayo highlands.",
                "marketingHighlights": ["Single-origin Aceh", "Specialty grade"],
                "lastUpdatedAi": "2026-08-06",
            })


def _seed_market_intelligence():
    """Seed market intelligence with country recommendations."""
    existing = {m["id"] for m in db.all("market_intelligence")}
    
    mins = [
        {"id": "MI-COF-001", "productId": "PRD-COF-001"},
    ]
    
    for mi in mins:
        if mi["id"] not in existing:
            db.insert("market_intelligence", {
                **mi,
                "recommendedCountries": [
                    {"country": "Japan", "code": "JP", "score": 88, "reason": "Specialty coffee demand tinggi; EPA zero duty."},
                    {"country": "Singapore", "code": "SG", "score": 82, "reason": "Hub re-export; regulasi labeling ringan."},
                ],
                "countriesToAvoid": [{"country": "North Korea", "code": "KP", "reason": "Sanksi internasional."}],
                "marketTrends": ["Kenaikan permintaan kopi specialty", "Preferensi single-origin"],
                "competitiveLandscape": "Banyak eksportir Vietnam & Brasil; diferensiasi lewat cerita asal-usul.",
                "growthOpportunities": ["Roaster specialty Jepang", "Kemasan retail premium"],
                "risksAndChallenges": ["Kepatuhan label Bahasa Jepang", "Fluktuasi freight"],
                "overallRecommendation": "Fokus pada Jepang & Singapura sebagai pasar awal.",
                "generatedAt": "2026-08-06",
            })


def _seed_pricing_results():
    """Seed dynamic pricing calculations."""
    existing = {p["id"] for p in db.all("pricing_results")}
    
    prcs = [
        {"id": "PRC-COF-001", "productId": "PRD-COF-001", "targetCountryCode": "JP"},
    ]
    
    for prc in prcs:
        if prc["id"] not in existing:
            db.insert("pricing_results", {
                **prc,
                "cogsPerUnitIdr": 28500,
                "targetMarginPercent": 22,
                "exchangeRateUsed": 15800,
                "exwPrice": 2.20,
                "fobPrice": 2.44,
                "cifPrice": 2.66,
                "pricingInsight": "Harga kompetitif untuk segmen specialty.",
                "pricingBreakdown": {"HPP (IDR)": 28500, "Margin": "22%", "EXW": 2.20},
                "generatedAt": "2026-08-06",
            })


# ============================================================================
# 34-35. VILLAGES & SETTINGS
# ============================================================================

def _seed_villages():
    """Seed village potential data for interactive map."""
    existing = {v["id"] for v in db.all("villages")}
    
    villages = [
        {"id": "DES-GAYO", "name": "Desa Kopi Gayo", "region": "Aceh Tengah", "province": "Aceh", "flagshipCommodity": "Kopi Arabika", "readiness": 86, "lat": 4.5074, "lng": 96.8557},
        {"id": "DES-VANILI-BALI", "name": "Desa Vanili Bali", "region": "Tabanan", "province": "Bali", "flagshipCommodity": "Vanili", "readiness": 77, "lat": -8.5955, "lng": 115.1121},
        {"id": "DES-TORAJA", "name": "Desa Kakao Toraja", "region": "Toraja Utara", "province": "Sulawesi Selatan", "flagshipCommodity": "Kakao", "readiness": 81, "lat": -2.9267, "lng": 119.3334},
        {"id": "DES-KAHAYAN", "name": "Desa Rotan Kahayan", "region": "Pulang Pisau", "province": "Kalimantan Tengah", "flagshipCommodity": "Rotan", "readiness": 72, "lat": -2.0194, "lng": 114.8025},
        {"id": "DES-SUMBAWA", "name": "Desa Madu Sumbawa", "region": "Dompu", "province": "NTB", "flagshipCommodity": "Madu Hutan", "readiness": 84, "lat": -8.5932, "lng": 118.4586},
        {"id": "DES-TERNATE", "name": "Desa Cengkeh Ternate", "region": "Ternate", "province": "Maluku Utara", "flagshipCommodity": "Cengkeh", "readiness": 75, "lat": 0.7833, "lng": 127.3667},
        {"id": "DES-MUNTOK", "name": "Desa Lada Putih Muntok", "region": "Bangka Barat", "province": "Bangka Belitung", "flagshipCommodity": "Lada", "readiness": 70, "lat": -2.8967, "lng": 105.8601},
        {"id": "DES-KERINCI", "name": "Desa Kayu Manis Kerinci", "region": "Kerinci", "province": "Jambi", "flagshipCommodity": "Kayu Manis", "readiness": 74, "lat": -1.5786, "lng": 101.3261},
        {"id": "DES-SITUBONDO", "name": "Desa Manggis Situbondo", "region": "Situbondo", "province": "Jawa Timur", "flagshipCommodity": "Manggis", "readiness": 68, "lat": -7.4091, "lng": 114.1161},
    ]
    
    for vil in villages:
        if vil["id"] not in existing:
            db.insert("villages", {
                **vil,
                "status": "Siap Ekspor" if vil["readiness"] >= 80 else "Butuh Pendampingan",
                "organization": f"Bumdes {vil['name']}",
                "production": f"{vil['readiness']} ton / bulan",
                "createdAt": "2026-07-01",
            })


def _seed_settings():
    """Seed platform settings."""
    existing = list(db.all("settings"))
    
    if len(existing) == 0:
        db.insert("settings", {
            "id": "SET-001",
            "key": "platform_config",
            "value": {
                "defaultCurrency": "USD",
                "defaultExchangeRate": 15800,
                "timezone": "Asia/Jakarta",
                "features": {"enable_chat": True, "enable_analytics": True},
            },
            "updatedAt": "2026-08-06",
        })
    
    # Exchange rate
    rates = list(db.all("exchange_rates"))
    if len(rates) == 0:
        db.insert("exchange_rates", {
            "id": db.gen_id("exchange_rates", "FX"),
            "rate": 15800,
            "source": "Bank Indonesia",
            "updatedAt": "2026-08-06 10:00",
        })


if __name__ == "__main__":
    seed_comprehensive()
