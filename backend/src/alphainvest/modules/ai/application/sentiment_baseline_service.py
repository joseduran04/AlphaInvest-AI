from sklearn.feature_extraction.text import (
    TfidfVectorizer,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
)
from sklearn.pipeline import Pipeline

from alphainvest.modules.ai.domain.sentiment_classification_result import (
    SentimentClassificationResult,
)

SENTIMENT_LABELS = (
    "NEGATIVO",
    "NEUTRAL",
    "POSITIVO",
)


class SentimentBaselineService:
    """Baseline NLP TF-IDF + Logistic Regression."""

    @staticmethod
    def build_pipeline() -> Pipeline:
        return Pipeline(
            steps=[
                (
                    "tfidf",
                    TfidfVectorizer(
                        lowercase=True,
                        ngram_range=(1, 2),
                        min_df=2,
                        max_df=0.95,
                        sublinear_tf=True,
                    ),
                ),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        random_state=42,
                    ),
                ),
            ]
        )

    @classmethod
    def train_and_evaluate(
        cls,
        *,
        train_texts: list[str],
        train_labels: list[str],
        evaluation_texts: list[str],
        evaluation_labels: list[str],
    ) -> tuple[
        Pipeline,
        SentimentClassificationResult,
    ]:
        pipeline = cls.build_pipeline()

        pipeline.fit(
            train_texts,
            train_labels,
        )

        predictions = pipeline.predict(
            evaluation_texts
        )

        matrix = confusion_matrix(
            evaluation_labels,
            predictions,
            labels=SENTIMENT_LABELS,
        )

        result = (
            SentimentClassificationResult(
                accuracy=float(
                    accuracy_score(
                        evaluation_labels,
                        predictions,
                    )
                ),
                balanced_accuracy=float(
                    balanced_accuracy_score(
                        evaluation_labels,
                        predictions,
                    )
                ),
                macro_f1=float(
                    f1_score(
                        evaluation_labels,
                        predictions,
                        labels=SENTIMENT_LABELS,
                        average="macro",
                        zero_division=0,
                    )
                ),
                labels=SENTIMENT_LABELS,
                confusion_matrix=tuple(
                    tuple(
                        int(value)
                        for value in row
                    )
                    for row in matrix.tolist()
                ),
            )
        )

        return pipeline, result