from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from alphainvest.infrastructure.database.session import get_db_session
from alphainvest.modules.auth.presentation.dependencies import (
    AuthContext,
    current_context,
)
from alphainvest.modules.profile.application.service import (
    ProfileService,
)
from alphainvest.modules.profile.infrastructure.repository import (
    ProfileRepository,
)

DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


def get_profile_repository(
    session: DatabaseSession,
) -> ProfileRepository:
    return ProfileRepository(session)


ProfileRepositoryDependency = Annotated[
    ProfileRepository,
    Depends(get_profile_repository),
]


def get_profile_service(
    repository: ProfileRepositoryDependency,
) -> ProfileService:
    return ProfileService(repository)


ProfileServiceDependency = Annotated[
    ProfileService,
    Depends(get_profile_service),
]

AuthenticatedContext = Annotated[
    AuthContext,
    Depends(current_context),
]