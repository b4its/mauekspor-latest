"""Role-based access control: role -> modules allowed to mutate."""

ROLES = {
    "Admin", "Exporter", "Buyer", "Forwarder", "CustomsBroker", "Finance",
    "KepalaDesa",  # role desa untuk menu sederhana (produk, kepatuhan, dokumen)
}

# Modules only an Admin may even read.
ADMIN_ONLY_MODULES = {"users", "audit", "api-keys", "settings", "admin"}

# Modules yang butuh login untuk DIBACA (data komersial/privasi tinggi).
# Sebelumnya semua read terbuka untuk anonim (kebocoran email/telepon buyer,
# nominal pembayaran, isi pesan). Halaman terkait semuanya AppShell-guarded.
# Read publik yang tetap dibuka: /auth/me, /countries, /hs-codes, /search,
# /catalogs/public, /health.
AUTH_REQUIRED_READ_MODULES = {
    "products",
    "trade-projects",
    "business-profiles",
    "export-analysis",
    "compliance",
    "buyers",
    "buyer-requests",
    "suppliers",
    "forwarders",
    "catalogs",
    "costing",
    "markets",
    "rfqs",
    "rfq",
    "quotations",
    "orders",
    "documents",
    "shipments",
    "payments",
    "tasks",
    "team",
    "notifications",
    "automations",
    "integrations",
    "templates",
    "knowledge",
    "educational",
    "calendar",
    "files",
    "reports",
    "analytics",
    "messages",
    "chat",
    "billing",
    "support",
    "villages",
}

# Modules each role may mutate (writes). Reads stay open unless in ADMIN_ONLY_MODULES.
MUTATE_MODULES: dict[str, set[str] | str] = {
    "Admin": "*",
    "Exporter": {
        "business-profiles",
        "products",
        "export-analysis",
        "trade-projects",
        "buyers",
        "buyer-requests",
        "markets",
        "forwarders",
        "catalogs",
        "costing",
        "rfqs",
        "quotations",
        "orders",
        "compliance",
        "documents",
        "shipments",
        "payments",
        "tasks",
        "team",
        "notifications",
        "analytics",
        "integrations",
        "templates",
        "automations",
        "knowledge",
        "educational",
        "calendar",
        "chat",
        "files",
        "reports",
        "billing",
        "support",
        "suppliers",
        "messages",
        "villages",
        # "settings" sengaja TIDAK disertakan — settings read/write khusus Admin
    },
    "Forwarder": {
        "shipments",
        "messages",
        "notifications",
        "analytics",
    },
    "CustomsBroker": {
        "shipments",
        "compliance",
        "documents",
        "payments",
        "messages",
        "analytics",
    },
    "Finance": {
        "payments",
        "billing",
        "orders",
        "quotations",
        "messages",
        "analytics",
    },
    "Buyer": {
        "buyer-requests",
        "quotations",
        "orders",
        "chat",
        "messages",
        "notifications",
        "analytics",
    },
    "KepalaDesa": {
        "products",
        "compliance",
        "documents",
        "messages",
        "notifications",
        "analytics",
        "villages",
    },
}


# Modul "dibagikan" yang boleh dibaca oleh SEMUA peran yang login (kolaborasi &
# informasi umum): notifikasi, pesan, dukungan, analitik, laporan, pengetahuan,
# edukasi, chat, kalender, berkas, dasbor. TIDAK termasuk data komersial/privasi
# seperti buyers, suppliers, costing, payments, team, dll.
SHARED_READ_MODULES = {
    "notifications",
    "messages",
    "support",
    "analytics",
    "reports",
    "knowledge",
    "educational",
    "chat",
    "calendar",
    "files",
}

# Modul komersial/sensitif yang boleh DIBACA per peran (selaras dengan UI/roleAccess.ts).
# Modul di luar daftar ini (dan bukan SHARED_READ_MODULES) → ditolak untuk peran tsb.
ROLE_READ_MODULES: dict[str, set[str]] = {
    "Exporter": {
        "business-profiles", "trade-projects", "products", "villages", "export-analysis",
        "compliance", "markets", "catalogs", "buyers", "buyer-requests", "suppliers",
        "forwarders", "rfqs", "quotations", "costing", "orders", "payments", "tasks",
        "team", "integrations", "templates", "automations", "billing",
    },
    "Buyer": {
        # Halaman /buyers/portal ditangani lewat ROLE_READ_PATH_ALLOW,
        # sehingga modul "buyers" (CRM lengkap) tetap TIDAK boleh dibaca Buyer.
        "buyer-requests", "quotations", "orders", "products", "catalogs",
    },
    "Forwarder": {
        "shipments", "documents", "catalogs", "trade-projects", "forwarders",
    },
    "CustomsBroker": {
        "shipments", "documents", "compliance", "payments", "trade-projects",
    },
    "Finance": {
        "payments", "billing", "orders", "quotations", "costing",
    },
    "KepalaDesa": {
        "products", "compliance", "documents", "villages",
    },
}


def can_mutate_module(role: str, module: str) -> bool:
    allowed = MUTATE_MODULES.get(role, set())
    return allowed == "*" or module in allowed


def can_read_module(role: str, module: str) -> bool:
    if module in ADMIN_ONLY_MODULES:
        return role == "Admin"
    if not role:
        return module not in AUTH_REQUIRED_READ_MODULES  # anonim hanya modul publik
    if role == "Admin":
        return True
    if module in SHARED_READ_MODULES:
        return True
    if module in AUTH_REQUIRED_READ_MODULES:
        return module in ROLE_READ_MODULES.get(role, set())
    return True


# Path spesifik yang boleh DIBACA per peran walau modulnya dibatasi umum.
# Kasus utama: /buyers/portal (portal publik buyer) berbagi modul "buyers"
# dengan CRM buyer lengkap yang sensitif — jadi perlu pengecualian path.
ROLE_READ_PATH_ALLOW: dict[str, tuple[str, ...]] = {
    # Portal publik buyer + profil milik buyer sendiri (self-service).
    "Buyer": ("/api/v1/buyers/portal", "/api/v1/buyers/profile"),
    "Exporter": ("/api/v1/buyers/portal",),
}


def can_read_path(role: str, path: str) -> bool:
    """Cek izin baca berbasis path (menangani pengecualian seperti /buyers/portal)."""
    clean = path.split("?", 1)[0]
    if role == "Admin":
        return True
    for prefix in ROLE_READ_PATH_ALLOW.get(role, ()):
        if clean == prefix or clean.startswith(prefix + "/"):
            return True
    return can_read_module(role, _module_of_path(clean))


def _module_of_path(path: str) -> str:
    parts = path.strip("/").split("/")
    return parts[2] if len(parts) > 2 else ""