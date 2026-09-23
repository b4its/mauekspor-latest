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
    },
}


def can_mutate_module(role: str, module: str) -> bool:
    allowed = MUTATE_MODULES.get(role, set())
    return allowed == "*" or module in allowed


def can_read_module(role: str, module: str) -> bool:
    if module in ADMIN_ONLY_MODULES:
        return role == "Admin"
    if module in AUTH_REQUIRED_READ_MODULES:
        return bool(role)  # butuh login (peran apa pun yang valid)
    return True