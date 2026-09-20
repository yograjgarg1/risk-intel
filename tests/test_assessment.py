"""Prompt 4 (Phase 3): weighted scoring, band boundaries and the critical-gap flag."""
import pytest

from app.assessment import MAX_ANSWER, Question, Questionnaire, band_for, load_questionnaire, score

QUESTIONNAIRE = load_questionnaire()
BANDS = QUESTIONNAIRE.bands


def answers_all(value: int) -> dict[str, int]:
    return {q.id: value for q in QUESTIONNAIRE.questions}


def test_question_set_is_well_formed():
    qs = QUESTIONNAIRE.questions
    assert 12 <= len(qs) <= 15
    assert len({q.id for q in qs}) == len(qs)
    assert {q.category for q in qs} == set(QUESTIONNAIRE.categories)
    assert QUESTIONNAIRE.critical_categories <= set(QUESTIONNAIRE.categories)
    assert all(q.weight >= 1 and q.framework_refs for q in qs)
    known = {"SR 26-2", "SS1/23", "E-23", "APRA"}
    assert {ref for q in qs for ref in q.framework_refs} <= known


def test_extremes():
    low = score(answers_all(0), QUESTIONNAIRE)
    assert (low.percent, low.band, low.weighted_score) == (0.0, "Foundational", 0)
    high = score(answers_all(MAX_ANSWER), QUESTIONNAIRE)
    assert (high.percent, high.band) == (100.0, "Advanced")
    assert high.weighted_score == high.max_weighted_score
    assert not high.has_critical_gap


@pytest.mark.parametrize("percent, expected", [
    (0, "Foundational"), (39.9, "Foundational"), (40, "Developing"), (64.9, "Developing"),
    (65, "Established"), (84.9, "Established"), (85, "Advanced"), (100, "Advanced"),
])
def test_band_boundaries(percent, expected):
    assert band_for(percent, BANDS) == expected


def test_weighting_favours_heavier_questions():
    light = min(QUESTIONNAIRE.questions, key=lambda q: q.weight)
    heavy = max(QUESTIONNAIRE.questions, key=lambda q: q.weight)
    assert heavy.weight > light.weight
    base = answers_all(0)
    lifted_light = score({**base, light.id: MAX_ANSWER}, QUESTIONNAIRE)
    lifted_heavy = score({**base, heavy.id: MAX_ANSWER}, QUESTIONNAIRE)
    assert lifted_heavy.percent > lifted_light.percent


def test_critical_gap_fires_on_an_otherwise_advanced_result():
    weakest = next(
        q for q in QUESTIONNAIRE.questions if q.category in QUESTIONNAIRE.critical_categories
    )
    result = score({**answers_all(MAX_ANSWER), weakest.id: 1}, QUESTIONNAIRE)
    assert result.band == "Advanced"  # the flag does not change the band
    assert result.has_critical_gap
    gap = result.critical_gaps[0]
    assert gap.category == weakest.category
    assert weakest.id in gap.weak_question_ids
    assert set(weakest.framework_refs) <= set(gap.frameworks)


def test_no_flag_for_weak_answers_outside_critical_categories():
    non_critical = next(
        q for q in QUESTIONNAIRE.questions if q.category not in QUESTIONNAIRE.critical_categories
    )
    result = score({**answers_all(MAX_ANSWER), non_critical.id: 0}, QUESTIONNAIRE)
    assert not result.has_critical_gap
    weak = [c for c in result.categories if c.weak_question_ids]
    assert [c.category for c in weak] == [non_critical.category]


def test_category_percentages():
    result = score(answers_all(2), QUESTIONNAIRE)
    assert all(c.percent == pytest.approx(66.7, abs=0.1) for c in result.categories)
    assert result.percent == pytest.approx(66.7, abs=0.1) and result.band == "Established"
    assert not result.has_critical_gap  # 2 is not a weak answer


def test_incomplete_answers_rejected():
    partial = answers_all(2)
    partial.pop("gov1")
    with pytest.raises(ValueError, match="missing answers"):
        score(partial, QUESTIONNAIRE)
    with pytest.raises(ValueError, match="missing answers"):
        score({}, QUESTIONNAIRE)


def test_unknown_question_rejected():
    with pytest.raises(ValueError, match="unknown question"):
        score({**answers_all(2), "nope": 1}, QUESTIONNAIRE)


@pytest.mark.parametrize("value", [4, -1, "3", 2.5, True, None])
def test_out_of_range_answers_rejected(value):
    with pytest.raises(ValueError, match="must be an integer"):
        score({**answers_all(2), "gov1": value}, QUESTIONNAIRE)


def test_band_note_is_present_for_every_band():
    for value in (0, 1, 2, 3):
        result = score(answers_all(value), QUESTIONNAIRE)
        assert result.band_note


def test_scoring_ignores_question_order():
    custom = Questionnaire(
        questions=(
            Question("a", "inventory", "Q a", 1, ("SR 26-2",)),
            Question("b", "validation", "Q b", 3, ("SS1/23",)),
        ),
        categories={"inventory": "Inventory", "validation": "Validation"},
        critical_categories=frozenset({"validation"}),
        bands=BANDS,
        answer_scale=QUESTIONNAIRE.answer_scale,
    )
    result = score({"b": 3, "a": 0}, custom)
    assert result.weighted_score == 9 and result.max_weighted_score == 12
    assert result.percent == 75.0 and result.band == "Established"
    # the weak answer sits in inventory, which is not critical in this custom set
    assert not result.has_critical_gap
    assert [c.category for c in result.categories if c.weak_question_ids] == ["inventory"]
