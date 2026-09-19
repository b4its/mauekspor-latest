"""Role-based access control: role -> modules allowed to mutate."""

ROLES = {
    "Admin", "Exporter", "Buyer", "Forwarder", "CustomsBroker", "Finance",
    "KepalaDesa",  # role desa untuk menu sederhana (produk, kepatuhan, dokumen)
}

# Modules only an Admin may even read.
ADMIN_ONLY_MODULES = {"users", "audit", "api-keys", "settings", "admin"}

# Modules each role may mutate (writes). Reads stay open unless in ADMIN_ONLY_MODULES.
MUTATE_MODULES: dict[str, set[str] | str] = {
    "Admin": "*",
    "Exporter": {
        "business-profile",
        "products",
        "export-analysis",
        "trade-projects",
        "buyers",
        "buyer-requests",
        "markets",
        "forwarders",
        "catalogs",
        "costing",
        "rfq",
        "quotations",
        "orders",
        "compliance",
        "documents",
        "shipments",
        "payments",
        "tasks",
        "team",
        "notifications",
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
    },
    "CustomsBroker": {
        "shipments",
        "compliance",
        "documents",
        "payments",
        "messages",
    },
    "Finance": {
        "payments",
        "billing",
        "orders",
        "quotations",
        "messages",
    },
    "Buyer": {
        "buyer-requests",
        "quotations",
        "orders",
        "chat",
        "messages",
    },
    "KepalaDesa": {
        "products",
        "compliance",
        "documents",
        "messages",
        "notifications",
    },
}


def can_mutate_module(role: str, module: str) -> bool:
    allowed = MUTATE_MODULES.get(role, set())
    return allowed == "*" or module in allowed


def can_read_module(role: str, module: str) -> bool:
    if module not in ADMIN_ONLY_MODULES:
        return True
    return role == "Admin"