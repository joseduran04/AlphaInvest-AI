import asyncio
from collections import Counter

from alphainvest.core.config import (
    get_settings,
)
from alphainvest.infrastructure.mongodb.client import (
    create_mongo_client,
)
from alphainvest.modules.ai.application.sentiment_dataset_service import (
    SentimentDatasetService,
)


async def main() -> None:
    settings = get_settings()

    client = create_mongo_client(
        settings
    )

    try:
        collection = (
            client[
                settings.mongodb_database
            ][
                settings
                .mongodb_news_collection
            ]
        )

        documents = []

        async for document in (
            collection.find(
                {}
            )
        ):
            documents.append(
                document
            )

        dataset = (
            SentimentDatasetService
            .build(documents)
        )

        distribution = Counter(
            sample.label.value
            for sample in dataset.samples
        )

        print(
            "=" * 72
        )

        print(
            "ALPHAINVEST AI — "
            "SENTIMENT DATASET"
        )

        print(
            "=" * 72
        )

        print(
            "Mongo documents:",
            len(documents),
        )

        print(
            "Usable samples:",
            dataset.size,
        )

        print()

        print(
            "Class distribution:"
        )

        for label in (
            "POSITIVO",
            "NEUTRAL",
            "NEGATIVO",
        ):
            count = distribution.get(
                label,
                0,
            )

            percentage = (
                count
                / dataset.size
                * 100
                if dataset.size
                else 0
            )

            print(
                f"{label:<10} "
                f"{count:>5} "
                f"({percentage:6.2f}%)"
            )

        print(
            "=" * 72
        )

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(
        main()
    )