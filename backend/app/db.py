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
    # --- Modul desa (komoditas unggulan & peta potensi desa) ---
    "villages",
]

_STORE: dict[str, list[dict[str, Any]]] = {}
_LOADED = False


def _persistence_enabled() -> bool:
    return os.getenv("MAUEKSPOR_DISABLE_PERSISTENCE", "").lower() not in {"1", "true", "yes"}


# ─────────────────────────────────────────────────────────────────────────────
# Backend detection & connection
# ─────────────────────────────────────────────────────────────────────────────
def _db_url() -> str:
    return os.getenv("MAUEKSPOR_DATABASE_URL", settings.database_url)


def is_postgres() -> bool:
    return _db_url().startswith(("postgresql://", "postgres://"))


def _pg_params() -> dict:
    """Parse postgresql://user:pass@host:port/dbname into psycopg2 params."""
    from urllib.parse import unquote, urlparse

    url = _db_url()
    # Normalize scheme
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    u = urlparse(url)
    return {
        "host": u.hostname or "localhost",
        "port": u.port or 5432,
        "dbname": u.path.lstrip("/") or "mauekspor",
        "user": unquote(u.username) if u.username else "mauekspor",
        "password": unquote(u.password) if u.password else "mauekspor",
    }


def _sqlite_path() -> Path:
    url = _db_url()
    if url.startswith("sqlite:///"):
        return Path(url.removeprefix("sqlite:///"))
    return Path("mauekspor.db")


def _connect_sqlite() -> sqlite3.Connection:
    path = _sqlite_path()
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


def _connect_pg():
    """Return a psycopg2 connection for PostgreSQL backend."""
    import psycopg2

    conn = psycopg2.connect(**_pg_params())
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                table_name TEXT NOT NULL,
                id TEXT NOT NULL,
                payload JSONB NOT NULL,
                PRIMARY KEY (table_name, id)
            )
            """
        )
    conn.commit()
    return conn


def _connect():
    """Open a connection to the configured backend (SQLite or PostgreSQL)."""
    if is_postgres():
        return _connect_pg()
    return _connect_sqlite()


# ─────────────────────────────────────────────────────────────────────────────
# Persistence operations (unified over SQLite / PostgreSQL)
# ─────────────────────────────────────────────────────────────────────────────
def _load_from_disk() -> None:
    global _LOADED
    if _LOADED or not _persistence_enabled():
        _LOADED = True
        return
    with _connect() as conn:
        if is_postgres():
            import psycopg2.extras
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT table_name, payload FROM records ORDER BY table_name, id")
                rows = cur.fetchall()
        else:
            cur = conn.execute("SELECT table_name, payload FROM records ORDER BY rowid")
            rows = cur.fetchall()
    for row in rows:
        if is_postgres():
            # RealDictRow: akses via key, payload sudah berupa dict (dari JSONB)
            table = row["table_name"]
            payload = row["payload"]
        else:
            table, payload = row
        if isinstance(payload, str):
            payload = json.loads(payload)
        all(table).append(_attach(table, dict(payload)))
    _LOADED = True


def _persist_record(table: str, record: dict[str, Any]) -> None:
    if not _persistence_enabled():
        return
    payload = {k: v for k, v in record.items() if not k.startswith("__")}
    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    with _connect() as conn:
        if is_postgres():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO records (table_name, id, payload)
                    VALUES (%s, %s, %s::jsonb)
                    ON CONFLICT (table_name, id) DO UPDATE SET payload = EXCLUDED.payload
                    """,
                    (table, str(record["id"]), payload_json),
                )
        else:
            conn.execute(
                """
                INSERT INTO records (table_name, id, payload)
                VALUES (?, ?, ?)
                ON CONFLICT(table_name, id) DO UPDATE SET payload = excluded.payload
                """,
                (table, str(record["id"]), payload_json),
            )


def _delete_record(table: str, record_id: str) -> None:
    if not _persistence_enabled():
        return
    with _connect() as conn:
        if is_postgres():
            with conn.cursor() as cur:
                cur.execute("DELETE FROM records WHERE table_name = %s AND id = %s", (table, record_id))
        else:
            conn.execute("DELETE FROM records WHERE table_name = ? AND id = ?", (table, record_id))


def _clear_disk() -> None:
    if not _persistence_enabled():
        return
    with _connect() as conn:
        if is_postgres():
            with conn.cursor() as cur:
                cur.execute("DELETE FROM records")
        else:
            conn.execute("DELETE FROM records")


def _attach(table: str, record: dict[str, Any]) -> dict[str, Any]:
    record["__table"] = table
    return record


# ─────────────────────────────────────────────────────────────────────────────
# Public store API (unchanged)
# ─────────────────────────────────────────────────────────────────────────────
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
    # Cari nomor urut tertinggi dari record yang ada (hindari duplikasi setelah delete)
    max_seq = 0
    for r in all(table):
        rid = str(r.get("id", ""))
        if rid.startswith(prefix + "-"):
            try:
                seq = int(rid[len(prefix) + 1:])
                max_seq = max(max_seq, seq)
            except ValueError:
                pass
    return f"{prefix}-{max_seq + 1:03d}"


def loaded_records(table: str) -> int:
    return len(all(table))
