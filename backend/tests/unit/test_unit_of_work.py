from unittest.mock import AsyncMock, Mock

import pytest

from alphainvest.shared.infrastructure.persistence.sqlalchemy_uow import SqlAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_unit_of_work_commits_and_closes() -> None:
    session = Mock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    factory = Mock(return_value=session)

    async with SqlAlchemyUnitOfWork(factory) as uow:
        await uow.commit()

    session.commit.assert_awaited_once()
    session.close.assert_awaited_once()
