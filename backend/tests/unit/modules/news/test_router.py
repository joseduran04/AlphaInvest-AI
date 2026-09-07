from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from alphainvest.modules.news.presentation.dependencies import (
    get_news_service,
    news_read_permission,
)
from alphainvest.modules.news.presentation.router import (
    router,
)
from alphainvest.modules.news.presentation.schemas import (
    NewsListResponse,
)

pytestmark = pytest.mark.unit


def build_app(
    service: object,
) -> FastAPI:
    app = FastAPI()

    app.include_router(
        router
    )

    app.dependency_overrides[
        get_news_service
    ] = lambda: service

    app.dependency_overrides[
        news_read_permission
    ] = lambda: SimpleNamespace()

    return app


def test_lists_news() -> None:
    asset_id = uuid4()

    service = SimpleNamespace(
        list_asset_news=AsyncMock(
            return_value=NewsListResponse(
                asset_id=asset_id,
                items=[],
                total=0,
                limit=20,
                offset=0,
                start_at=None,
                end_at=None,
            )
        )
    )

    app = build_app(
        service
    )

    client = TestClient(
        app
    )

    response = client.get(
        f"/news/assets/{asset_id}"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["asset_id"] == str(
        asset_id
    )

    assert payload["items"] == []
    assert payload["total"] == 0


def test_rejects_invalid_query_limit(
) -> None:
    service = SimpleNamespace(
        list_asset_news=AsyncMock()
    )

    app = build_app(
        service
    )

    client = TestClient(
        app
    )

    response = client.get(
        
            f"/news/assets/{uuid4()}"
            "?limit=0"
        
    )

    assert response.status_code == 422


def test_passes_date_filters() -> None:
    asset_id = uuid4()

    service = SimpleNamespace(
        list_asset_news=AsyncMock(
            return_value=NewsListResponse(
                asset_id=asset_id,
                items=[],
                total=0,
                limit=10,
                offset=0,
                start_at=datetime(
                    2026,
                    8,
                    1,
                    tzinfo=UTC,
                ),
                end_at=datetime(
                    2026,
                    8,
                    24,
                    tzinfo=UTC,
                ),
            )
        )
    )

    app = build_app(
        service
    )

    client = TestClient(
        app
    )

    response = client.get(
        
            f"/news/assets/{asset_id}"
            "?start_at=2026-08-01T00:00:00Z"
            "&end_at=2026-08-24T00:00:00Z"
            "&limit=10"
        
    )

    assert response.status_code == 200