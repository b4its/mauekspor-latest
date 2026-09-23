from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from builtins import all as builtin_all

from app.core.config import settings

_TABLES = [
    "users", "products", "projects", "business_profiles", "export_analyses", "buyers",
    "buyer_requests", "forwarders", "catalogs", "costing", "markets", "rfqs",
    "quotations", "orders", "compliance_requirements", "documents", "shipments",
    "payments", "tasks", "team_members", "notifications", "integrations", "templates",
    "automations", "knowledge_articles", "educational_modules", "educational_articles",
    "calendar_events", "messages", "billing_records", "support_tickets", "api_keys",
    "files", "reports", "audit_events", "chat_conversations", "refresh_tokens",
    # --- Modul inti ExportReadyAI ---
    "countries", "hs_codes", "exchange_rates", "product_enrichments",
    "market_intelligence", "pricing_results", "forwarder_reviews",
    "catalog_images", "catalog_variant_types", "catalog_variant_options",
    "chat_sessions", "regulation_recommendations", "buyer_profiles",
    "forwarder_profiles", "educational_lessons", "regulations",
    "settings",
]

_STORE: dict[str, list[dict[str, Any]]] = {}
_LOADED = False


def _persistence_enabled() -> bool:
    return os.getenv("MAUEKSPOR_DISABLE_PERSISTENCE", "").lower() not in {"1", "true", "yes"}


def _db_path() -> Path:
    url = os.getenv("MAUEKSPOR_DATABASE_URL", settings.database_url)
    if url.startswith("sqlite:///"):
        return Path(url.removeprefix("sqlite:///"))
    return Path("mauekspor.db")


def _connect() -> sqlite3.Connection:
    path = _db_path()
    if path.parent and str(path.parent) not in {"", "."}:
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            table_name TEXT NOT NULL,
            id TEXT NOT NULL,
            payload TEXT NOT NULL,
            PRIMARY KEY (table_name, id)
        )
        """
    )
    return conn


def _load_from_disk() -> None:
    global _LOADED
    if _LOADED or not _persistence_enabled():
        _LOADED = True
        return
    with _connect() as conn:
        rows = conn.execute("SELECT table_name, payload FROM records ORDER BY rowid").fetchall()
    for table, payload in rows:
        all(table).append(_attach(table, json.loads(payload)))
    _LOADED = True


def _persist_record(table: str, record: dict[str, Any]) -> None:
    if not _persistence_enabled():
        return
    payload = {k: v for k, v in record.items() if not k.startswith("__")}
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO records (table_name, id, payload)
            VALUES (?, ?, ?)
            ON CONFLICT(table_name, id) DO UPDATE SET payload = excluded.payload
            """,
            (table, str(record["id"]), json.dumps(payload, separators=(",", ":"))),
        )


def _delete_record(table: str, record_id: str) -> None:
    if not _persistence_enabled():
        return
    with _connect() as conn:
        conn.execute("DELETE FROM records WHERE table_name = ? AND id = ?", (table, record_id))


def _clear_disk() -> None:
    if not _persistence_enabled():
        return
    with _connect() as conn:
        conn.execute("DELETE FROM records")


def _attach(table: str, record: dict[str, Any]) -> dict[str, Any]:
    record["__table"] = table
    return record


def init_store():
    for name in _TABLES:
        _STORE.setdefault(name, [])
    _load_from_disk()


def reset_store():
    global _LOADED
    _STORE.clear()
    for name in _TABLES:
        _STORE[name] = []
    _LOADED = True
    _clear_disk()


def all(table: str) -> list[dict[str, Any]]:
    if table not in _STORE:
        _STORE[table] = []
    for record in _STORE[table]:
        record.setdefault("__table", table)
    return _STORE[table]


def get(table: str, record_id: str) -> dict[str, Any] | None:
    for record in all(table):
        if record.get("id") == record_id:
            return record
    return None


def _matches(r: dict, filters: dict) -> bool:
    return _all_builtin(r.get(k) == v for k, v in filters.items())


def _all_builtin(iterable):
    return builtin_all(iterable)


def _check_all(r: dict, filters: dict) -> bool:
    return builtin_all(r.get(k) == v for k, v in filters.items())


def find(table: str, **filters: Any) -> list[dict[str, Any]]:
    return [r for r in all(table) if _check_all(r, filters)]


def get_by(table: str, **filters: Any) -> dict[str, Any] | None:
    for r in all(table):
        if _check_all(r, filters):
            return r
    return None


def insert(table: str, record: dict[str, Any]) -> dict[str, Any]:
    if "id" not in record:
        record["id"] = gen_id(table)
    _attach(table, record)
    all(table).append(record)
    _persist_record(table, record)
    return record


def save(record: dict[str, Any]) -> dict[str, Any]:
    table = record.get("__table")
    if table and record.get("id"):
        _persist_record(str(table), record)
    return record


def update(table: str, record_id: str, patch: dict[str, Any]) -> dict[str, Any] | None:
    record = get(table, record_id)
    if not record:
        return None
    record.update({k: v for k, v in patch.items() if v is not None})
    _persist_record(table, record)
    return record


def replace(table: str, record_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    for i, record in enumerate(all(table)):
        if record.get("id") == record_id:
            data["id"] = record_id
            all(table)[i] = data
            _persist_record(table, data)
            return data
    return None


def delete(table: str, record_id: str) -> bool:
    before = len(all(table))
    all(table)[:] = [r for r in all(table) if r.get("id") != record_id]
    deleted = len(all(table)) < before
    if deleted:
        _delete_record(table, record_id)
    return deleted


def gen_id(table: str, prefix: str | None = None) -> str:
    if prefix is None:
        prefix = table.rstrip("s").upper()
    seq = len(all(table)) + 1
    return f"{prefix}-{seq:03d}"


def loaded_records(table: str) -> int:
    return len(all(table))
