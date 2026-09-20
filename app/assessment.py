"""Phase 3: model risk governance maturity self-assessment.

Pure scoring logic, no Streamlit and no database, so it can be unit tested
and reused by the API later. Questions, weights, bands and the answer scale
live in data/assessment_questions.json.

Scoring
-------
Each question is answered 0 to 3 and carries a weight. The result is the
weighted score as a percentage of the maximum, mapped to a band:

    Foundational  under 40
    Developing    40 to under 65
    Established   65 to under 85
    Advanced      85 and above

Separately, any answer of 0 or 1 in a critical category (model definition
and inventory, independent validation) raises a critical-gap flag. The flag
sits next to the band and never changes it: a high total should not hide a
missing inventory or no independent validation.

Informational and educational only, not regulatory or legal advice.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = ROOT / "data" / "assessment_questions.json"

MIN_ANSWER = 0
MAX_ANSWER = 3
WEAK_ANSWERS = (0, 1)

BAND_NOTES = {
    "Foundational": (
        "The building blocks are mostly missing. Start with a written model "
        "definition, one inventory and a named owner."
    ),
    "Developing": (
        "The pieces exist but are uneven. Tier the inventory by risk and make "
        "validation independent of model development."
    ),
    "Established": (
        "The framework works. Tighten monitoring thresholds, issue closure and "
        "coverage of AI and vendor models."
    ),
    "Advanced": (
        "Mature practice. Keep it honest with outcomes analysis, challenge on "
        "assumptions, and evidence a supervisor could follow."
    ),
}


@dataclass(frozen=True)
class Question:
    id: str
    category: str
    question_text: str
    weight: int
    framework_refs: tuple[str, ...]


@dataclass(frozen=True)
class Questionnaire:
    questions: tuple[Question, ...]
    categories: Mapping[str, str]
    critical_categories: frozenset[str]
    bands: tuple[tuple[str, float], ...]  # (name, min_percent), ascending
    answer_scale: tuple[tuple[int, str], ...]

    def by_id(self, question_id: str) -> Question:
        for q in self.questions:
            if q.id == question_id:
                return q
        raise KeyError(question_id)

    @property
    def max_weighted_score(self) -> int:
        return sum(q.weight for q in self.questions) * MAX_ANSWER


@dataclass(frozen=True)
class CategoryResult:
    category: str
    label: str
    percent: float
    is_critical: bool
    weak_question_ids: tuple[str, ...] = ()
    frameworks: tuple[str, ...] = ()


@dataclass(frozen=True)
class Result:
    percent: float
    band: str
    band_note: str
    weighted_score: int
    max_weighted_score: int
    critical_gaps: tuple[CategoryResult, ...] = ()
    categories: tuple[CategoryResult, ...] = field(default=())

    @property
    def has_critical_gap(self) -> bool:
        return bool(self.critical_gaps)


def _load(path: Path) -> Questionnaire:
    raw: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    questions = tuple(
        Question(
            id=q["id"],
            category=q["category"],
            question_text=q["question_text"],
            weight=int(q["weight"]),
            framework_refs=tuple(q["framework_refs"]),
        )
        for q in raw["questions"]
    )
    bands = tuple(
        (b["name"], float(b["min_percent"]))
        for b in sorted(raw["bands"], key=lambda b: b["min_percent"])
    )
    return Questionnaire(
        questions=questions,
        categories=dict(raw["categories"]),
        critical_categories=frozenset(raw["critical_categories"]),
        bands=bands,
        answer_scale=tuple((int(a["score"]), a["label"]) for a in raw["answer_scale"]),
    )


@lru_cache(maxsize=4)
def load_questionnaire(path: Path | str = QUESTIONS_FILE) -> Questionnaire:
    return _load(Path(path))


def band_for(percent: float, bands: Iterable[tuple[str, float]]) -> str:
    """Half-open intervals: a band starts at its min_percent and runs to the next."""
    name = ""
    for band_name, minimum in sorted(bands, key=lambda b: b[1]):
        if percent >= minimum:
            name = band_name
    return name


def score(
    answers: Mapping[str, int], questionnaire: Questionnaire | None = None
) -> Result:
    """Score a full set of answers. Every question must be answered 0 to 3."""
    q = questionnaire or load_questionnaire()
    missing = [item.id for item in q.questions if item.id not in answers]
    if missing:
        raise ValueError(f"missing answers for: {', '.join(missing)}")
    unknown = set(answers) - {item.id for item in q.questions}
    if unknown:
        raise ValueError(f"unknown question id(s): {', '.join(sorted(unknown))}")
    for qid, value in answers.items():
        if isinstance(value, bool) or not isinstance(value, int) or not MIN_ANSWER <= value <= MAX_ANSWER:
            raise ValueError(
                f"answer for {qid} must be an integer {MIN_ANSWER} to {MAX_ANSWER}, got {value!r}"
            )

    weighted = sum(q.by_id(qid).weight * value for qid, value in answers.items())
    maximum = q.max_weighted_score
    percent = round(100 * weighted / maximum, 1) if maximum else 0.0
    band = band_for(percent, q.bands)

    categories: list[CategoryResult] = []
    for key, label in q.categories.items():
        items = [item for item in q.questions if item.category == key]
        if not items:
            continue
        cat_max = sum(item.weight for item in items) * MAX_ANSWER
        cat_score = sum(item.weight * answers[item.id] for item in items)
        weak = tuple(item.id for item in items if answers[item.id] in WEAK_ANSWERS)
        frameworks = tuple(
            sorted({ref for item in items if item.id in weak for ref in item.framework_refs})
        )
        categories.append(
            CategoryResult(
                category=key,
                label=label,
                percent=round(100 * cat_score / cat_max, 1) if cat_max else 0.0,
                is_critical=key in q.critical_categories,
                weak_question_ids=weak,
                frameworks=frameworks,
            )
        )

    critical = tuple(c for c in categories if c.is_critical and c.weak_question_ids)
    return Result(
        percent=percent,
        band=band,
        band_note=BAND_NOTES.get(band, ""),
        weighted_score=weighted,
        max_weighted_score=maximum,
        critical_gaps=critical,
        categories=tuple(categories),
    )
