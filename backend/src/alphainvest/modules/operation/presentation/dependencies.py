from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from alphainvest.infrastructure.database.session import (
    get_db_session,
)
from alphainvest.modules.auth.presentation.dependencies import (
    AuthContext,
    require_permission,
)
from alphainvest.modules.operation.application.notification_admin_service import (
    NotificationAdminService,
)
from alphainvest.modules.operation.application.notification_service import (
    NotificationService,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)


def get_notification_service(
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> NotificationService:
    repository = OperationRepository(
        session
    )

    return NotificationService(
        repository
    )


def get_notification_admin_service(
    session: AsyncSession = Depends(get_db_session),
) -> NotificationAdminService:
    repository = OperationRepository(session)

    return NotificationAdminService(repository)


NotificationServiceDependency = Annotated[
    NotificationService,
    Depends(
        get_notification_service
    ),
]


NotificationAdminServiceDependency = Annotated[
    NotificationAdminService,
    Depends(get_notification_admin_service),
]


notification_read_permission = (
    require_permission(
        "notificaciones.leer"
    )
)


NotificationReadContext = Annotated[
    AuthContext,
    Depends(
        notification_read_permission
    ),
]


notification_admin_permission = (
    require_permission(
        "notificaciones.administrar"
    )
)


NotificationAdminContext = Annotated[
    AuthContext,
    Depends(
        notification_admin_permission
    ),
]