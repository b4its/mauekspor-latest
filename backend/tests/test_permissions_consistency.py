"""Konsistensi RBAC: tidak ada modul yang boleh ditulis tapi tidak boleh dibaca,
dan setiap peran boleh membaca modul yang relevan (termasuk Documents/Shipments).

Bug yang dijaga di sini: `documents`/`shipments` pernah ada di MUTATE_MODULES
Exporter tetapi TIDAK di ROLE_READ_MODULES — sehingga menu tampil di UI namun
halaman/api-nya 403 ("menu tampil tapi ditolak").
"""

from app.core import permissions as p


def test_no_role_can_write_but_not_read():
    """Untuk tiap peran, setiap modul yang boleh dimutasi harus juga bisa dibaca."""
    for role, mods in p.MUTATE_MODULES.items():
        if mods == "*":
            continue
        for module in mods:
            assert p.can_read_module(role, module), (
                f"{role} boleh menulis '{module}' tetapi tidak boleh membacanya"
            )


def test_exporter_can_read_documents_and_shipments():
    assert p.can_read_module("Exporter", "documents")
    assert p.can_read_module("Exporter", "shipments")
    assert p.can_read_path("Exporter", "/api/v1/documents/")
    assert p.can_read_path("Exporter", "/api/v1/shipments/")


def test_shared_modules_readable_for_all_roles():
    """Modul kolaborasi/referensi dibaca semua peran yang login."""
    for role in ("Exporter", "Buyer", "Forwarder", "CustomsBroker", "Finance", "KepalaDesa"):
        for module in p.SHARED_READ_MODULES:
            assert p.can_read_module(role, module), f"{role} tidak bisa baca '{module}'"


def test_admin_only_modules_blocked_for_non_admin():
    for role in ("Exporter", "Buyer", "Forwarder", "CustomsBroker", "Finance", "KepalaDesa"):
        for module in p.ADMIN_ONLY_MODULES:
            assert not p.can_read_module(role, module), f"{role} seharusnya tidak baca '{module}'"


def test_public_reference_modules_open():
    """Negara & kode HS adalah referensi publik (bukan modul auth-required)."""
    for module in ("countries", "hs-codes"):
        assert module not in p.AUTH_REQUIRED_READ_MODULES
        for role in ("Exporter", "Buyer", "Forwarder", "CustomsBroker", "Finance", "KepalaDesa", "Admin"):
            assert p.can_read_module(role, module), f"{role} tidak bisa baca '{module}'"


def test_buyer_cannot_read_commercial_modules():
    """Buyer tidak boleh membaca modul komersial sensitif (batas tetap dijaga)."""
    for module in ("suppliers", "team", "costing", "payments", "buyers", "forwarders"):
        assert not p.can_read_module("Buyer", module), f"Buyer seharusnya tidak baca '{module}'"
