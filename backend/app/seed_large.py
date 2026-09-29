"""Seeder generator: 100 record per tabel dengan data realistis & saling terhubung."""
from app import db
from app.core.security import hash_password

EXPORT_COMPANIES = [
    "PT Kopi Gayo Nusantara", "CV Cirebon Rattan Works", "North Sumatra Snacks",
    "Bali Indah Crafts", "Surabaya Food Export", "Bandung Tekstil Prima",
    "Makassar Seafood Lautan", "Medan Spice Trading", "Semarang Furniture Jaya",
    "Yogyakarta Batik Lestari", "Lombok Pearls Industry", "Pontianak Rubber Indah",
    "Palembang Kriya Ukir", "Manado Cengkih Sejahtera", "Padang Kopi Kapal",
    "Aceh Organic Farm", "Riau Fiber Optima", "Jambi Kayu Manis",
    "Bengkulu Lada Hitam", "Lampung Kopi Robusta",
    "BUMDes Kerajinan Batam Sejahtera", "Koperasi Tani Tangerang Makmur",
    "BUMDes Agro Bogor Lestari", "Malang Apple Fresh", "Probolinggo Udang Ocean",
    "Cianjur Beras Sehat", "Subang Nanas Manis", "Garut Domba Export",
    "Tasikmalaya Bordir Kreatif", "Kudus Kretek Rempah", "Jepara Ukir Furniture",
    "Solo Batik Pusaka", "Pekalongan Laut Batik", "Tegal Ikan Laut Asin",
    "Cilacap Kayu Jati", "Purwokerto Agro Nusantara", "Magelang Kopi Arabika",
    "Salatiga Snack Sehat", "Ambon Cengkih Bestari", "Ternate Pala Rempah",
    "Biak Coral Marine", "Jayawijaya Kopi Papua", "Merauke Sagu Abadi",
    "Timika Tani Sejahtera", "Sorong Ikan Tuna", "Madiun Kripik Tempe",
    "Kediri Tebu Gula", "Blitar Susu Murni", "Pasuruan Ikan Bandeng",
    "BUMDes Agro Gresik Makmur", "Sidoarjo Kerupuk Udang", "Mojokerto Kerajinan Bambu",
    "Ngawi Kayu Jati", "BUMDes Tani Bojonegoro", "Tuban Kerajinan Batu",
    "Lamongan Ikan Lele", "Jombang Cor Logam", "Nganjuk Jahe Merah",
    "Ponorogo Alat Musik Kayu",
]

BUYER_COMPANIES = [
    "Hikari Foods Co. Ltd.", "Nordhaus Living GmbH", "Merlion Grocers Pte",
    "Tokyo Fresh Imports", "Osaka Trading House", "Yokohama Food Services",
    "Seoul Mart Corporation", "Busan Logistics Hub", "Incheon Distribution",
    "Shanghai Food Import", "Guangzhou Trading Ltd", "Shenzhen Electronics Buyers",
    "Hong Kong Commodities", "Singapore Tropical Foods", "Kuala Lumpur Rasa",
    "Bangkok Spice Traders", "Ho Chi Minh Export JV", "Manila Food Distributors",
    "Jakarta Premium Retail", "Taipei Tech Importers", "Seattle Coffee Importers",
    "New York Gourmet Foods", "Los Angeles Pacific Trade", "Miami Latin Food",
    "Chicago Midwest Import", "Vancouver Forest Products", "Toronto Maple Trade",
    "Mexico City Importadora", "Santiago Chile Foods", "Buenos Aires Cargo",
    "London British Imports", "Paris Euro Gourmet", "Berlin Deutsche Waren",
    "Amsterdam Port Logistics", "Rotterdam EU Distribution", "Stockholm Nordic Foods",
    "Oslo Fjord Imports", "Copenhagen Scandinavian Trade", "Dubai Middle East Hub",
    "Riyadh Saudi Import", "Doha Qatar Trading", "Kuwait City Gulf Mart",
    "Sydney Down Under Foods", "Melbourne Pacific Grocers", "Auckland Kiwi Exports",
    "Mumbai Spice Bazaar", "Chennai Textile Imports", "Delhi India Mart",
    "Colombo Ceylon Tea", "Dhaka Bengal Trading", "Karachi Pak Trade",
    "Istanbul Bosphorus Trade", "Moscow EuroAsia Imports", "Warsaw Poland Foods",
    "Prague Central Europe Trade", "Rome Italia Gourmet", "Madrid Iberica Trading",
    "Lisbon Atlantic Port", "Athens Mediterranean Foods", "Cairo Nile Trading",
    "Casablanca Maghreb Import", "Nairobi African Goods", "Cape Town SA Trading",
    "Lagos Nigeria Export Hub", "Accra Ghana Cocoa", "Dar es Salaam East Africa",
    "Phnom Penh Mekong Trade", "Vientiane Laos Woodcraft",
    "Kathmandu Himalayan Tea", "Islamabad Pakistan Leather",
    "Beirut Levant Importers",
]

FORWARDER_COMPANIES = [
    "Nusantara Global Logistics", "Archipelago Freight Network", "Indo Pacific Shipping",
    "Java Sea Container Lines", "Sumatra Cargo Express", "Borneo Logistics Solutions",
    "Sulawesi Maritime Freight", "Papua Port Forwarding", "Bali Air Cargo Services",
    "Merpati Nusantara Lines", "Garuda Logistics International", "Sea Horse Shipping Indo",
    "Ocean Sky Logistics", "Trans Asia Freight Forwarding", "Global Port Connections",
    "Bintang Samudra Logistik", "Kargo Nusantara Abadi", "Lintas Laut Ekspres",
    "Samudera Agung Logistics", "Indah Kargo International",
    "Multi Freight Solutions", "Prestige Logistics Group", "Royal Cargo Indonesia",
    "Lincah Jaya Logistik", "Cepat Kirim Global", "Sentosa Logistics Mandiri",
    "Berkah Samudra Logistik", "Prima Armada Nusantara", "Utama Cargo Services",
    "Pantai Indah Logistics", "Bumi Jaya Shipping", "Makmur Abadi Forwarding",
    "Sinar Pelangi Cargo", "Mitra Samudera Lines", "Artha Logistics Solutions",
    "Putra Jaya Forwarding", "Duta Logistik Internasional",
    "Naga Laut Container", "Angkasa Logistics Group", "Biru Laut Shipping",
    "Gunung Emas Freight", "Delta Cargo Indonesia", "Fajar Logistics Solutions",
    "Berkat Jasa Logistik", "Tirta Samudera Shipping", "Wahana Cargo Express",
    "Pelangi Express Cargo", "Gunung Agung Logistics", "Satria Kargo Nusantara",
    "Roda Jaya Forwarding", "Anugrah Logistik Global", "Mandiri Cargo Line",
    "Bahana Logistics Indo", "Samudra Shipping Lines", "Cahaya Pelabuhan Indonesia",
    "Kencana Cargo Solutions", "Purna Jasa Logistik", "Indo Global Forwarding",
    "Sinergi Logistik Nusantara", "Abadi Jaya Cargo", "Merdeka Logistics Indo",
    "Bangun Nusa Shipping", "Logistik Utama Sejahtera", "Bhakti Samudera Cargo",
    "Jaya Makmur Forwarding", "Nusa Indah Logistics", "Mitra Abadi Express",
    "Surya Logistics Indonesia", "Karya Cipta Forwarding", "Tanjung Priok Logistics",
    "Belawan Port Service", "Tanjung Perak Cargo", "Makassar Terminal Services",
]

CERTIFICATES = ["HACCP", "ISO 9001:2015", "ISO 22000", "Halal MUI", "Organic USDA",
    "EU Organic", "Japan JAS", "BPOM", "SNI", "GMP", "BRC Global Standard",
    "FSSC 22000", "Rainforest Alliance", "Fair Trade", "RSPO", "FSC",
    "OEKO-TEX", "GOTS", "SMETA", "GLOBALGAP", "ASC", "MSC"]

# Pool HS khusus komoditas desa: Chapter 01-24 (pertanian-peternakan-perikanan-
# perkebunan), 46 (kerajinan anyaman rotan), dan 68-70 (kriya batu/keramik/kaca).
HS_POOL = [
    ("010632", "Live parrots"), ("020230", "Frozen bovine meat"),
    ("030389", "Frozen fish"), ("030432", "Frozen tilapia fillets"),
    ("040900", "Natural honey"), ("060311", "Fresh orchid cut flowers"),
    ("071333", "Shelled kidney beans"), ("080310", "Bananas, fresh"),
    ("081060", "Mangosteens, fresh"), ("081330", "Dried mango slices"),
    ("090111", "Coffee, not roasted"), ("090121", "Coffee, roasted"),
    ("090230", "Black tea"), ("090411", "Pepper of genus Piper"),
    ("090611", "Vanilla, neither crushed nor ground"), ("090831", "Nutmeg"),
    ("090961", "Cinnamon tree bark"), ("100630", "Semi-milled rice"),
    ("120100", "Soybeans"), ("120740", "Sesame seeds"),
    ("151190", "Palm oil"), ("160413", "Shrimps prepared"),
    ("160414", "Tuna prepared"), ("170114", "Raw cane sugar"),
    ("180100", "Cocoa beans"), ("190531", "Sweet biscuits"),
    ("200811", "Cashew nuts prepared"), ("210111", "Coffee extracts"),
    ("240120", "Tobacco, partly stemmed"),
    ("460212", "Basketwork of vegetable materials, rattan"),
    ("680291", "Monumental/building articles of stone"),
    ("691110", "Porcelain tableware"), ("691390", "Ceramic statuettes"),
    ("701399", "Glass tableware"),
]

PRODUCTS = [
    "Kopi Arabika Gayo", "Kopi Robusta Lampung", "Kopi Luwak Premium",
    "Teh Hitam Jawa", "Kakao Fermentasi", "Udang Vannamei", "Tuna Sirip Kuning",
    "Minyak Kelapa Virgin", "Karet Alam RSS1", "Kayu Jati Olahan",
    "Rattan Anyaman", "Bambu Laminasi", "Mebel Rotan", "Kursi Kayu Ukir",
    "Meja Jati", "Lemari Pakaian", "Batik Tulis Solo", "Batik Cap Pekalongan",
    "Kain Tenun Sumba", "Kain Songket", "Sarung Sutra", "Kemeja Batik",
    "Tas Rotan", "Sepatu Kulit", "Tas Kulit", "Sabun Herbal",
    "Minyak Sereh Wangi", "Essential Oil", "Lilin Aromaterapi",
    "Keramik Hias", "Patung Perunggu", "Patung Kayu", "Wayang Kulit",
    "Keris Hias", "Topeng Kayu", "Lukisan Bali", "Ukiran Jepara",
    "Permadani Tenun", "Karpet Serat Alam", "Ikan Asin Belah",
    "Abon Sapi", "Dendeng Sapi", "Rendang Sapi Kaleng", "Sambal Goreng",
    "Pempek Kaleng", "Krupuk Udang", "Kripik Tempe", "Kripik Pisang",
    "Madu Hutan Sumbawa", "Gula Kelapa Organik", "Gula Aren",
    "Kecap Manis", "Saus Sambal", "Beras Pandanwangi", "Beras Hitam",
    "Kacang Mete Goreng", "Emping Melinjo", "Kerupuk Ikan",
    "Sarden Ikan Kembung", "Bandeng Presto", "Otak-Otak Ikan",
    "Tepung Tapioka", "Patin Fillet Beku", "Kopi Instant Premium",
    "Jahe Bubuk", "Kunyit Bubuk", "Kayu Manis Batang", "Cengkih Kering",
    "Pala Bubuk", "Lada Hitam", "Lada Putih", "Vanili Kering",
    "Minyak Atsiri Cengkih", "Kapur Barus", "Sirup Gula Merah",
    "Bumbu Rendang Instan", "Bumbu Nasi Goreng", "Jagung Pipil",
    "Kacang Tanah Kupas", "Tepung Beras", "Lele Filet", "Biskuit Jahe",
    "Stroopwafel", "Kemasan Vakum 250g", "Kontainer 20ft",
    "Palet Kayu Premium", "Box 5kg Ekspor", "Cokelat Premium",
    "Cumi-Cumi Beku", "Rumput Laut Kering", "Minyak Sawit",
    "Kayu Mahoni Furniture", "Keranjang Bambu", "Anyaman Mendong",
    "Tikar Pandan", "Sandal Kayu", "Gaun Tenun", "Selendang Sutra",
    "Dompet Kulit", "Sarung Bantal Batik", "Taplak Meja Bordir",
    "Beras Merah Organik",
]

# Peta produk → kode HS yang benar (chapter komoditas desa 01-24, 46, 68-70).
# Kunci = nama pada PRODUCTS; nilai = (kode HS, deskripsi Inggris singkat).
# Sebelumnya setiap produk mendapat HS acak dari HS_POOL sehingga kopi bisa
# berlabel HS pisang — fatal untuk aplikasi yang inti fiturnya klasifikasi HS.
PRODUCT_HS = {
    "Kopi Arabika Gayo": ("090111", "Coffee, not roasted"),
    "Kopi Robusta Lampung": ("090111", "Coffee, not roasted"),
    "Kopi Luwak Premium": ("090121", "Coffee, roasted"),
    "Teh Hitam Jawa": ("090230", "Black tea"),
    "Kakao Fermentasi": ("180100", "Cocoa beans"),
    "Udang Vannamei": ("030617", "Frozen shrimps"),
    "Tuna Sirip Kuning": ("030487", "Frozen tuna fillets"),
    "Minyak Kelapa Virgin": ("151311", "Crude coconut oil"),
    "Karet Alam RSS1": ("400121", "Natural rubber, smoked sheets"),
    "Kayu Jati Olahan": ("440729", "Tropical wood sawn"),
    "Rattan Anyaman": ("460212", "Basketwork of rattan"),
    "Bambu Laminasi": ("441210", "Plywood of bamboo"),
    "Mebel Rotan": ("940383", "Bamboo/rattan furniture"),
    "Kursi Kayu Ukir": ("940360", "Wooden furniture"),
    "Meja Jati": ("940360", "Wooden furniture"),
    "Lemari Pakaian": ("940350", "Wooden bedroom furniture"),
    "Batik Tulis Solo": ("621142", "Cotton garments"),
    "Batik Cap Pekalongan": ("621142", "Cotton garments"),
    "Kain Tenun Sumba": ("520852", "Woven cotton fabric"),
    "Kain Songket": ("520842", "Woven cotton fabric"),
    "Sarung Sutra": ("500720", "Woven silk fabric"),
    "Kemeja Batik": ("620590", "Men's garments"),
    "Tas Rotan": ("460290", "Basketwork articles"),
    "Sepatu Kulit": ("640399", "Leather footwear"),
    "Tas Kulit": ("420291", "Leather articles"),
    "Sabun Herbal": ("340111", "Soap for toilet use"),
    "Minyak Sereh Wangi": ("330129", "Essential oils, nes"),
    "Essential Oil": ("330129", "Essential oils, nes"),
    "Lilin Aromaterapi": ("340600", "Candles"),
    "Keramik Hias": ("691390", "Ceramic statuettes"),
    "Patung Perunggu": ("830629", "Bronze ornaments"),
    "Patung Kayu": ("442010", "Wooden statuettes"),
    "Wayang Kulit": ("970500", "Collector's pieces"),
    "Keris Hias": ("930700", "Swords and cutlasses"),
    "Topeng Kayu": ("442010", "Wooden statuettes"),
    "Lukisan Bali": ("970110", "Paintings"),
    "Ukiran Jepara": ("442010", "Wooden statuettes"),
    "Permadani Tenun": ("570500", "Carpets and textiles, nes"),
    "Karpet Serat Alam": ("570500", "Carpets and textiles, nes"),
    "Ikan Asin Belah": ("030559", "Dried fish, nes"),
    "Abon Sapi": ("160250", "Prepared bovine meat"),
    "Dendeng Sapi": ("160250", "Prepared bovine meat"),
    "Rendang Sapi Kaleng": ("160250", "Prepared bovine meat"),
    "Sambal Goreng": ("210390", "Sauces and preparations"),
    "Pempek Kaleng": ("160420", "Prepared fish"),
    "Krupuk Udang": ("190590", "Bread, pastry, cakes"),
    "Kripik Tempe": ("200819", "Prepared nuts/seeds"),
    "Kripik Pisang": ("200899", "Prepared fruit, nes"),
    "Madu Hutan Sumbawa": ("040900", "Natural honey"),
    "Gula Kelapa Organik": ("170114", "Raw cane sugar"),
    "Gula Aren": ("170114", "Raw cane sugar"),
    "Kecap Manis": ("210310", "Soy sauce"),
    "Saus Sambal": ("210390", "Sauces and preparations"),
    "Beras Pandanwangi": ("100630", "Semi-milled rice"),
    "Beras Hitam": ("100620", "Husked (brown) rice"),
    "Kacang Mete Goreng": ("200819", "Prepared cashew nuts"),
    "Emping Melinjo": ("190590", "Bread, pastry, cakes"),
    "Kerupuk Ikan": ("190590", "Bread, pastry, cakes"),
    "Sarden Ikan Kembung": ("160413", "Prepared sardines"),
    "Bandeng Presto": ("160419", "Prepared fish, nes"),
    "Otak-Otak Ikan": ("160420", "Prepared fish"),
    "Tepung Tapioka": ("110814", "Cassava starch"),
    "Patin Fillet Beku": ("030489", "Frozen fish fillets, nes"),
    "Kopi Instant Premium": ("210111", "Coffee extracts"),
    "Jahe Bubuk": ("091012", "Ginger, crushed or ground"),
    "Kunyit Bubuk": ("091030", "Turmeric"),
    "Kayu Manis Batang": ("090611", "Cinnamon"),
    "Cengkih Kering": ("090710", "Cloves"),
    "Pala Bubuk": ("090822", "Nutmeg, crushed or ground"),
    "Lada Hitam": ("090411", "Pepper, neither crushed"),
    "Lada Putih": ("090412", "Pepper, crushed or ground"),
    "Vanili Kering": ("090611", "Vanilla"),
    "Minyak Atsiri Cengkih": ("330129", "Essential oils, nes"),
    "Kapur Barus": ("330741", "Odoriferous preparations"),
    "Sirup Gula Merah": ("170290", "Other sugars and syrups"),
    "Bumbu Rendang Instan": ("210390", "Sauces and preparations"),
    "Bumbu Nasi Goreng": ("210390", "Sauces and preparations"),
    "Jagung Pipil": ("100590", "Maize, other"),
    "Kacang Tanah Kupas": ("120242", "Groundnuts, shelled"),
    "Tepung Beras": ("110230", "Rice flour"),
    "Lele Filet": ("030432", "Frozen catfish fillets"),
    "Biskuit Jahe": ("190531", "Sweet biscuits"),
    "Stroopwafel": ("190532", "Waffles and wafers"),
    "Kemasan Vakum 250g": ("392321", "Plastic sacks and bags"),
    "Kontainer 20ft": ("860900", "Containers for transport"),
    "Palet Kayu Premium": ("441520", "Wooden pallets"),
    "Box 5kg Ekspor": ("481910", "Cartons of paper"),
    "Cokelat Premium": ("180632", "Chocolate, not filled"),
    "Cumi-Cumi Beku": ("030743", "Frozen squid"),
    "Rumput Laut Kering": ("121229", "Seaweed, other"),
    "Minyak Sawit": ("151190", "Palm oil"),
    "Kayu Mahoni Furniture": ("940360", "Wooden furniture"),
    "Keranjang Bambu": ("460212", "Basketwork of bamboo"),
    "Anyaman Mendong": ("460212", "Basketwork of vegetable materials"),
    "Tikar Pandan": ("460129", "Plaiting materials"),
    "Sandal Kayu": ("640399", "Footwear"),
    "Gaun Tenun": ("620449", "Women's garments"),
    "Selendang Sutra": ("621410", "Silk shawls and scarves"),
    "Dompet Kulit": ("420231", "Leather wallets"),
    "Sarung Bantal Batik": ("630492", "Furnishing articles, cotton"),
    "Taplak Meja Bordir": ("630492", "Furnishing articles, cotton"),
    "Beras Merah Organik": ("100620", "Husked (brown) rice"),
}

REGIONS = {
    "Asia": ["JP", "KR", "SG", "MY", "TH", "VN", "PH", "CN", "IN", "TW"],
    "Europe": ["DE", "NL", "GB", "FR", "IT", "ES", "BE", "CH", "SE", "NO"],
    "North America": ["US", "CA", "MX"],
    "South America": ["BR", "AR", "CL", "CO"],
    "Africa": ["ZA", "NG", "KE", "EG", "MA", "GH"],
    "Oceania": ["AU", "NZ"],
    "Middle East": ["AE", "SA", "QA", "KW", "OM"],
}

CATEGORIES = ["Food & Beverage", "Furniture & Craft", "Apparel & Textile", "Electronics", "Agro & Spice"]
INCOTERMS = ["EXW", "FOB", "CIF", "DAP", "DDP", "FCA"]
STAGES = ["Scoping", "Compliance Review", "Quotation", "Documents", "Booked", "In Transit", "Delivered"]
RISKS = ["Low", "Medium", "High"]
CITIES = ["Jakarta", "Surabaya", "Bandung", "Medan", "Semarang", "Makassar", "Palembang", "Yogyakarta", "Denpasar", "Malang"]

# RNG deterministik (seed tetap) untuk sebaran yang sehat.
#
# Sebelumnya `_pick` memakai indeks `n % len(seq)` dari counter yang naik
# konstan tiap iterasi, sehingga satu status bisa selalu jatuh ke indeks yang
# sama — mis. 100 pembeli semuanya "Qualified", 100 supplier "Pending", 100
# pembayaran "Received", 100 analisis "Needs Review". Akibatnya UI menampilkan
# angka yang saling bertentangan (mis. "Active buyers 102" vs "Pembeli aktif 0")
# dan demo jadi tidak realistis. Seed tetap agar hasil reproducible untuk tes.
_RNG = __import__("random").Random(20260815)


def _pick(seq, n=None):
    """Pilih elemen acak (deterministik). `n` diabaikan — dipertahankan agar
    pemanggil lama `_pick(seq, n())` tetap kompatibel."""
    if not seq:
        return None
    return seq[_RNG.randrange(len(seq))]


def _pick_n(seq, n, seed=None):
    """Ambil `n % len(seq)` elemen unik acak dari `seq`."""
    if not seq:
        return []
    count = min(max(n % max(len(seq), 1), 0), len(seq))
    return _RNG.sample(list(seq), count)


def seed_100_records():
    """Generate 100 records per table."""
    from app.services.forwarders import recalculate_rating

    if db.loaded_records("users") and db.loaded_records("users") > 50:
        return

    print("🌱 Seeding 100 records per table (50+ tables)...")
    r = iter(range(1, 1000001))
    _counter = [0]
    def n():
        _counter[0] += 1
        return _counter[0]
    ALL_REGIONS = list(REGIONS.keys())

    # -- USERS (100) -- Mulai dari U-101 agar tidak menimpa seed dasar (U-001..U-003)
    roles = (["Admin"]*5 + ["Exporter"]*60 + ["Buyer"]*15 + ["Forwarder"]*10 + ["CustomsBroker"]*5 + ["Finance"]*5)
    user_ids = []
    for i in range(1, 101):
        role = roles[i-1]
        pool = EXPORT_COMPANIES if role == "Exporter" else BUYER_COMPANIES if role == "Buyer" else FORWARDER_COMPANIES if role == "Forwarder" else EXPORT_COMPANIES
        name = _pick(pool, n())
        dom = "export" if role == "Exporter" else "buyer" if role == "Buyer" else "fwd" if role == "Forwarder" else "admin" if role == "Admin" else "cb" if role == "CustomsBroker" else "fin"
        uid = f"U-{100 + i:03d}"
        u = {"id": uid, "email": f"user{i:03d}@{dom}.example", "fullName": f"User {i} - {name[:20]}",
             "name": name, "role": role, "organization": name,
             "password": hash_password("password123" if role != "Admin" else "admin123"),
             "status": "Active", "createdAt": f"2026-{n()%12+1:02d}-{n()%28+1:02d}", "lastLogin": f"2026-08-{n()%20+1:02d}"}
        db.insert("users", u)
        user_ids.append(uid)

    # -- PRODUCTS (100) + enrichments --
    product_ids = []
    for i in range(1, 101):
        pname = PRODUCTS[i-1]
        # HS code diambil dari peta kurasi per produk (fallback acak hanya bila
        # produk tak terdaftar) agar klasifikasi HS di demo masuk akal.
        hs = PRODUCT_HS.get(pname) or _pick(HS_POOL, n())
        cat = _pick(CATEGORIES, n())
        city = _pick(CITIES, n())
        pid = f"PRD-{i:03d}"
        product_ids.append(pid)
        db.insert("products", {"id": pid, "name": pname, "category": cat,
            "origin": f"{city}, Indonesia", "status": _pick(["Enriched", "Needs HS Review", "Ready"], n()),
            "hs": hs[0], "hsConfidence": 70+n()%25,
            "packaging": _pick(["Karton 20kg","Karung 50kg","Vakum 250g","Dus 12 pcs","Palet kayu"], n()),
            "netWeight": f"{n()%50+1}kg", "grossWeight": f"{n()%55+5}kg",
            "moq": f"{n()%1000+100} {_pick(['kg','pcs','unit'], n())}",
            "leadTime": f"{n()%45+7} hari",
            "certificates": _pick_n(CERTIFICATES, n()%3, n()),
            "readiness": n()%100, "sku": f"SKU-{i:04d}",
            "description": f"Produk {pname.lower()} berkualitas ekspor.",
            "updatedAt": "now"})
        db.insert("product_enrichments", {"id": f"ENR-{i:03d}", "productId": pid,
            "hsCodeRecommendation": hs[0], "skuGenerated": f"SKU-{i:04d}",
            "nameEnglishB2b": f"{pname} - Premium Export Grade",
            "descriptionEnglishB2b": f"High-quality {pname.lower()} for B2B.",
            "marketingHighlights": [f"Direct from {city}", "Premium quality"],
            "lastUpdatedAi": "now"})

    # -- BUSINESS PROFILES (100) --
    for i in range(1, 101):
        db.insert("business_profiles", {"id": f"BIZ-{i:03d}",
            "companyName": _pick(EXPORT_COMPANIES, n()),
            "address": f"Jl. {_pick(CITIES, n())} No.{n()%200+1}",
            "productionCapacity": f"{n()%1000+100} ton/bulan",
            "yearEstablished": 1990+n()%30,
            "certifications": _pick_n(CERTIFICATES, n()%5+1, n()),
            "status": _pick(["Complete","Needs Review","Draft"], n()),
            "owner": _pick(user_ids, n()), "readiness": n()%100, "updatedAt": "now"})

    # -- PROJECTS (100) --
    proj_ids = []
    for i in range(1, 101):
        reg = _pick(ALL_REGIONS, n())
        country = _pick(REGIONS[reg], n())
        buyer = _pick(BUYER_COMPANIES, n())
        pid = f"EXP-{i:03d}"
        proj_ids.append(pid)
        db.insert("projects", {"id": pid, "name": f"Project {i}: {_pick(PRODUCTS, n())}",
            "buyer": buyer, "country": country, "product": _pick(PRODUCTS, n()),
            "stage": _pick(STAGES, n()), "readiness": n()%100,
            "value": n()%500000+50000, "risk": _pick(RISKS, n()),
            "eta": f"2026-{n()%12+1:02d}", "incoterm": _pick(INCOTERMS, n()),
            "hsCode": _pick(HS_POOL, n())[0], "port": f"{_pick(CITIES, n())} - {country}",
            "payment": _pick(["LC","T/T","DP","DA"], n()), "updatedAt": "now"})

    # -- BUYERS (100) --
    buyer_ids = []
    for i in range(1, 101):
        bid = f"BUY-{i:03d}"
        buyer_ids.append(bid)
        db.insert("buyers", {"id": bid, "name": _pick(BUYER_COMPANIES, n()),
            "country": _pick(REGIONS[_pick(ALL_REGIONS, n())], n()),
            "segment": _pick(["Retail","Wholesale","Distributor"], n()),
            "status": _pick(["Lead","Qualified","Negotiating","Active"], n()),
            "fitScore": n()%100, "interestedProducts": _pick_n(PRODUCTS, n()%3+1, n()),
            "estimatedAnnualValue": n()%1000000+100000,
            "paymentProfile": _pick(["LC","T/T","Open Account"], n()),
            "lastContact": f"2026-{n()%8+1:02d}-{n()%28+1:02d}",
            "nextStep": _pick(["Send quotation","Schedule meeting","Provide samples"], n()),
            "contact": {"name": f"Contact {i}", "role": "Import Manager",
                       "email": f"buyer{i}@example.com", "phone": f"+62{n()%9000000+1000000}"},
            "notes": _pick_n(["Interested in bulk", "Prefers LC", "Needs samples"], n()%2, n()),
            "updatedAt": "now"})

    # -- BUYER REQUESTS (100) --
    for i in range(1, 101):
        db.insert("buyer_requests", {"id": f"BRQ-{i:03d}",
            "buyerId": _pick(buyer_ids, n()),
            "productId": _pick(product_ids, n()),
            "subject": f"Request for {_pick(PRODUCTS, n())}",
            "status": _pick(["New","Matched","Quoted","Closed"], n()),
            "destination": _pick(REGIONS[_pick(ALL_REGIONS, n())], n()),
            "quantity": f"{n()%10000+100} kg",
            "deadline": f"2026-{n()%12+1:02d}-{n()%28+1:02d}",
            "requirements": _pick_n(["HALAL certified","Organic","Premium grade"], n()%2+1, n()),
            "matches": [], "createdAt": "now", "updatedAt": "now"})

    # -- FORWARDERS (100) + REVIEWS --
    fwd_ids = []
    for i in range(1, 101):
        fid = f"FWD-{i:03d}"
        fwd_ids.append(fid)
        db.insert("forwarders", {"id": fid, "name": _pick(FORWARDER_COMPANIES, n()),
            "coverage": _pick(["Japan and North Asia","Europe","Global","Americas","SE Asia"], n()),
            "status": _pick(["Verified","In Review"], n()),
            "mode": _pick(["Ocean","Air","Multimodal"], n()),
            "onTimeRate": n()%40+60, "quoteSpeed": f"{n()%48+2}h",
            "lanes": [f"{_pick(CITIES, n())} - {_pick(REGIONS[_pick(ALL_REGIONS, n())], n())}"],
            "contact": f"fwd{i:03d}@example.com",
            "averageRating": 0, "totalReviews": 0, "updatedAt": "now"})
        db.insert("forwarder_reviews", {"id": f"REV-{i+100:03d}",
            "forwarderId": fid, "rating": n()%5+1,
            "reviewText": _pick(["Fast booking","Competitive rates","Good communication","Reliable tracking"], n()),
            "umkmId": _pick(user_ids, n()),
            "reviewerName": _pick(EXPORT_COMPANIES, n()),
            "createdAt": "now"})
        recalculate_rating(db.get("forwarders", fid))

    # -- CATALOGS (100) + IMAGES + VARIANTS --
    for i in range(1, 101):
        cid = f"CAT-{i:03d}"
        # Ambil produk yang benar-benar dirujuk catalog agar title/description
        # konsisten dengan productId (sebelumnya masing-masing mengundi produk
        # berbeda → judul "Kopi Instant Premium" dengan deskripsi "sirup gula merah").
        product_id = _pick(product_ids, n())
        product_name = (db.get("products", product_id) or {}).get("name", product_id)
        # Status dipilih dari indeks iterasi (bukan counter `n()`) agar sebaran
        # Draft/Published/Needs Review selalu sehat. Counter `n()` yang dipakai
        # berulang modulo 3 pernah membuat SEMUA katalog "Draft" begitu urutan
        # pemanggilan bergeser, sehingga portal pembeli jadi kosong.
        catalog_status = ["Draft", "Published", "Needs Review"][i % 3]
        db.insert("catalogs", {"id": cid, "productId": product_id,
            "projectId": _pick(proj_ids, n()),
            "title": f"{product_name} - Export",
            "status": catalog_status,
            "targetMarket": _pick(ALL_REGIONS, n()),
            "moq": f"{n()%5000+100} {_pick(['kg','pcs','unit'], n())}",
            "leadTime": f"{n()%45+7} days",
            "priceRange": f"FOB USD {n()%100+10}-{n()%200+50}",
            "incoterms": _pick_n(INCOTERMS, n()%3+1, n()),
            "readiness": n()%100,
            "description": f"High-quality {product_name.lower()}.",
            "highlights": _pick_n(["Premium quality","Direct from producer","Export ready"], n()%2+1, n()),
            "images": n()%10, "variants": [], "updatedAt": "now"})
        db.insert("catalog_images", {"id": f"IMG-{i:03d}", "catalogId": cid,
            "imageUrl": f"https://picsum.photos/seed/cat{i:03d}/400/400",
            "altText": f"Image {i}", "sortOrder": 0, "isPrimary": True,
            "createdAt": "now", "updatedAt": "now"})
        vtid = f"VT-{i:03d}"
        db.insert("catalog_variant_types", {"id": vtid, "catalogId": cid,
            "typeCode": _pick(["size","color","weight"], n()),
            "typeName": _pick(["Ukuran","Warna","Berat"], n()),
            "sortOrder": 0, "createdAt": "now", "updatedAt": "now"})
        db.insert("catalog_variant_options", {"id": f"VO-{i:03d}-01",
            "variantTypeId": vtid,
            "optionName": _pick(["Premium","Standard","Kecil","Besar"], n()),
            "sortOrder": 0, "isAvailable": True, "createdAt": "now", "updatedAt": "now"})

    # -- COSTING (100) --
    for i in range(1, 101):
        cogs = n()%50000+5000
        mv = n()%30+10
        db.insert("costing", {"id": f"CST-{i:03d}",
            "projectId": _pick(proj_ids, n()),
            "productId": _pick(product_ids, n()),
            "title": f"Costing {_pick(PRODUCTS, n())}",
            "destination": _pick(REGIONS[_pick(ALL_REGIONS, n())], n()),
            "incoterm": _pick(INCOTERMS, n()), "currency": "USD",
            "status": "Ready", "margin": mv, "exchangeRate": 15800,
            "exwPrice": round(cogs/15800, 2),
            "fobPrice": round(cogs/15800*(1+mv/100), 2),
            "cifPrice": round(cogs/15800*(1+mv/100)*1.12, 2),
            "cogs_per_unit_idr": cogs,
            "updatedAt": "now"})

    # -- EXPORT ANALYSES (100) + REGULATION RECS --
    for i in range(1, 101):
        aid = f"ANL-{i:03d}"
        # Analisis harus konsisten dengan produk yang dirujuk: nama produk, HS
        # code, dan ringkasan diambil dari `productId` yang sama. Sebelumnya
        # masing-masing diundi terpisah → judul, ringkasan, dan HS saling tidak
        # berhubungan (mis. "Keranjang Bambu" dengan "Market analysis for Teh...").
        analysis_product_id = _pick(product_ids, n())
        analysis_product = db.get("products", analysis_product_id) or {}
        analysis_product_name = analysis_product.get("name") or analysis_product_id
        db.insert("export_analyses", {"id": aid,
            "productId": analysis_product_id,
            "productName": analysis_product_name,
            "destination": _pick(REGIONS[_pick(ALL_REGIONS, n())], n()),
            "status": _pick(["Ready","In Progress","Needs Review"], n()),
            "hsCode": analysis_product.get("hs") or _pick(HS_POOL, n())[0],
            "confidence": n()%100, "score": n()%100,
            "marketDemand": _pick(["High","Medium","Low"], n()),
            "duties": f"{n()%30}%",
            "restrictions": _pick_n(["Labeling rules","Import quota"], n()%2, n()),
            "recommendations": _pick_n(["COO","Health Cert","Lab Report"], n()%3+1, n()),
            "summary": f"Market analysis for {analysis_product_name}.",
            "updatedAt": "now"})
        db.insert("regulation_recommendations", {"id": f"REG-{i:03d}",
            "analysisId": aid,
            "language": _pick(["id","en"], n()),
            "country": _pick(REGIONS[_pick(ALL_REGIONS, n())], n()),
            "sections": [{"title":"HS Code","content":"Classification done.","status":"completed"}],
            "fromCache": False})

    # -- MARKETS (100) --
    for i in range(1, 101):
        db.insert("markets", {"id": f"MKT-{i:03d}",
            "productId": _pick(product_ids, n()),
            "projectId": _pick(proj_ids, n()),
            "country": _pick(REGIONS[_pick(ALL_REGIONS, n())], n()),
            "marketScore": n()%100,
            "complianceComplexity": _pick(["Low","Medium","High"], n()),
            "entryStrategy": _pick(["Direct export","Partner distributor","E-commerce"], n()),
            "status": _pick(["Analyzed","Pending"], n()),
            "updatedAt": "now"})

    # -- RFQ, QUOTATIONS, ORDERS, PAYMENTS (100 each) --
    for i in range(1, 101):
        rfq_id = f"RFQ-{i:03d}"
        db.insert("rfqs", {"id": rfq_id, "projectId": _pick(proj_ids, n()),
            "productId": _pick(product_ids, n()),
            "buyerName": _pick(BUYER_COMPANIES, n()),
            "destination": _pick(REGIONS[_pick(ALL_REGIONS, n())], n()),
            "quantity": f"{n()%10000+100} kg",
            "incoterm": _pick(INCOTERMS, n()),
            "status": _pick(["Open","Quoted","Shortlisted","Closed"], n()),
            "deadline": f"2026-{n()%12+1:02d}-{n()%28+1:02d}",
            "matchScore": n()%100, "matches": [], "updatedAt": "now"})
        quot_id = f"Q-{i:03d}"
        db.insert("quotations", {"id": quot_id, "rfqId": rfq_id,
            "projectId": _pick(proj_ids, n()),
            "supplier": _pick(EXPORT_COMPANIES, n()),
            "buyer": _pick(BUYER_COMPANIES, n()),
            "incoterm": _pick(INCOTERMS, n()),
            "value": n()%50000+5000,
            "currency": _pick(["USD","EUR","JPY","SGD"], n()),
            "status": _pick(["In Review","Revision Needed","Accepted","Draft"], n()),
            "validUntil": f"2026-{n()%12+1:02d}-{n()%28+1:02d}",
            "margin": n()%30+5, "updatedAt": "now"})
        # Order line konsisten: total = unitPrice * quantity, dan `value` order
        # mengikuti total baris. Sebelumnya `unitPrice` tak ada sehingga halaman
        # detail order menampilkan "RpNaN per unit".
        line_qty = n() % 1000 + 1
        unit_price = round(n() % 95 + 5 + (n() % 100) / 100, 2)
        order_value = round(unit_price * line_qty, 2)
        order_line = {
            "product": _pick(PRODUCTS, n()),
            "quantity": f"{line_qty} kg",
            "unitPrice": unit_price,
            "total": order_value,
        }
        db.insert("orders", {"id": f"ORD-{i:03d}", "quotationId": quot_id,
            "projectId": _pick(proj_ids, n()),
            "buyer": _pick(BUYER_COMPANIES, n()),
            "supplier": _pick(EXPORT_COMPANIES, n()),
            "status": _pick(["Draft","Confirmed","Document Prep","In Shipment","Delivered"], n()),
            "incoterm": _pick(INCOTERMS, n()),
            "value": order_value, "currency": "USD",
            "paymentTerms": _pick(["Net 30","LC at sight","T/T advance","Net 60"], n()),
            "deliveryWindow": f"{n()%28+1}-{n()%28+1} Aug 2026",
            "readiness": n()%100,
            "lines": [order_line],
            "updatedAt": "now"})
        # `paid` tidak boleh melebihi `amount` — kalau tidak, piutang jadi negatif
        # (mis. "Tertunggak -Rp 1") dan progres terbayar > 100%.
        paid = round(order_value * (n() % 101) / 100, 2)
        db.insert("payments", {"id": f"PAY-{i:03d}", "orderId": f"ORD-{i:03d}",
            "buyer": _pick(BUYER_COMPANIES, n()),
            "status": _pick(["Pending","Received","Overdue"], n()),
            "currency": "USD", "amount": order_value,
            "paid": paid, "dueDate": f"2026-{n()%12+1:02d}-{n()%28+1:02d}",
            "method": _pick(["T/T","LC","DP"], n()), "risk": _pick(RISKS, n()),
            "remindersSent": n()%3, "updatedAt": "now"})

    # -- COMPLIANCE, DOCUMENTS, SHIPMENTS, TASKS, SUPPLIERS (100 each) --
    for i in range(1, 101):
        eid = _pick(proj_ids, n())
        db.insert("compliance_requirements", {"id": f"REQ-{i:03d}",
            "projectId": eid, "productId": _pick(product_ids, n()),
            "title": _pick(["Labeling regulation","Certificate required","Packaging standard","Import permit"], n()),
            "category": _pick(["Labeling","Certificate","Packaging","Documentation"], n()),
            "severity": _pick(["Critical","Major","Minor"], n()),
            "status": _pick(["Open","Evidence Uploaded","Verified"], n()),
            "owner": _pick(user_ids, n()),
            "due": f"2026-{n()%12+1:02d}-{n()%28+1:02d}",
            # `confidence` dipakai UI (daftar & detail). Tanpa ini halaman
            # menampilkan "KEYAKINAN AI %" (nilai kosong).
            "confidence": n()%60+40,
            # `requiredEvidence`/`currentEvidence` dirender di kartu
            # "Bukti yang Diperlukan"; tanpa ini bagian tersebut kosong.
            "requiredEvidence": _pick([
                "Certificate of origin + lab report",
                "Signed label artwork and importer approval",
                "Phytosanitary certificate",
                "Halal certificate and packaging spec sheet",
                "Health certificate and packing list",
            ], n()),
            "currentEvidence": _pick([
                "Draft uploaded, awaiting review",
                "Evidence pending from supplier",
                "Verified by compliance team",
                "In progress — lab test booked",
            ], n()),
            "source": _pick(["Regulation","Buyer requirement","Internal policy"], n()),
            "updatedAt": "now"})
        db.insert("documents", {"id": f"DOC-{i:03d}", "projectId": eid,
            "type": _pick(["Commercial Invoice","Packing List","Certificate of Origin","Bill of Lading","Insurance Cert"], n()),
            "status": _pick(["Draft","Ready","Approved","Sent"], n()),
            "version": f"v{n()%5+1}.0", "owner": _pick(user_ids, n()),
            "validationScore": n()%100,
            "fields": {"inv_no": f"INV-{i:04d}", "date": "2026-08-15"},
            "updatedAt": "now"})
        db.insert("shipments", {"id": f"SHP-{i:03d}", "projectId": eid,
            "forwarder": _pick(FORWARDER_COMPANIES, n()),
            "mode": _pick(["Ocean","Air","Multimodal"], n()),
            "route": f"{_pick(CITIES, n())} -> {_pick(ALL_REGIONS, n())}",
            "status": _pick(["Booked","In Transit","Customs Hold","Delivered"], n()),
            "eta": f"2026-{n()%12+1:02d}-{n()%28+1:02d}",
            "progress": n()%100, "container": f"CONT-{i:04d}",
            "bookingNo": f"BK-{i:04d}",
            "milestones": [{"label":"Booked","status":"Done"}],
            "updatedAt": "now"})
        db.insert("tasks", {"id": f"TSK-{i:03d}",
            "title": f"Task {i}: {_pick(['Review docs','Check compliance','Update costing','Contact buyer'], n())}",
            "module": _pick(["Compliance","Documents","Shipments","Payments"], n()),
            "projectId": eid, "owner": _pick(user_ids, n()),
            "priority": _pick(["High","Medium","Low"], n()),
            "status": _pick(["Open","In Progress","Done","Blocked"], n()),
            "due": f"2026-{n()%12+1:02d}-{n()%28+1:02d}",
            "updatedAt": "now"})
        db.insert("suppliers", {"id": f"SUP-{i:03d}",
            "name": _pick(EXPORT_COMPANIES, n()),
            "location": _pick(CITIES, n()),
            "category": _pick(CATEGORIES, n()),
            "status": _pick(["Verified","Pending"], n()),
            "capabilityScore": n()%100, "capacity": f"{n()%1000+100} ton/month",
            "leadTime": f"{n()%30+5} days",
            "qualityScore": n()%100, "complianceScore": n()%100,
            "contact": f"supplier{i}@example.com",
            "certificates": _pick_n(CERTIFICATES, n()%3, n()),
            "updatedAt": "now"})

    # -- TEAM, NOTIFICATIONS, INTEGRATIONS, TEMPLATES, AUTOMATIONS, KNOWLEDGE, CALENDAR, FILES, MESSAGES, REPORTS (100 each) --
    for i in range(1, 101):
        db.insert("team_members", {"id": f"USRM-{i:03d}",
            "name": _pick(EXPORT_COMPANIES, n()),
            "role": _pick(["Operations","Finance","Compliance","Logistics","Sales"], n()),
            "status": _pick(["Active","Invited"], n()),
            "email": f"team{i:03d}@mauekspor.example",
            "lastActive": f"2026-08-{n()%20+1:02d}",
            "permissions": _pick_n(["read","write"], n()%2+1, n()),
            "workload": n()%100, "updatedAt": "now"})
        db.insert("notifications", {"id": f"NTF-{i:04d}",
            "title": f"Notification {i}", "description": f"Desc {i}.",
            "module": _pick(["Compliance","Documents","Payments","Shipments","Buyers"], n()),
            "severity": _pick(["Info","Warning","Critical"], n()),
            "status": _pick(["Unread","Read","Archived"], n()),
            "time": f"{n()%24}:{n()%60:02d}",
            "href": f"/{_pick(['compliance','documents','payments','shipments'], n())}/{i}",
            "createdAt": "now"})
        db.insert("integrations", {"id": f"INT-{i:03d}",
            "name": f"Integration {i}",
            "category": _pick(["Forwarder API","Payment Gateway","Customs Portal","E-commerce Platform"], n()),
            "status": _pick(["Active","Disconnected"], n()),
            "description": f"Integration for {_pick(['shipping','payment','customs','inventory'], n())}.",
            "lastSync": f"2026-08-{n()%20+1:02d}",
            "scopes": _pick_n(["read_orders","write_shipments","read_inventory"], n()%2+1, n())})
        db.insert("templates", {"id": f"TPL-{i:03d}",
            "title": f"Template {i}: {_pick(['Commercial Invoice','Packing List','Quotation','COO','Proforma'], n())}",
            "category": _pick(["Document","Email","Report"], n()),
            "status": _pick(["Active","Draft"], n()),
            "description": f"Template #{i}.",
            "usedCount": n()%500, "updatedAt": "now"})
        db.insert("automations", {"id": f"AUT-{i:03d}",
            "name": f"Auto {i}: {_pick(['Label Check','Doc Approval','Payment Reminder','Shipment Tracker'], n())}",
            "trigger": _pick(["Status Change","Schedule","Webhook"], n()),
            "action": _pick(["Send Notification","Update Status","Generate Document"], n()),
            "status": _pick(["Active","Paused"], n()),
            "module": _pick(["Compliance","Documents","Payments","Shipments"], n()),
            "runs": n()%1000, "lastRun": "now", "updatedAt": "now"})
        db.insert("knowledge_articles", {"id": f"KB-{i:03d}",
            "title": f"Knowledge: {_pick(['Export Documentation Guide','HS Code Guide','Incoterms','Payment Methods'], n())}",
            "category": _pick(["Guide","FAQ","Regulation"], n()),
            "status": _pick(["Published","Draft"], n()),
            "readTime": f"{n()%20+2} min",
            "summary": f"Guide about {_pick(['export','compliance','logistics','payments'], n())}.",
            "steps": _pick_n(["Step 1: Prepare","Step 2: Check","Step 3: Submit"], n()%3+1, n()),
            "updatedAt": "now"})
        # Agenda kalender: `type` & `status` wajib memakai kosakata yang dikenal
        # UI (Compliance/Payment/Shipment/Buyer/Supplier dan
        # Scheduled/Due Soon/Blocked/Done). Sebelumnya bulk seed memakai
        # Task/Meeting/Deadline + Upcoming/Done sehingga filter tipe di halaman
        # kalender tidak pernah cocok dan label status tampil mentah.
        # Tanggal disebar di sekitar Agustus 2026 (jangkar data demo) agar
        # kalender bulanan terisi; jam berada pada rentang kerja 08:00-17:30.
        cal_month = 8 + (i % 3) - 1  # Juli, Agustus, September 2026
        cal_month = max(1, min(12, cal_month))
        cal_day = (i * 3) % 28 + 1
        cal_type = ["Compliance", "Payment", "Shipment", "Buyer", "Supplier"][i % 5]
        cal_status = ["Scheduled", "Scheduled", "Due Soon", "Done", "Blocked"][i % 5]
        cal_title = {
            "Compliance": f"Compliance review {i:03d}",
            "Payment": f"Payment follow-up {i:03d}",
            "Shipment": f"Shipment booking {i:03d}",
            "Buyer": f"Buyer meeting {i:03d}",
            "Supplier": f"Supplier evidence audit {i:03d}",
        }[cal_type]
        db.insert("calendar_events", {"id": f"CAL-{i:03d}",
            "title": cal_title,
            "date": f"2026-{cal_month:02d}-{cal_day:02d}",
            "time": f"{n()%10+8:02d}:{(n()%2)*30:02d}",
            "type": cal_type,
            "status": cal_status,
            "projectId": _pick(proj_ids, n()),
            "owner": _pick(user_ids, n()),
            "description": _pick([
                "Koordinasi lintas tim sebelum tenggat.",
                "Tindak lanjut dengan pihak terkait.",
                "Verifikasi bukti dan dokumen pendukung.",
                "Perbarui status dan kirim pembaruan ke pemangku kepentingan.",
            ], n()),
            "updatedAt": "now"})
        db.insert("files", {"id": f"FIL-{i:03d}", "name": f"file_{i:03d}.pdf",
            "type": _pick(["Document","Image","Certificate","Report"], n()),
            "status": "Active", "projectId": _pick(proj_ids, n()),
            "owner": _pick(user_ids, n()), "size": n()%5000+100,
            "updatedAt": "now"})
        db.insert("messages", {"id": f"MSG-{i:03d}",
            "subject": f"Msg {i}: {_pick(['Quotation review','Document request','Shipment update'], n())}",
            "party": _pick(BUYER_COMPANIES, n()),
            "channel": _pick(["Email","WhatsApp","Portal"], n()),
            "status": _pick(["New","Read","Replied","Resolved"], n()),
            "time": f"2026-08-{n()%20+1:02d}",
            "linkedTo": _pick(proj_ids, n()),
            "participants": _pick_n(user_ids, 2, n())})
        db.insert("reports", {"id": f"RPT-{i:03d}",
            "title": f"Report {i}: {_pick(['Monthly Summary','Compliance Status','Pipeline Analysis','Payment Recon'], n())}",
            "type": _pick(["Summary","Analysis","Performance"], n()),
            "status": _pick(["Ready","Generating","Scheduled"], n()),
            "period": f"2026-{n()%12+1:02d}",
            "owner": _pick(user_ids, n()),
            "updatedAt": "now"})

    # -- BILLING, SUPPORT, API KEYS (100 each) --
    for i in range(1, 101):
        db.insert("billing_records", {"id": f"BIL-{i:03d}",
            "plan": _pick(["Free","Starter","Professional","Enterprise"], n()),
            "status": _pick(["Active","Past Due"], n()),
            "amount": n()%1000+99, "currency": "USD",
            "period": f"2026-{n()%12+1:02d}",
            "dueDate": f"2026-{n()%12+1:02d}-{n()%28+1:02d}",
            "updatedAt": "now"})
        db.insert("support_tickets", {"id": f"SUPPORT-{i:03d}",
            "subject": f"Ticket {i}: {_pick(['Login issue','API error','Feature request','Bug report'], n())}",
            "category": _pick(["Technical","Billing","Feature","Account"], n()),
            "status": _pick(["Open","In Progress","Resolved","Closed"], n()),
            "priority": _pick(["Low","Medium","High","Critical"], n()),
            "createdAt": "now", "owner": _pick(user_ids, n())})
        db.insert("api_keys", {"id": f"KEY-{i:03d}",
            "name": f"API Key {i}: {_pick(['Production','Dev','Testing'], n())}",
            "prefix": f"mk_{i:03d}_",
            "scopes": _pick_n(["read:products","write:orders","read:shipments"], n()%2+1, n()),
            "status": _pick(["Active","Revoked"], n()),
            "createdAt": "now", "lastUsed": f"2026-08-{n()%20+1:02d}",
            "owner": _pick(user_ids, n())})

    # -- EDUCATIONAL MODULES + ARTICLES (100 each) --
    for i in range(1, 101):
        mid = f"EDU-{i:03d}"
        db.insert("educational_modules", {"id": mid,
            "title": f"Module {i}: {_pick(['Export Fundamentals','HS Classification','Documentation','International Payments','Shipping & Logistics'], n())}",
            "level": _pick(["Beginner","Intermediate","Advanced"], n()),
            "status": _pick(["Published","Draft"], n()),
            "lessons": n()%10+3, "completion": n()%100,
            "summary": f"Module about {_pick(['export','documentation','compliance','logistics'], n())}.",
            "orderIndex": i, "createdAt": "now", "updatedAt": "now"})
        db.insert("educational_articles", {"id": f"ART-{i:03d}", "moduleId": mid,
            "title": f"Article {i}: {_pick(['Getting Started','Step by Step Guide','Tips & Tricks','Case Study','Best Practices'], n())}",
            "status": _pick(["Published","Draft"], n()),
            "level": _pick(["Beginner","Intermediate","Advanced"], n()),
            "readMinutes": n()%20+2,
            "tags": _pick_n(["export","documentation","compliance","shipping"], n()%3+1, n()),
            "summary": f"Article about {_pick(['export docs','HS code','payments','shipping'], n())}.",
            "body": f"# Article {i}\n\nContent for educational article {i}.",
            "orderIndex": i, "createdAt": "now", "updatedAt": "now"})

    # -- CHAT SESSIONS (100) --
    for i in range(1, 101):
        db.insert("chat_sessions", {"id": f"CHS-{i+100:03d}",
            "title": f"Chat {i}: {_pick(['Export guidance','Compliance question','Pricing inquiry','Market research'], n())}",
            "messages": [{"role":"user","text":f"How to export to {_pick(ALL_REGIONS, n())}?"},
                        {"role":"ai","text":"Based on your workspace data, here are the steps..."}],
            "messageCount": 2, "createdAt": "now", "updatedAt": "now"})

    # -- MARKET INTELLIGENCE (100) --
    for i in range(1, 101):
        region = _pick(ALL_REGIONS, n())
        db.insert("market_intelligence", {"id": f"MI-{i:03d}",
            "productId": _pick(product_ids, n()),
            "recommendedCountries": [{"country":cc,"code":cc,"score":n()%40+60,
                "reason":f"Strong demand.","market_size":f"US${n()%500+100}M",
                "competition_level":_pick(["Low","Medium","High"], n())}
                for cc in REGIONS[region][:3]],
            "countriesToAvoid": [],
            "marketTrends": ["Growing demand","Digital adoption"],
            "competitiveLandscape": "Moderate competition.",
            "growthOpportunities": ["New markets","Product expansion"],
            "risksAndChallenges": ["Regulation","Logistics"],
            "overallRecommendation": f"Focus on {region}.",
            "generatedAt": "now"})

    # -- PRICING RESULTS (100) --
    for i in range(1, 101):
        cogs = n()%100000+10000
        mv = n()%25+10
        exr = 15800
        db.insert("pricing_results", {"id": f"PRC-{i:03d}",
            "productId": _pick(product_ids, n()),
            "cogsPerUnitIdr": cogs, "targetMarginPercent": mv,
            "targetCountryCode": _pick(["JP","US","DE","SG","KR"], n()),
            "exchangeRateUsed": exr,
            "exwPrice": round(cogs/exr, 2),
            "fobPrice": round(cogs/exr*(1+mv/100), 2),
            "cifPrice": round(cogs/exr*(1+mv/100)*1.12, 2),
            "generatedAt": "now"})

    # -- HS CODES (pool komoditas desa) --
    from app.seed_village_commodities import village_flags
    for i, (code, desc) in enumerate(HS_POOL[:100], 1):
        db.insert("hs_codes", {"id": f"HS-{i:03d}", "hs_code": code,
            "description": desc, "section": _pick(["I","II","III","IV","V","VI","VII","VIII","IX","X"], n()),
            "level": len(code), "parent": code[:-2] if len(code)>2 else "TOTAL",
            **village_flags(code), "createdAt": "now"})

    # -- REGULATIONS (100) --
    demo_cc = ["JP","SG","DE","US","KR","NL","AU","GB","MY","TH"]
    for i in range(1, 101):
        cc = demo_cc[(i-1)%len(demo_cc)]
        db.insert("regulations", {"id": f"REG-{i+200:03d}", "countryCode": cc,
            "ruleCategory": _pick(["Labeling","Ingredient","Packaging","Documentation","Certificate"], n()),
            "forbiddenKeywords": _pick_n(["BPA","phthalates","GMO"], n()%2+1, n()),
            "requiredSpecs": _pick_n(["Nutrition facts","Country of origin","Expiry date"], n()%2+1, n()),
            "descriptionRule": f"Regulation for {cc}.", "createdAt": "now", "updatedAt": "now"})

    # -- BUYER PROFILES (100) — 1:1 dengan user role Buyer (U-166..U-180) + ekspansi --
    buyer_users = [f"U-{100 + i:03d}" for i in range(1, 101) if roles[i-1] == "Buyer"] or [f"U-{100 + i:03d}" for i in range(1, 101)]
    for i in range(1, 101):
        owner = buyer_users[(i-1) % len(buyer_users)]
        db.insert("buyer_profiles", {"id": f"BYP-{i+100:03d}", "userId": owner,
            "company_name": _pick(BUYER_COMPANIES, n()),
            "companyName": _pick(BUYER_COMPANIES, n()+1),
            "company_description": f"{_pick(BUYER_COMPANIES, n())} is an importer focused on {_pick(CATEGORIES, n()).lower()}.",
            "companyDescription": f"{_pick(BUYER_COMPANIES, n())} is an importer.",
            "contact_info": {"email": f"buyer{i:03d}@example.com", "phone": f"+{n()%100+1}-{n()%9000000+1000000}"},
            "contactInfo": {"email": f"buyer{i:03d}@example.com", "phone": f"+{n()%100+1}-{n()%9000000+1000000}"},
            "preferred_product_categories": _pick_n(CATEGORIES, n()%3+1, n()),
            "preferredProductCategories": _pick_n(CATEGORIES, n()%3+1, n()),
            "source_countries": _pick_n(REGIONS[_pick(ALL_REGIONS, n())], n()%2+1, n()),
            "sourceCountries": _pick_n(REGIONS[_pick(ALL_REGIONS, n())], n()%2+1, n()),
            "business_type": _pick(["Importer","Distributor","Wholesaler","Retailer"], n()),
            "businessType": _pick(["Importer","Distributor","Wholesaler","Retailer"], n()+1),
            "annual_import_volume": _pick(["US$1-5M","US$5-20M","US$20-100M","US$100M+"], n()),
            "annualImportVolume": _pick(["US$1-5M","US$5-20M","US$20-100M","US$100M+"], n()+1),
            "createdAt": "now", "updatedAt": "now"})

    # -- FORWARDER PROFILES (100) — 1:1 dengan user role Forwarder (U-181..U-190) --
    fwd_users = [f"U-{100 + i:03d}" for i in range(1, 101) if roles[i-1] == "Forwarder"] or [f"U-{100 + i:03d}" for i in range(1, 101)]
    for i in range(1, 101):
        owner = fwd_users[(i-1) % len(fwd_users)]
        db.insert("forwarder_profiles", {"id": f"FWP-{i+100:03d}", "userId": owner,
            "company_name": _pick(FORWARDER_COMPANIES, n()),
            "companyName": _pick(FORWARDER_COMPANIES, n()+1),
            "contact_info": {"email": f"fwd{i:03d}@example.com", "phone": f"+{n()%100+1}-{n()%9000000+1000000}"},
            "contactInfo": {"email": f"fwd{i:03d}@example.com", "phone": f"+{n()%100+1}-{n()%9000000+1000000}"},
            "specialization_routes": _pick_n(["ID-JP","ID-SG","ID-DE","ID-US","ID-KR"], n()%3+1, n()),
            "specializationRoutes": _pick_n(["ID-JP","ID-SG","ID-DE","ID-US","ID-KR"], n()%3+1, n()),
            "service_types": _pick_n(["Ocean Freight","Air Freight","Customs Brokerage","Warehousing","Trucking"], n()%3+1, n()),
            "serviceTypes": _pick_n(["Ocean Freight","Air Freight","Customs Brokerage","Warehousing","Trucking"], n()%3+1, n()),
            "averageRating": round(n()%50/10, 1), "totalReviews": n()%50,
            "createdAt": "now", "updatedAt": "now"})

    # -- SETTINGS, EXCHANGE RATES --

    # -- FULL MASTER DATA: 250 negara + 6940 HS codes --
    if db.loaded_records("countries") < 100:
        from app.data import world_countries
        for i, c in enumerate(world_countries.WORLD_COUNTRIES, 1):
            db.insert("countries", {
                "id": f"CTY-{i:03d}",
                "country_code": c.get("country_code", ""),
                "country_name": c.get("country_name", ""),
                "region": c.get("region", ""),
                "createdAt": "2026-07-01",
            })

    # HS codes: jika hanya 100 dari pool (belum dataset penuh), muat dari CSV
    # HANYA chapter komoditas desa (01-24 pertanian/perikanan/perkebunan,
    # 46 kerajinan anyaman rotan, 68-70 kriya) — bukan seluruh 6.941 kode.
    if db.loaded_records("hs_codes") < 1000:
        from app.seed_village_commodities import seed_village_hs_codes
        seed_village_hs_codes()
    db.insert("settings", {"id":"SET-ORG-001", "companyName":"MauEkspor Demo",
        "country":"Indonesia", "entityType":"PT",
        "nib":"1234567890123", "taxId":"01.234.567.8",
        "currency":"IDR", "language":"id",
        "notifications":{"email":True,"inApp":True},
        "security":{"twoFactor":False,"sessionTimeout":60},
        "updatedAt":"now"})
    db.insert("exchange_rates", {"id":"FX-001","rate":15800,"source":"seed","updatedAt":"now"})

    # -- AUDIT EVENTS (100) --
    modules_list = ["products","projects","buyers","forwarders","catalogs","export-analysis","orders","shipments","payments","documents","compliance","tasks","messages","notifications","billing","support","educational","markets","rfqs","quotations","costing","suppliers","team","calendar","files","reports","automations","integrations","templates","knowledge"]
    for i in range(1, 101):
        mod = _pick(modules_list, n())
        db.insert("audit_events", {"id": f"AUD-{i:04d}", "time":"now",
            "actor":"System Seed", "action":f"INSERT {mod}",
            "module": mod, "entity":f"/api/v1/{mod}/{i}",
            "severity":"Info", "detail":"HTTP 200"})

    print(f"✅ Seeded 100 records across 50+ tables")
