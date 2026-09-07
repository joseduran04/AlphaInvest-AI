from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from alphainvest.core.config import Settings, get_settings
from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
    get_db_session,
)
from alphainvest.infrastructure.mongodb.client import (
    get_mongo_client,
)
from alphainvest.modules.auth.presentation.dependencies import (
    AuthContext,
    require_permission,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.news.application.service import (
    NewsService,
)
from alphainvest.modules.news.application.synchronization_service import (
    NewsSynchronizationService,
)
from alphainvest.modules.news.infrastructure.mongodb_repository import (
    MongoNewsRepository,
)
from alphainvest.modules.news.infrastructure.providers.factory import (
    create_alpha_vantage_news_provider,
)
from alphainvest.modules.news.infrastructure.storage_coordinator import (
    SqlAlchemyNewsStorageCoordinator,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)


def get_news_service(
    session: AsyncSession = Depends(
        get_db_session
    ),
    settings: Settings = Depends(
        get_settings
    ),
) -> NewsService:
    market_repository = MarketRepository(
        session
    )

    mongo_repository = MongoNewsRepository(
        client=get_mongo_client(),
        database_name=(
            settings.mongodb_database
        ),
        collection_name=(
            settings.mongodb_news_collection
        ),
    )

    return NewsService(
        market_repository=market_repository,
        mongo_repository=mongo_repository,
    )


def get_news_synchronization_service(
    session: AsyncSession = Depends(
        get_db_session
    ),
    settings: Settings = Depends(
        get_settings
    ),
) -> NewsSynchronizationService:
    market_repository = MarketRepository(
        session
    )

    operation_repository = (
        OperationRepository(
            session
        )
    )

    mongo_repository = (
        MongoNewsRepository(
            client=get_mongo_client(),
            database_name=(
                settings.mongodb_database
            ),
            collection_name=(
                settings
                .mongodb_news_collection
            ),
        )
    )

    storage = (
        SqlAlchemyNewsStorageCoordinator(
            session_factory=(
                AsyncSessionFactory
            ),
            mongo_repository=(
                mongo_repository
            ),
        )
    )

    provider = (
        create_alpha_vantage_news_provider(
            settings
        )
    )

    return NewsSynchronizationService(
        market_repository=(
            market_repository
        ),
        operation_repository=(
            operation_repository
        ),
        provider=provider,
        storage=storage,
    )


NewsServiceDependency = Annotated[
    NewsService,
    Depends(get_news_service),
]


NewsSynchronizationServiceDependency = Annotated[
    NewsSynchronizationService,
    Depends(
        get_news_synchronization_service
    ),
]


news_read_permission = require_permission(
    "noticias.leer"
)


NewsReadContext = Annotated[
    AuthContext,
    Depends(
        news_read_permission
    ),
]


news_write_permission = require_permission(
    "noticias.cargar"
)


NewsWriteContext = Annotated[
    AuthContext,
    Depends(
        news_write_permission
    ),
]