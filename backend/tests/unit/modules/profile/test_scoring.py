from decimal import Decimal

import pytest

from alphainvest.modules.profile.domain.enums import RiskClassification
from alphainvest.modules.profile.domain.scoring import (
    RiskScoringService,
    ScoredAnswer,
)

pytestmark = pytest.mark.unit


def create_answers(
    option_value: str,
) -> list[ScoredAnswer]:
    weights = [
        "1.0",
        "1.2",
        "1.0",
        "1.1",
        "1.1",
        "1.5",
        "1.5",
        "1.2",
        "1.1",
        "1.2",
    ]

    return [
        ScoredAnswer(
            question_id=f"question-{index}",
            option_value=Decimal(option_value),
            weight=Decimal(weight),
        )
        for index, weight in enumerate(weights, start=1)
    ]


def test_minimum_answers_produce_conservative_profile() -> None:
    result = RiskScoringService.calculate(
        create_answers("1")
    )

    assert result.raw_score == Decimal("11.90")
    assert result.normalized_score == Decimal("0.00")
    assert (
        result.classification
        == RiskClassification.CONSERVATIVE
    )


def test_middle_answers_produce_moderate_profile() -> None:
    result = RiskScoringService.calculate(
        create_answers("3")
    )

    assert result.raw_score == Decimal("35.70")
    assert result.normalized_score == Decimal("50.00")
    assert (
        result.classification
        == RiskClassification.MODERATE
    )


def test_maximum_answers_produce_aggressive_profile() -> None:
    result = RiskScoringService.calculate(
        create_answers("5")
    )

    assert result.raw_score == Decimal("59.50")
    assert result.normalized_score == Decimal("100.00")
    assert (
        result.classification
        == RiskClassification.AGGRESSIVE
    )


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        ("0", RiskClassification.CONSERVATIVE),
        ("19.99", RiskClassification.CONSERVATIVE),
        (
            "20",
            RiskClassification.MODERATE_CONSERVATIVE,
        ),
        (
            "39.99",
            RiskClassification.MODERATE_CONSERVATIVE,
        ),
        ("40", RiskClassification.MODERATE),
        ("59.99", RiskClassification.MODERATE),
        (
            "60",
            RiskClassification.MODERATE_AGGRESSIVE,
        ),
        (
            "79.99",
            RiskClassification.MODERATE_AGGRESSIVE,
        ),
        ("80", RiskClassification.AGGRESSIVE),
        ("100", RiskClassification.AGGRESSIVE),
    ],
)
def test_classification_boundaries(
    score: str,
    expected: RiskClassification,
) -> None:
    assert (
        RiskScoringService.classify(Decimal(score))
        == expected
    )


def test_empty_answers_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="al menos una respuesta",
    ):
        RiskScoringService.calculate([])


def test_duplicate_questions_are_rejected() -> None:
    answers = [
        ScoredAnswer(
            question_id="same-question",
            option_value=Decimal("2"),
            weight=Decimal("1"),
        ),
        ScoredAnswer(
            question_id="same-question",
            option_value=Decimal("3"),
            weight=Decimal("1"),
        ),
    ]

    with pytest.raises(
        ValueError,
        match="más de una respuesta",
    ):
        RiskScoringService.calculate(answers)


@pytest.mark.parametrize("value", ["0", "6"])
def test_invalid_option_values_are_rejected(
    value: str,
) -> None:
    answers = [
        ScoredAnswer(
            question_id="question-1",
            option_value=Decimal(value),
            weight=Decimal("1"),
        )
    ]

    with pytest.raises(
        ValueError,
        match="entre 1 y 5",
    ):
        RiskScoringService.calculate(answers)


def test_invalid_weight_is_rejected() -> None:
    answers = [
        ScoredAnswer(
            question_id="question-1",
            option_value=Decimal("3"),
            weight=Decimal("0"),
        )
    ]

    with pytest.raises(
        ValueError,
        match="mayor que cero",
    ):
        RiskScoringService.calculate(answers)