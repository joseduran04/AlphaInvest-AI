from alphainvest.core.config import Settings
from alphainvest.modules.news.domain.provider import (
    NewsProvider,
)
from alphainvest.modules.news.infrastructure.providers.alpha_vantage import (
    AlphaVantageNewsProvider,
)


def create_alpha_vantage_news_provider(
    settings: Settings,
) -> NewsProvider:
    return AlphaVantageNewsProvider(
        api_key=settings.alpha_vantage_api_key,
        base_url=settings.alpha_vantage_base_url,
        timeout_seconds=(
            settings.alpha_vantage_timeout_seconds
        ),
    )