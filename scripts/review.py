"""Mark content reviewed, so publishing is one command instead of hand-editing JSON.

The JSON seed files are the source of truth; the database is rebuilt from
them. Nothing here reads a regulator's website: it records that you have
read the source yourself and sets `last_reviewed_by_you` to the date.

    python -m scripts.review list
    python -m scripts.review publish --briefing "APS 116"
    python -m scripts.review publish --briefing all --date 2026-09-20
    python -m scripts.review publish --comparison "SR 26-2"
    python -m scripts.review publish --comparison all
    python -m scripts.review unpublish --briefing "APS 116"

`publish` sets last_reviewed_by_you (and, for briefings, status
"published"). `unpublish` clears both. Add --no-seed to edit the JSON
without reloading the database.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.seed import COMPARISON_FILE, SEED_FILE, reset_and_seed  # noqa: E402

ALL = "all"


def _matches(text: str, needle: str) -> bool:
    return needle == ALL or needle.lower() in text.lower()


def _load(path: Path) -> list[dict[str, Any]]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _save(path: Path, records: list[dict[str, Any]]) -> None:
    Path(path).write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def mark_briefings(
    records: list[dict[str, Any]], match: str, when: date | None, *, publish: bool = True
) -> list[str]:
    """Set or clear review date and status on every briefing whose title matches."""
    touched: list[str] = []
    for record in records:
        if not _matches(record.get("title", ""), match):
            continue
        record["last_reviewed_by_you"] = when.isoformat() if publish and when else None
        record["status"] = "published" if publish else "draft"
        touched.append(record["title"])
    return touched


def mark_comparison(
    records: list[dict[str, Any]], match: str, when: date | None, *, publish: bool = True
) -> list[str]:
    """Set or clear the review date on every comparison cell whose framework matches."""
    touched: list[str] = []
    for record in records:
        if not _matches(record.get("framework", ""), match):
            continue
        record["last_reviewed_by_you"] = when.isoformat() if publish and when else None
        touched.append(f"{record['framework']} / {record['dimension']}")
    return touched


def status_lines(
    briefings: Iterable[dict[str, Any]], cells: Iterable[dict[str, Any]]
) -> list[str]:
    lines = ["Briefings:"]
    for b in briefings:
        mark = "published" if b.get("status") == "published" else "draft    "
        lines.append(f"  [{mark}] {b.get('last_reviewed_by_you') or '  not reviewed'}  {b['title']}")
    cells = list(cells)
    reviewed = sum(1 for c in cells if c.get("last_reviewed_by_you"))
    lines.append(f"Comparison cells: {reviewed} of {len(cells)} reviewed")
    for framework in dict.fromkeys(c["framework"] for c in cells):
        rows = [c for c in cells if c["framework"] == framework]
        done = sum(1 for c in rows if c.get("last_reviewed_by_you"))
        lines.append(f"  {framework}: {done} of {len(rows)}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="show what is reviewed and what is not")
    for name in ("publish", "unpublish"):
        p = sub.add_parser(name, help=f"{name} briefings or comparison cells")
        p.add_argument("--briefing", help='title substring, or "all"')
        p.add_argument("--comparison", help='framework name, or "all"')
        p.add_argument(
            "--date", type=date.fromisoformat, default=date.today(),
            help="review date, YYYY-MM-DD (default: today)",
        )
        p.add_argument("--no-seed", action="store_true", help="edit the JSON only")

    args = parser.parse_args(argv)
    briefings, cells = _load(SEED_FILE), _load(COMPARISON_FILE)

    if args.command == "list":
        print("\n".join(status_lines(briefings, cells)))
        return 0

    if not args.briefing and not args.comparison:
        parser.error("give --briefing and/or --comparison")

    publish = args.command == "publish"
    touched: list[str] = []
    if args.briefing:
        names = mark_briefings(briefings, args.briefing, args.date, publish=publish)
        if names:
            _save(SEED_FILE, briefings)
        touched += names
    if args.comparison:
        names = mark_comparison(cells, args.comparison, args.date, publish=publish)
        if names:
            _save(COMPARISON_FILE, cells)
        touched += names

    if not touched:
        print("Nothing matched. Run `python -m scripts.review list` to see the names.")
        return 1

    verb = "Published" if publish else "Returned to draft"
    print(f"{verb} {len(touched)} item(s):")
    for name in touched:
        print(f"  {name}")
    if not args.no_seed:
        reset_and_seed()
        print("Database rebuilt from the seed files (ingestion queue untouched).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
