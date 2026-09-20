"""FastAPI backend for the Model & Market Risk Intelligence Platform.

Run locally:
    uvicorn app.main:app --reload
Docs:
    http://127.0.0.1:8000/docs
"""
from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Query, status

from . import db
from .models import Briefing, BriefingCreate, ComparisonRow, Facets


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    yield


app = FastAPI(
    title="Model & Market Risk Intelligence API",
    version="0.2.0",
    description=(
        "Plain-language briefings on Australian and global model-risk and "
        "market-risk guidance. Informational and educational only; not "
        "regulatory or legal advice."
    ),
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/briefings", response_model=Briefing, status_code=status.HTTP_201_CREATED)
def create_briefing(payload: BriefingCreate) -> Briefing:
    data = payload.model_dump()
    data["source_url"] = str(payload.source_url)
    with db.connect() as conn:
        try:
            new_id = db.insert_briefing(conn, data)
        except sqlite3.IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A briefing with this title and source_url already exists.",
            ) from exc
        return Briefing(**db.get_briefing(conn, new_id))


@app.get("/briefings", response_model=list[Briefing])
def list_briefings(
    topic: Optional[list[str]] = Query(
        default=None, description="Repeat to require several tags, e.g. ?topic=model risk&topic=AI"
    ),
    jurisdiction: Optional[str] = None,
    document_type: Optional[str] = None,
    status_filter: Optional[Literal["draft", "published"]] = Query(default=None, alias="status"),
    q: Optional[str] = Query(default=None, min_length=2, description="Free-text search"),
) -> list[Briefing]:
    with db.connect() as conn:
        rows = db.list_briefings(
            conn,
            topics=topic,
            jurisdiction=jurisdiction,
            document_type=document_type,
            status=status_filter,
            q=q,
        )
    return [Briefing(**r) for r in rows]


@app.get("/briefings/{briefing_id}", response_model=Briefing)
def get_briefing(briefing_id: int) -> Briefing:
    with db.connect() as conn:
        row = db.get_briefing(conn, briefing_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Briefing not found")
    return Briefing(**row)


@app.get("/facets", response_model=Facets)
def facets(
    status_filter: Optional[Literal["draft", "published"]] = Query(default=None, alias="status"),
) -> Facets:
    with db.connect() as conn:
        return Facets(**db.facet_values(conn, status=status_filter))


@app.get("/comparison", response_model=list[ComparisonRow])
def comparison(
    reviewed_only: bool = Query(
        default=False, description="Only cells with a last_reviewed_by_you date"
    ),
) -> list[ComparisonRow]:
    """Model risk framework comparison: one row per (framework, dimension) cell."""
    with db.connect() as conn:
        rows = db.list_comparison(conn, reviewed_only=reviewed_only)
    return [ComparisonRow(**r) for r in rows]


@app.get("/pending-review")
def pending_review(review_status: str = "new") -> list[dict]:
    """Items found by the ingestion job that still need a human summary."""
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT * FROM pending_review WHERE review_status = ? ORDER BY detected_date DESC",
            (review_status,),
        ).fetchall()
    return [dict(r) for r in rows]
