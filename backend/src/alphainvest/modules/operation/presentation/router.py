from uuid import UUID

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from alphainvest.modules.operation.domain.enums import (
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)
from alphainvest.modules.operation.domain.exceptions import (
    InvalidNotificationStateTransitionError,
    NotificationNotFoundError,
    NotificationNotSentError,
)
from alphainvest.modules.operation.presentation.dependencies import (
    NotificationAdminContext,
    NotificationAdminServiceDependency,
    NotificationReadContext,
    NotificationServiceDependency,
)
from alphainvest.modules.operation.presentation.schemas import (
    AdminNotificationListResponse,
    NotificationListResponse,
    NotificationResponse,
    UnreadNotificationCountResponse,
)

router = APIRouter(
    prefix="/notifications",
    tags=["Notificaciones"],
)


@router.get(
    "",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar mis notificaciones",
    description=(
        "Consulta las notificaciones entregadas "
        "al usuario autenticado."
    ),
)
async def list_notifications(
    context: NotificationReadContext,
    service: NotificationServiceDependency,
    unread_only: bool = Query(
        default=False,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> NotificationListResponse:
    return await service.list_notifications(
        user_id=context.user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/unread-count",
    response_model=(
        UnreadNotificationCountResponse
    ),
    status_code=status.HTTP_200_OK,
    summary="Contar notificaciones no leídas",
    description=(
        "Obtiene la cantidad de notificaciones "
        "entregadas que el usuario todavía "
        "no ha leído."
    ),
)
async def count_unread_notifications(
    context: NotificationReadContext,
    service: NotificationServiceDependency,
) -> UnreadNotificationCountResponse:
    return await service.count_unread(
        user_id=context.user.id,
    )



@router.get(
    "/admin",
    response_model=AdminNotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar notificaciones administrativamente",
)
async def list_notifications_admin(
    _: NotificationAdminContext,
    service: NotificationAdminServiceDependency,
    user_id: UUID | None = Query(
        default=None,
    ),
    notification_status: NotificationStatus | None = Query(
        default=None,
        alias="status",
    ),
    notification_type: NotificationType | None = Query(
        default=None,
        alias="type",
    ),
    channel: NotificationChannel | None = Query(
        default=None,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> AdminNotificationListResponse:
    return await service.list_notifications(
        user_id=user_id,
        status=notification_status,
        notification_type=notification_type,
        channel=channel,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/admin/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar notificación administrativamente",
)
async def get_notification_admin(
    notification_id: UUID,
    _: NotificationAdminContext,
    service: NotificationAdminServiceDependency,
) -> NotificationResponse:
    try:
        return await service.get_notification(
            notification_id=notification_id
        )

    except NotificationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.patch(
    "/admin/{notification_id}/cancel",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancelar una notificación",
    description=(
        "Cancela una notificación PENDIENTE "
        "o PROGRAMADA antes de comenzar su envío."
    ),
)
async def cancel_notification_admin(
    notification_id: UUID,
    _: NotificationAdminContext,
    service: NotificationAdminServiceDependency,
) -> NotificationResponse:
    try:
        return await service.cancel_notification(
            notification_id=notification_id
        )

    except NotificationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except (
        InvalidNotificationStateTransitionError
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar una notificación",
    description=(
        "Consulta una notificación entregada "
        "perteneciente al usuario autenticado."
    ),
)
async def get_notification(
    notification_id: UUID,
    context: NotificationReadContext,
    service: NotificationServiceDependency,
) -> NotificationResponse:
    try:
        return await service.get_notification(
            notification_id=notification_id,
            user_id=context.user.id,
        )

    except NotificationNotFoundError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(error),
        ) from error

    except NotificationNotSentError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(error),
        ) from error


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Marcar notificación como leída",
    description=(
        "Marca como leída una notificación "
        "entregada perteneciente al usuario "
        "autenticado."
    ),
)
async def mark_notification_as_read(
    notification_id: UUID,
    context: NotificationReadContext,
    service: NotificationServiceDependency,
) -> NotificationResponse:
    try:
        return await service.mark_as_read(
            notification_id=notification_id,
            user_id=context.user.id,
        )

    except NotificationNotFoundError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(error),
        ) from error

    except NotificationNotSentError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(error),
        ) from error

