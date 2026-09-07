from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import torch

from alphainvest.modules.ai.application.sentiment_inference_service import (
    SentimentInferenceService,
)
from alphainvest.modules.ai.domain.sentiment_enums import (
    SentimentClass,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_predicts_positive_sentiment(
) -> None:
    version_id = uuid4()
    model_id = uuid4()

    tokenizer = MagicMock(
        return_value={
            "input_ids": torch.tensor(
                [
                    [
                        101,
                        200,
                        102,
                    ]
                ],
                dtype=torch.long,
            ),
            "attention_mask": (
                torch.tensor(
                    [
                        [
                            1,
                            1,
                            1,
                        ]
                    ],
                    dtype=torch.long,
                )
            ),
        }
    )

    classifier = MagicMock(
        return_value=SimpleNamespace(
            logits=torch.tensor(
                [
                    [
                        0.2,
                        0.5,
                        2.0,
                    ]
                ],
                dtype=torch.float32,
            )
        )
    )

    runtime_service = SimpleNamespace(
        load_version=AsyncMock(
            return_value=SimpleNamespace(
                version_id=version_id,
                model_id=model_id,
                version="0.1.0",
                tokenizer=tokenizer,
                classifier=classifier,
            )
        )
    )

    service = SentimentInferenceService(
        runtime_service=runtime_service,
    )

    result = await service.predict(
        version_id=version_id,
        text=(
            "The company reported "
            "strong earnings growth."
        ),
    )

    assert (
        result.classification
        == SentimentClass.POSITIVE
    )

    assert result.version_id == version_id
    assert result.model_id == model_id

    assert (
        result.confidence
        == result.probabilities.positive
    )

    assert (
        result.probabilities.total
        > Decimal("0.999")
    )

    assert (
        result.probabilities.total
        < Decimal("1.001")
    )

    tokenizer.assert_called_once()

    classifier.assert_called_once()


@pytest.mark.asyncio
async def test_rejects_empty_text(
) -> None:
    runtime_service = SimpleNamespace(
        load_version=AsyncMock()
    )

    service = SentimentInferenceService(
        runtime_service=runtime_service,
    )

    with pytest.raises(
        ValueError,
        match="no puede estar vacío",
    ):
        await service.predict(
            version_id=uuid4(),
            text="   ",
        )

    runtime_service.load_version.assert_not_awaited()


@pytest.mark.asyncio
async def test_rejects_invalid_logit_shape(
) -> None:
    tokenizer = MagicMock(
        return_value={
            "input_ids": torch.tensor(
                [
                    [
                        101,
                        102,
                    ]
                ],
                dtype=torch.long,
            )
        }
    )

    classifier = MagicMock(
        return_value=SimpleNamespace(
            logits=torch.tensor(
                [
                    [
                        0.5,
                        0.5,
                    ]
                ],
                dtype=torch.float32,
            )
        )
    )

    runtime_service = SimpleNamespace(
        load_version=AsyncMock(
            return_value=SimpleNamespace(
                version_id=uuid4(),
                model_id=uuid4(),
                version="0.1.0",
                tokenizer=tokenizer,
                classifier=classifier,
            )
        )
    )

    service = SentimentInferenceService(
        runtime_service=runtime_service,
    )

    with pytest.raises(
        ValueError,
        match="tres probabilidades",
    ):
        await service.predict(
            version_id=uuid4(),
            text="Financial news text",
        )