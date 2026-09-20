"""Pydantic request/response models."""
from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class BriefingBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=300)
    source_name: str = Field(..., min_length=2, max_length=100, examples=["APRA"])
    source_url: HttpUrl
    jurisdiction: str = Field(..., min_length=2, max_length=60, examples=["Australia"])
    topic_tags: list[str] = Field(default_factory=list, examples=[["model risk", "CPS 230"]])
    document_type: str = Field(..., min_length=2, max_length=60, examples=["prudential standard"])
    publish_date: Optional[date] = None
    effective_date: Optional[date] = None
    supersedes: Optional[str] = Field(
        default=None, max_length=300, examples=["SR 11-7; SR 21-8"],
        description="Guidance this document replaces, so superseded rules stay visible",
    )
    applicability_note: Optional[str] = Field(
        default=None, max_length=500, examples=["USD 30b+ in total assets"],
        description="Size thresholds or tier dependencies that decide who it applies to",
    )
    plain_language_summary: str = Field(..., min_length=20)
    why_it_matters: str = Field(..., min_length=10)
    who_it_applies_to: str = Field(..., min_length=3)
    last_reviewed_by_you: Optional[date] = None
    status: Literal["draft", "published"] = "draft"

    @field_validator("topic_tags")
    @classmethod
    def clean_tags(cls, tags: list[str]) -> list[str]:
        seen: list[str] = []
        for tag in tags:
            t = tag.strip()
            if t and t.lower() not in {s.lower() for s in seen}:
                seen.append(t)
        return seen


class BriefingCreate(BriefingBase):
    pass


class Briefing(BriefingBase):
    id: int
    created_at: str
    source_url: str  # stored as plain text once validated


class Facets(BaseModel):
    topics: list[str]
    jurisdictions: list[str]
    document_types: list[str]


FRAMEWORKS = ("SR 26-2", "SS1/23", "E-23", "APRA")
DIMENSIONS = (
    "Definition of a model",
    "Scope and threshold",
    "AI treatment",
    "Model inventory",
    "Validation",
    "Governance",
    "Effective date",
)


class ComparisonCell(BaseModel):
    framework: Literal["SR 26-2", "SS1/23", "E-23", "APRA"]
    dimension: str = Field(..., min_length=3, max_length=60)
    position: str = Field(..., min_length=3)
    source_url: HttpUrl
    as_of: Optional[date] = Field(default=None, description="Date the position reflects")
    last_reviewed_by_you: Optional[date] = None

    @field_validator("dimension")
    @classmethod
    def known_dimension(cls, value: str) -> str:
        if value not in DIMENSIONS:
            raise ValueError(f"dimension must be one of {DIMENSIONS}")
        return value


class ComparisonRow(BaseModel):
    framework: str
    dimension: str
    position: str
    source_url: str
    as_of: Optional[str] = None
    last_reviewed_by_you: Optional[str] = None
