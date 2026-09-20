"""Load the JSON seed files into SQLite.

Usage:
    python -m scripts.seed            # insert any rows not already present
    python -m scripts.seed --reset    # rebuild the seeded tables from JSON

Seed files:
    data/seed_briefings.json        -> briefings
    data/framework_comparison.json  -> framework_comparison

--reset empties only `briefings` and `framework_comparison` before reloading.
`pending_review` and `source_checks` hold live ingestion results and are
never touched.

Every seed briefing ships with status "draft" and last_reviewed_by_you = null.
Read the source document, edit the JSON, then set status to "published" and
fill in last_reviewed_by_you before showing it to anyone. Comparison cells
follow the same rule: a cell with last_reviewed_by_you = null is hidden on
the public site.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import db  # noqa: E402
from app.models import BriefingCreate, ComparisonCell  # noqa: E402

SEED_FILE = ROOT / "data" / "seed_briefings.json"
COMPARISON_FILE = ROOT / "data" / "framework_comparison.json"


def seed(
    db_path: Path | None = None,
    seed_file: Path = SEED_FILE,
    comparison_file: Path | None = COMPARISON_FILE,
) -> tuple[int, int]:
    """Insert seed briefings (and comparison cells). Returns briefings (inserted, skipped)."""
    db.init_db(db_path)
    records = json.loads(seed_file.read_text(encoding="utf-8"))
    inserted = skipped = 0
    with db.connect(db_path) as conn:
        for record in records:
            model = BriefingCreate(**record)  # validates every seed record
            data = model.model_dump()
            data["source_url"] = str(model.source_url)
            try:
                db.insert_briefing(conn, data)
                inserted += 1
            except sqlite3.IntegrityError:
                skipped += 1
    if comparison_file is not None and Path(comparison_file).exists():
        seed_comparison(db_path, comparison_file)
    return inserted, skipped


def seed_comparison(db_path: Path | None = None, comparison_file: Path = COMPARISON_FILE) -> tuple[int, int]:
    db.init_db(db_path)
    records = json.loads(Path(comparison_file).read_text(encoding="utf-8"))
    inserted = skipped = 0
    with db.connect(db_path) as conn:
        for record in records:
            cell = ComparisonCell(**record)
            data = cell.model_dump()
            data["source_url"] = str(cell.source_url)
            try:
                db.insert_comparison(conn, data)
                inserted += 1
            except sqlite3.IntegrityError:  # (framework, dimension) already present
                skipped += 1
    return inserted, skipped


def reset_and_seed(db_path: Path | None = None) -> tuple[int, int]:
    db.reset_seeded_tables(db_path)
    return seed(db_path)


def ensure_seeded(db_path: Path | None = None) -> bool:
    """Build the database from the seed files if it is missing or empty.

    Used by the Streamlit app on startup so a fresh deployment (where the
    .db file is git-ignored) is never empty. Returns True if it seeded.
    """
    db.init_db(db_path)
    with db.connect(db_path) as conn:
        if db.count_rows(conn, "briefings") > 0:
            return False
    seed(db_path)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--reset", action="store_true",
        help="empty briefings and framework_comparison before seeding (ingestion tables are kept)",
    )
    args = parser.parse_args()
    path = db.get_db_path()
    inserted, skipped = reset_and_seed() if args.reset else seed()
    with db.connect() as conn:
        cells = db.count_rows(conn, "framework_comparison")
        queued = db.count_rows(conn, "pending_review")
    print(
        f"Seeded {inserted} briefing(s), skipped {skipped} already present; "
        f"{cells} comparison cell(s); {queued} pending-review item(s) kept -> {path}"
    )


if __name__ == "__main__":
    main()
