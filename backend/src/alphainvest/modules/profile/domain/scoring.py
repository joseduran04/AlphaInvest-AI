from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from alphainvest.modules.profile.domain.enums import RiskClassification

ZERO = Decimal("0")
ONE_HUNDRED = Decimal("100")
TWO_DECIMALS = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class ScoredAnswer:
    question_id: str
    option_value: Decimal
    weight: Decimal

    @property
    def weighted_score(self) -> Decimal:
        return self.option_value * self.weight


@dataclass(frozen=True, slots=True)
class RiskScoreResult:
    raw_score: Decimal
    minimum_score: Decimal
    maximum_score: Decimal
    normalized_score: Decimal
    classification: RiskClassification
    confidence: Decimal
    description: str


class RiskScoringService:
    """Calcula el perfil de riesgo mediante reglas deterministas."""

    MINIMUM_OPTION_VALUE = Decimal("1")
    MAXIMUM_OPTION_VALUE = Decimal("5")

    @classmethod
    def calculate(cls, answers: list[ScoredAnswer]) -> RiskScoreResult:
        if not answers:
            raise ValueError("Se requiere al menos una respuesta")

        cls._validate_answers(answers)

        raw_score = sum(
            (answer.weighted_score for answer in answers),
            start=ZERO,
        )

        minimum_score = sum(
            (
                cls.MINIMUM_OPTION_VALUE * answer.weight
                for answer in answers
            ),
            start=ZERO,
        )

        maximum_score = sum(
            (
                cls.MAXIMUM_OPTION_VALUE * answer.weight
                for answer in answers
            ),
            start=ZERO,
        )

        normalized_score = cls._normalize(
            raw_score=raw_score,
            minimum_score=minimum_score,
            maximum_score=maximum_score,
        )

        classification = cls.classify(normalized_score)

        return RiskScoreResult(
            raw_score=raw_score.quantize(
                TWO_DECIMALS,
                rounding=ROUND_HALF_UP,
            ),
            minimum_score=minimum_score.quantize(
                TWO_DECIMALS,
                rounding=ROUND_HALF_UP,
            ),
            maximum_score=maximum_score.quantize(
                TWO_DECIMALS,
                rounding=ROUND_HALF_UP,
            ),
            normalized_score=normalized_score,
            classification=classification,
            confidence=Decimal("1.00"),
            description=cls.description_for(classification),
        )

    @classmethod
    def _validate_answers(cls, answers: list[ScoredAnswer]) -> None:
        question_ids = [answer.question_id for answer in answers]

        if len(question_ids) != len(set(question_ids)):
            raise ValueError(
                "No puede existir más de una respuesta por pregunta"
            )

        for answer in answers:
            if answer.weight <= ZERO:
                raise ValueError(
                    "La ponderación debe ser mayor que cero"
                )

            if not (
                cls.MINIMUM_OPTION_VALUE
                <= answer.option_value
                <= cls.MAXIMUM_OPTION_VALUE
            ):
                raise ValueError(
                    "El valor de la opción debe estar entre 1 y 5"
                )

    @staticmethod
    def _normalize(
        *,
        raw_score: Decimal,
        minimum_score: Decimal,
        maximum_score: Decimal,
    ) -> Decimal:
        score_range = maximum_score - minimum_score

        if score_range <= ZERO:
            raise ValueError(
                "El rango de puntuación debe ser mayor que cero"
            )

        normalized = (
            (raw_score - minimum_score)
            / score_range
            * ONE_HUNDRED
        )

        normalized = max(ZERO, min(ONE_HUNDRED, normalized))

        return normalized.quantize(
            TWO_DECIMALS,
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def classify(
        normalized_score: Decimal,
    ) -> RiskClassification:
        if normalized_score < Decimal("20"):
            return RiskClassification.CONSERVATIVE

        if normalized_score < Decimal("40"):
            return RiskClassification.MODERATE_CONSERVATIVE

        if normalized_score < Decimal("60"):
            return RiskClassification.MODERATE

        if normalized_score < Decimal("80"):
            return RiskClassification.MODERATE_AGGRESSIVE

        return RiskClassification.AGGRESSIVE

    @staticmethod
    def description_for(
        classification: RiskClassification,
    ) -> str:
        descriptions = {
            RiskClassification.CONSERVATIVE: (
                "Prioriza la conservación del capital y presenta "
                "una tolerancia baja a las pérdidas."
            ),
            RiskClassification.MODERATE_CONSERVATIVE: (
                "Acepta fluctuaciones limitadas para obtener "
                "rendimientos ligeramente superiores."
            ),
            RiskClassification.MODERATE: (
                "Busca equilibrio entre crecimiento, estabilidad "
                "y tolerancia a variaciones temporales."
            ),
            RiskClassification.MODERATE_AGGRESSIVE: (
                "Acepta volatilidad relevante para buscar un mayor "
                "crecimiento de largo plazo."
            ),
            RiskClassification.AGGRESSIVE: (
                "Presenta una tolerancia alta al riesgo y acepta "
                "pérdidas importantes a cambio de mayor crecimiento."
            ),
        }

        return descriptions[classification]