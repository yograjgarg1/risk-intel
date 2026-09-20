"""SQLite access layer.

Uses the standard library sqlite3 module so there is nothing to install or
configure. topic_tags is stored as a JSON array in a TEXT column and queried
with SQLite's built-in json_each().
"""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "risk_intel.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS briefings (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    title                  TEXT NOT NULL,
    source_name            TEXT NOT NULL,
    source_url             TEXT NOT NULL,
    jurisdiction           TEXT NOT NULL,
    topic_tags             TEXT NOT NULL DEFAULT '[]',
    document_type          TEXT NOT NULL,
    publish_date           TEXT,
    effective_date         TEXT,
    plain_language_summary TEXT NOT NULL,
    why_it_matters         TEXT NOT NULL,
    who_it_applies_to      TEXT NOT NULL,
    supersedes             TEXT,
    applicability_note     TEXT,
    last_reviewed_by_you   TEXT,
    status                 TEXT NOT NULL DEFAULT 'draft'
                           CHECK (status IN ('draft', 'published')),
    created_at             TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (title, source_url)
);

CREATE TABLE IF NOT EXISTS pending_review (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name    TEXT NOT NULL,
    title          TEXT NOT NULL,
    url            TEXT NOT NULL UNIQUE,
    detected_date  TEXT,
    found_at       TEXT NOT NULL DEFAULT (datetime('now')),
    review_status  TEXT NOT NULL DEFAULT 'new'
                   CHECK (review_status IN ('new', 'summarised', 'dismissed'))
);

CREATE TABLE IF NOT EXISTS source_checks (
    source_name     TEXT PRIMARY KEY,
    last_checked_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS framework_comparison (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    framework            TEXT NOT NULL,
    dimension            TEXT NOT NULL,
    position             TEXT NOT NULL,
    source_url           TEXT NOT NULL,
    as_of                TEXT,
    last_reviewed_by_you TEXT,
    UNIQUE (framework, dimension)
);
"""

# Columns added after the first release. init_db() adds any that are missing
# to an existing database with ALTER TABLE, so no data is lost.
MIGRATIONS: dict[str, dict[str, str]] = {
    "briefings": {
        "supersedes": "TEXT",
        "applicability_note": "TEXT",
    },
}

# Tables rebuilt from the JSON seed files by `scripts.seed --reset`.
# pending_review and source_checks hold live ingestion results and are
# never touched by a reset.
SEEDED_TABLES = ("briefings", "framework_comparison")


def get_db_path() -> Path:
    return Path(os.environ.get("RISK_INTEL_DB", DEFAULT_DB_PATH))


@contextmanager
def connect(db_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    path = Path(db_path) if db_path else get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _migrate(conn: sqlite3.Connection) -> None:
    for table, columns in MIGRATIONS.items():
        existing = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})")}
        for name, col_type in columns.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {col_type}")


def init_db(db_path: Path | None = None) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        _migrate(conn)


def reset_seeded_tables(db_path: Path | None = None) -> None:
    """Empty the seeded tables only; ingestion tables are left intact."""
    init_db(db_path)
    with connect(db_path) as conn:
        for table in SEEDED_TABLES:
            conn.execute(f"DELETE FROM {table}")
            conn.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table,))


BRIEFING_FIELDS = (
    "title", "source_name", "source_url", "jurisdiction", "topic_tags",
    "document_type", "publish_date", "effective_date",
    "supersedes", "applicability_note", "plain_language_summary", "why_it_matters", "who_it_applies_to",
    "last_reviewed_by_you", "status",
)


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    d["topic_tags"] = json.loads(d.get("topic_tags") or "[]")
    return d


def insert_briefing(conn: sqlite3.Connection, data: dict[str, Any]) -> int:
    values = dict(data)
    values["topic_tags"] = json.dumps(values.get("topic_tags", []))
    for key in ("publish_date", "effective_date", "last_reviewed_by_you"):
        if values.get(key) is not None:
            values[key] = str(values[key])
    cols = ", ".join(BRIEFING_FIELDS)
    placeholders = ", ".join(f":{c}" for c in BRIEFING_FIELDS)
    cur = conn.execute(
        f"INSERT INTO briefings ({cols}) VALUES ({placeholders})",
        {c: values.get(c) for c in BRIEFING_FIELDS},
    )
    return int(cur.lastrowid)


def get_briefing(conn: sqlite3.Connection, briefing_id: int) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM briefings WHERE id = ?", (briefing_id,)).fetchone()
    return _row_to_dict(row) if row else None


def list_briefings(
    conn: sqlite3.Connection,
    *,
    topics: list[str] | None = None,
    jurisdiction: str | None = None,
    document_type: str | None = None,
    status: str | None = None,
    q: str | None = None,
) -> list[dict[str, Any]]:
    sql = ["SELECT * FROM briefings b WHERE 1=1"]
    params: list[Any] = []
    if jurisdiction:
        sql.append("AND lower(b.jurisdiction) = lower(?)")
        params.append(jurisdiction)
    if document_type:
        sql.append("AND lower(b.document_type) = lower(?)")
        params.append(document_type)
    if status:
        sql.append("AND b.status = ?")
        params.append(status)
    for topic in topics or []:
        # Every requested topic must be present (AND semantics).
        sql.append(
            "AND EXISTS (SELECT 1 FROM json_each(b.topic_tags) t "
            "WHERE lower(t.value) = lower(?))"
        )
        params.append(topic)
    if q:
        like = f"%{q.lower()}%"
        sql.append(
            "AND (lower(b.title) LIKE ? OR lower(b.plain_language_summary) LIKE ? "
            "OR lower(b.why_it_matters) LIKE ? OR lower(b.topic_tags) LIKE ?)"
        )
        params.extend([like] * 4)
    sql.append("ORDER BY COALESCE(b.publish_date, b.effective_date) DESC, b.id DESC")
    rows = conn.execute(" ".join(sql), params).fetchall()
    return [_row_to_dict(r) for r in rows]


COMPARISON_FIELDS = (
    "framework", "dimension", "position", "source_url", "as_of", "last_reviewed_by_you",
)


def insert_comparison(conn: sqlite3.Connection, data: dict[str, Any]) -> int:
    values = {c: data.get(c) for c in COMPARISON_FIELDS}
    for key in ("as_of", "last_reviewed_by_you"):
        if values[key] is not None:
            values[key] = str(values[key])
    cols = ", ".join(COMPARISON_FIELDS)
    placeholders = ", ".join(f":{c}" for c in COMPARISON_FIELDS)
    cur = conn.execute(
        f"INSERT INTO framework_comparison ({cols}) VALUES ({placeholders})", values
    )
    return int(cur.lastrowid)


def list_comparison(
    conn: sqlite3.Connection, *, reviewed_only: bool = False
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM framework_comparison"
    if reviewed_only:
        sql += " WHERE last_reviewed_by_you IS NOT NULL"
    return [dict(r) for r in conn.execute(sql + " ORDER BY id")]


def count_rows(conn: sqlite3.Connection, table: str) -> int:
    if table not in SEEDED_TABLES + ("pending_review", "source_checks"):
        raise ValueError(f"unknown table {table!r}")
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def facet_values(conn: sqlite3.Connection, status: str | None = None) -> dict[str, list[str]]:
    """Distinct values for the filter dropdowns in the UI, optionally for one status."""
    where, params = ("WHERE b.status = ?", (status,)) if status else ("", ())
    topics = [r[0] for r in conn.execute(
        f"SELECT DISTINCT t.value FROM briefings b, json_each(b.topic_tags) t {where} ORDER BY 1",
        params,
    )]
    jurisdictions = [r[0] for r in conn.execute(
        f"SELECT DISTINCT jurisdiction FROM briefings b {where} ORDER BY 1", params
    )]
    doc_types = [r[0] for r in conn.execute(
        f"SELECT DISTINCT document_type FROM briefings b {where} ORDER BY 1", params
    )]
    return {"topics": topics, "jurisdictions": jurisdictions, "document_types": doc_types}
