from datetime import datetime
from typing import Protocol

from alphainvest.modules.news.domain.news_document import (
    NewsDocument,
)


class NewsProvider(Protocol):
    """Contrato independiente para proveedores de noticias."""

    @property
    def source_name(self) -> str:
        """Nombre lógico del proveedor."""

    async def fetch_news(
        self,
        *,
        symbol: str,
        start_at: datetime | None,
        end_at: datetime | None,
        limit: int,
    ) -> list[NewsDocument]:
        """Obtiene y normaliza noticias financieras."""