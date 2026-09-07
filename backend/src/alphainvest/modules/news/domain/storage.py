from typing import Protocol
from uuid import UUID

from alphainvest.modules.news.domain.news_document import (
    NewsDocument,
)
from alphainvest.modules.news.domain.news_storage import (
    NewsStorageResult,
)


class NewsAssetStorage(Protocol):
    """Puerto para persistir una noticia asociada a un activo."""

    async def store_for_asset(
        self,
        *,
        asset_id: UUID,
        document: NewsDocument,
        provider_name: str,
        language: str | None = None,
    ) -> NewsStorageResult:
        """Persiste documento y referencia relacional."""