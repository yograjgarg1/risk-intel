"""Phase 2: check regulator publication pages for new documents.

Human-in-the-loop by design: anything new goes into the `pending_review`
table. Nothing is ever written to `briefings` automatically. You read the
source, write the summary yourself, then publish it.

Usage:
    python -m ingestion.check_sources                 # check all sources
    python -m ingestion.check_sources --dry-run       # print, don't save
    python -m ingestion.check_sources --source RBA-speeches
    python -m ingestion.check_sources --since 2026-08-01

Schedule it with cron, Windows Task Scheduler or GitHub Actions (see
.github/workflows/check_sources.yml).

Be a polite scraper: one request per source per run, a clear User-Agent,
and prefer official RSS feeds where they exist. Check each site's terms of
use and robots.txt before you deploy this on a schedule.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import db  # noqa: E402

CONTACT_ENV = "RISK_INTEL_CONTACT"
USER_AGENT_TEMPLATE = "risk-intel-research-bot/0.2 (personal research project; contact: {contact})"


def user_agent() -> str:
    """Build the User-Agent from RISK_INTEL_CONTACT so regulators can reach you."""
    contact = os.environ.get(CONTACT_ENV, "").strip()
    if not contact or "@" not in contact or contact.endswith("example.com"):
        raise RuntimeError(
            f"Set {CONTACT_ENV} to your contact email before checking live sources, "
            f"e.g. {CONTACT_ENV}=you@example.org (Windows: set {CONTACT_ENV}=...)."
        )
    return USER_AGENT_TEMPLATE.format(contact=contact)
DEFAULT_LOOKBACK_DAYS = 30

# Keep relevance filtering broad. It only decides what lands in your review
# queue; you still decide what becomes a briefing.
RISK_KEYWORDS = [
    "model", "market risk", "credit risk", "operational risk", "capital",
    "prudential", "basel", "trading book", "frtb", "cps 230", "aps 1", "aps 2",
    "cpg", "apg", "risk management", "artificial intelligence", " ai ",
    "stress test", "liquidity", "interest rate risk", "counterparty",
    "financial stability", "governance",
]


@dataclass
class FoundItem:
    source_name: str
    title: str
    url: str
    detected_date: Optional[date]


@dataclass
class Source:
    name: str
    url: str
    kind: str  # "rss" or "apra_html"
    keywords: Optional[list[str]] = field(default=None)  # None = keep everything
    title_must_contain: Optional[str] = None


SOURCES: list[Source] = [
    Source("APRA", "https://www.apra.gov.au/news-and-publications", "apra_html", RISK_KEYWORDS),
    Source("RBA-media-releases", "https://www.rba.gov.au/rss/rss-cb-media-releases.xml", "rss", RISK_KEYWORDS),
    Source("RBA-speeches", "https://www.rba.gov.au/rss/rss-cb-speeches.xml", "rss", RISK_KEYWORDS),
    Source("RBA-financial-stability-review", "https://www.rba.gov.au/rss/rss-cb-fsr.xml", "rss", None),
    # BIS does not list a BCBS-only feed on bis.org/rss, so we read the
    # all-press-releases feed and keep only Basel Committee items.
    Source("Basel Committee", "https://www.bis.org/doclist/all_pressrels.rss", "rss", None,
           title_must_contain="basel committee"),
]

DATE_RE = re.compile(
    r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\s+(\d{4})\b",
    re.IGNORECASE,
)


def parse_display_date(text: str) -> Optional[date]:
    m = DATE_RE.search(text or "")
    if not m:
        return None
    return datetime.strptime(f"{m.group(1)} {m.group(2).title()} {m.group(3)}", "%d %B %Y").date()


def parse_rss(content: bytes | str, source: Source) -> list[FoundItem]:
    feed = feedparser.parse(content)
    items: list[FoundItem] = []
    for entry in feed.entries:
        title = (entry.get("title") or "").strip()
        link = (entry.get("link") or "").strip()
        if not title or not link:
            continue
        parsed = entry.get("published_parsed") or entry.get("updated_parsed")
        detected = date(*parsed[:3]) if parsed else None
        items.append(FoundItem(source.name, title, link, detected))
    return items


def parse_apra_html(html: str, source: Source) -> list[FoundItem]:
    """Parse APRA's News and Publications listing.

    The listing shows a linked headline plus a display date such as
    "10 September 2026" for each item. Rather than depend on exact CSS
    class names (which change when sites are redesigned), we take every
    link into /news-and-publications/<slug> and look for a date in the
    nearest enclosing block. If APRA changes its layout, run with
    --dry-run and adjust this function.
    """
    soup = BeautifulSoup(html, "html.parser")
    items: list[FoundItem] = []
    seen: set[str] = set()
    for a in soup.select('a[href*="/news-and-publications/"]'):
        href = a.get("href", "")
        if href.rstrip("/").endswith("/news-and-publications") or "?" in href:
            continue  # filter/pagination links, not documents
        title = " ".join(a.get_text(" ", strip=True).split())
        if len(title) < 8:
            continue
        url = urljoin(source.url, href)
        if url in seen:
            continue
        detected = None
        node = a
        for _ in range(5):
            node = node.parent
            if node is None:
                break
            # Stop once the block holds more than one document link, or we
            # would pick up a neighbouring item's date.
            doc_links = {
                x.get("href") for x in node.select('a[href*="/news-and-publications/"]')
                if "?" not in x.get("href", "")
            }
            if len(doc_links) > 1:
                break
            detected = parse_display_date(node.get_text(" ", strip=True))
            if detected:
                break
        seen.add(url)
        items.append(FoundItem(source.name, title, url, detected))
    return items


PARSERS: dict[str, Callable[[str | bytes, Source], list[FoundItem]]] = {
    "rss": parse_rss,
    "apra_html": parse_apra_html,
}


def is_relevant(item: FoundItem, source: Source) -> bool:
    title = f" {item.title.lower()} "
    if source.title_must_contain and source.title_must_contain not in title:
        return False
    if source.keywords is None:
        return True
    return any(k in title for k in source.keywords)


def filter_new(items: list[FoundItem], since: date) -> list[FoundItem]:
    # Items without a detectable date are kept: better to review one extra
    # item than to silently miss a new standard.
    return [i for i in items if i.detected_date is None or i.detected_date >= since]


def fetch(source: Source, timeout: int = 30) -> str:
    resp = requests.get(source.url, headers={"User-Agent": user_agent()}, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def get_last_checked(conn, source_name: str) -> Optional[date]:
    row = conn.execute(
        "SELECT last_checked_at FROM source_checks WHERE source_name = ?", (source_name,)
    ).fetchone()
    return date.fromisoformat(row[0][:10]) if row else None


def save_items(conn, items: list[FoundItem]) -> int:
    added = 0
    for i in items:
        cur = conn.execute(
            "INSERT OR IGNORE INTO pending_review (source_name, title, url, detected_date) "
            "VALUES (?, ?, ?, ?)",
            (i.source_name, i.title, i.url, i.detected_date.isoformat() if i.detected_date else None),
        )
        added += cur.rowcount
    return added


def mark_checked(conn, source_name: str, when: date) -> None:
    conn.execute(
        "INSERT INTO source_checks (source_name, last_checked_at) VALUES (?, ?) "
        "ON CONFLICT(source_name) DO UPDATE SET last_checked_at = excluded.last_checked_at",
        (source_name, when.isoformat()),
    )


def run(
    sources: list[Source],
    *,
    since_override: Optional[date] = None,
    dry_run: bool = False,
    fetcher: Callable[[Source], str] = fetch,
    today: Optional[date] = None,
) -> dict[str, int]:
    today = today or date.today()
    db.init_db()
    results: dict[str, int] = {}
    with db.connect() as conn:
        for source in sources:
            last = get_last_checked(conn, source.name)
            # Overlap by one day so items published late on the last run day
            # are not missed; the UNIQUE url constraint removes duplicates.
            since = since_override or (last - timedelta(days=1) if last else today - timedelta(days=DEFAULT_LOOKBACK_DAYS))
            try:
                raw = fetcher(source)
            except Exception as exc:  # keep going if one site is down
                print(f"[{source.name}] fetch failed: {exc}")
                results[source.name] = -1
                continue
            items = [i for i in PARSERS[source.kind](raw, source) if is_relevant(i, source)]
            new_items = filter_new(items, since)
            if dry_run:
                print(f"[{source.name}] {len(new_items)} candidate(s) since {since}:")
                for i in new_items:
                    print(f"   {i.detected_date or '????-??-??'}  {i.title}\n      {i.url}")
                results[source.name] = len(new_items)
                continue
            added = save_items(conn, new_items)
            mark_checked(conn, source.name, today)
            print(f"[{source.name}] {added} new item(s) queued for review (checked since {since})")
            results[source.name] = added
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Queue new regulator publications for review")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--source", action="append", help="limit to one or more source names")
    parser.add_argument("--since", type=date.fromisoformat, help="YYYY-MM-DD; overrides last-checked date")
    args = parser.parse_args()
    chosen = [s for s in SOURCES if not args.source or s.name in args.source]
    if not chosen:
        parser.error(f"unknown source; choose from {[s.name for s in SOURCES]}")
    try:
        user_agent()
    except RuntimeError as exc:
        parser.exit(2, f"{exc}\n")
    run(chosen, since_override=args.since, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
