"""Prompt 1 and 2: new briefing fields, migration, comparison seed, scoped reset."""
import json
import sqlite3

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def db_path(tmp_path, monkeypatch):
    path = tmp_path / "t.db"
    monkeypatch.setenv("RISK_INTEL_DB", str(path))
    return path


def test_new_fields_round_trip(db_path):
    from app.main import app
    from scripts.seed import seed

    seed(db_path)
    with TestClient(app) as c:
        rows = c.get("/briefings").json()
        sr = next(r for r in rows if "SR 26-2" in r["title"])
        assert sr["supersedes"] == "SR 11-7; SR 21-8"
        assert "USD 30b" in sr["applicability_note"]
        body = {
            "title": "Briefing with applicability",
            "source_name": "APRA",
            "source_url": "https://www.apra.gov.au/x",
            "jurisdiction": "Australia",
            "document_type": "speech",
            "plain_language_summary": "A summary that is long enough to validate.",
            "why_it_matters": "Because tests.",
            "who_it_applies_to": "SFIs",
            "applicability_note": "SFI ($30b+) / MSFI ($300b+) tiers from 1 July 2026",
        }
        created = c.post("/briefings", json=body).json()
        assert created["applicability_note"].startswith("SFI")
        assert created["supersedes"] is None


def test_migration_adds_columns_without_data_loss(db_path):
    # A database created by the v0.1 schema (no supersedes/applicability_note).
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE briefings (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
            source_name TEXT NOT NULL, source_url TEXT NOT NULL,
            jurisdiction TEXT NOT NULL, topic_tags TEXT NOT NULL DEFAULT '[]',
            document_type TEXT NOT NULL, publish_date TEXT, effective_date TEXT,
            plain_language_summary TEXT NOT NULL, why_it_matters TEXT NOT NULL,
            who_it_applies_to TEXT NOT NULL, last_reviewed_by_you TEXT,
            status TEXT NOT NULL DEFAULT 'draft',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE (title, source_url));
        INSERT INTO briefings (title, source_name, source_url, jurisdiction, document_type,
            plain_language_summary, why_it_matters, who_it_applies_to)
        VALUES ('Old row', 'APRA', 'https://a.example/x', 'Australia', 'speech',
            'An existing summary from before the migration.', 'Old', 'Old');
        """
    )
    conn.commit()
    conn.close()

    from app import db

    db.init_db(db_path)
    db.init_db(db_path)  # idempotent
    with db.connect(db_path) as conn:
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(briefings)")}
        assert {"supersedes", "applicability_note"} <= cols
        row = db.list_briefings(conn)[0]
        assert row["title"] == "Old row" and row["supersedes"] is None


def test_comparison_seed_and_endpoint(db_path):
    from app.main import app
    from app.models import DIMENSIONS, FRAMEWORKS
    from scripts.seed import COMPARISON_FILE, seed

    seed(db_path)
    records = json.loads(COMPARISON_FILE.read_text(encoding="utf-8"))
    assert {(r["framework"], r["dimension"]) for r in records} == {
        (f, d) for f in FRAMEWORKS for d in DIMENSIONS
    }
    with TestClient(app) as c:
        rows = c.get("/comparison").json()
        assert len(rows) == len(FRAMEWORKS) * len(DIMENSIONS)
        assert all(r["source_url"].startswith("https://") for r in rows)
        # nothing is reviewed yet, so the public view is empty
        assert c.get("/comparison", params={"reviewed_only": True}).json() == []


def test_comparison_unique_per_cell(db_path):
    from app import db
    from scripts.seed import seed, seed_comparison

    seed(db_path)
    inserted, skipped = seed_comparison(db_path)  # second load
    assert inserted == 0 and skipped == 28
    with db.connect(db_path) as conn, pytest.raises(sqlite3.IntegrityError):
        db.insert_comparison(conn, {
            "framework": "APRA", "dimension": "AI treatment",
            "position": "dup", "source_url": "https://x.example",
        })


def test_comparison_rejects_unknown_dimension():
    from pydantic import ValidationError

    from app.models import ComparisonCell

    with pytest.raises(ValidationError):
        ComparisonCell(framework="APRA", dimension="Vibes", position="x" * 5,
                       source_url="https://x.example")


def test_reset_keeps_ingestion_tables(db_path):
    from app import db
    from scripts.seed import reset_and_seed, seed

    seed(db_path)
    with db.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO pending_review (source_name, title, url) VALUES ('APRA', 'Queued', 'https://q.example')"
        )
        conn.execute("INSERT INTO source_checks VALUES ('APRA', '2026-09-14')")
        conn.execute("UPDATE briefings SET who_it_applies_to = 'HAND EDIT' WHERE id = 1")

    inserted, skipped = reset_and_seed(db_path)
    assert (inserted, skipped) == (8, 0)
    with db.connect(db_path) as conn:
        assert db.count_rows(conn, "pending_review") == 1
        assert db.count_rows(conn, "source_checks") == 1
        assert db.count_rows(conn, "framework_comparison") == 28
        # the manual DB edit is gone: briefings were rebuilt from JSON
        assert "HAND EDIT" not in {r["who_it_applies_to"] for r in db.list_briefings(conn)}
